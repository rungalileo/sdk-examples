package com.example.gateway;

import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;

@RestController
public class AskController {

    private static final Logger log = LoggerFactory.getLogger(AskController.class);

    private final ChatClient chatClient;
    private final RestTemplate restTemplate;
    private final String pythonServiceUrl;

    public AskController(
            ChatClient.Builder chatClientBuilder,
            RestTemplate restTemplate,
            @Value("${python-service.url}") String pythonServiceUrl) {
        this.chatClient = chatClientBuilder
                .defaultSystem("You are a routing classifier for a financial services AI system. "
                        + "Classify questions into exactly one category: FINANCIAL, TECHNICAL, or GENERAL. "
                        + "Reply with ONLY the category name, nothing else.")
                .build();
        this.restTemplate = restTemplate;
        this.pythonServiceUrl = pythonServiceUrl;
    }

    @PostMapping("/ask")
    @SuppressWarnings("unchecked")
    public ResponseEntity<Map<String, Object>> ask(@RequestBody Map<String, String> request) {
        String question = request.get("question");
        log.info("Received question: {}", question);

        Tracer tracer = GlobalOpenTelemetry.getTracer("java-gateway");

        // Wrap the full agent flow in a span with Galileo-recognized gen_ai attributes.
        // The OTel Java agent auto-instruments Spring Boot/HTTP, but these attributes
        // are needed for Galileo to render this as an "agent" span in the trace UI.
        Span agentSpan = tracer.spanBuilder("invoke_agent financial-assistant")
                .setAttribute("gen_ai.system", "spring-ai")
                .setAttribute("gen_ai.operation.name", "invoke_agent")
                .setAttribute("gen_ai.agent.name", "financial-assistant")
                .setAttribute(AttributeKey.stringKey("gen_ai.input.messages"),
                        "[{\"role\": \"user\", \"content\": " + jsonEscape(question) + "}]")
                .startSpan();

        try (Scope ignored = agentSpan.makeCurrent()) {
            // Step 1: Classify the question using Spring AI + OpenAI
            String category = classifyQuestion(tracer, question);
            log.info("Classified as: {}", category);

            // Step 2: Call Python RAG service — the OTel Java agent automatically
            // injects the W3C traceparent header, propagating the trace context.
            Map<String, String> pythonRequest = new HashMap<>();
            pythonRequest.put("question", question);
            pythonRequest.put("category", category);

            Map<String, Object> ragResponse = restTemplate.postForObject(
                    pythonServiceUrl + "/process",
                    pythonRequest,
                    Map.class);

            Map<String, Object> response = new HashMap<>();
            response.put("answer", ragResponse.get("answer"));
            response.put("category", category);
            response.put("sources", ragResponse.get("sources"));

            agentSpan.setAttribute(AttributeKey.stringKey("gen_ai.output.messages"),
                    "[{\"role\": \"assistant\", \"content\": " + jsonEscape((String) ragResponse.get("answer")) + "}]");

            return ResponseEntity.ok(response);
        } finally {
            agentSpan.end();
        }
    }

    private String classifyQuestion(Tracer tracer, String question) {
        // Manual LLM span — Spring AI doesn't yet auto-emit gen_ai.operation.name=chat,
        // so we create it ourselves for proper Galileo trace rendering.
        Span llmSpan = tracer.spanBuilder("chat classify_question")
                .setAttribute("gen_ai.system", "spring-ai")
                .setAttribute("gen_ai.operation.name", "chat")
                .setAttribute("gen_ai.request.model", "gpt-4o-mini")
                .setAttribute(AttributeKey.stringKey("gen_ai.input.messages"),
                        "[{\"role\": \"user\", \"content\": " + jsonEscape(question) + "}]")
                .startSpan();

        try (Scope ignored = llmSpan.makeCurrent()) {
            String category = chatClient.prompt()
                    .user(question)
                    .call()
                    .content()
                    .trim();

            llmSpan.setAttribute(AttributeKey.stringKey("gen_ai.output.messages"),
                    "[{\"role\": \"assistant\", \"content\": " + jsonEscape(category) + "}]");
            return category;
        } finally {
            llmSpan.end();
        }
    }

    private static String jsonEscape(String value) {
        if (value == null) return "\"\"";
        return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n") + "\"";
    }
}
