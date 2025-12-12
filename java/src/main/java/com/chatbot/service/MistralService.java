package com.chatbot.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class MistralService {
    
    private final String apiKey;
    private final String model;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private static final String MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions";
    
    @Autowired
    private DocumentService documentService;
    
    @Autowired(required = false)
    private com.chatbot.service.GalileoService galileoService;
    
    public MistralService(
            @Value("${mistral.api-key}") String apiKey,
            @Value("${mistral.model:mistral-medium}") String model) {
        this.apiKey = apiKey;
        this.model = model;
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
    }
    
    public com.chatbot.dto.ChatCompletionResult getChatCompletion(String userMessage, List<String> conversationHistory, String traceId, List<String> relevantContext) {
        try {
            // Build messages list
            List<Map<String, String>> messages = new ArrayList<>();
            
            // Context is already retrieved in ChatController, so we just use it here
            // Retriever span is created in ChatController, so we don't create it here
            Map<String, Object> retrieverSpan = null;
            
            String contextText = "";
            if (relevantContext != null && !relevantContext.isEmpty()) {
                contextText = "\n\nRelevant context from knowledge base:\n" + 
                    relevantContext.stream()
                        .map(ctx -> "- " + ctx)
                        .collect(java.util.stream.Collectors.joining("\n"));
            }
            
            // Build system message with RAG context and 30-word limit
            String systemPrompt = "You are a helpful assistant. " +
                "Answer questions concisely using the provided context when available. " +
                "IMPORTANT: Keep your responses to 30 words or less. " +
                "Be direct and brief." + contextText;
            
            // Add system message
            Map<String, String> systemMessage = new HashMap<>();
            systemMessage.put("role", "system");
            systemMessage.put("content", systemPrompt);
            messages.add(systemMessage);
            
            // Add conversation history
            if (conversationHistory != null && !conversationHistory.isEmpty()) {
                int historySize = conversationHistory.size();
                // If the last item matches the current message, exclude it
                if (historySize > 0 && conversationHistory.get(historySize - 1).equals(userMessage)) {
                    historySize--;
                }
                
                for (int i = 0; i < historySize; i += 2) {
                    if (i < historySize) {
                        Map<String, String> userMsg = new HashMap<>();
                        userMsg.put("role", "user");
                        userMsg.put("content", conversationHistory.get(i));
                        messages.add(userMsg);
                    }
                    if (i + 1 < historySize) {
                        Map<String, String> assistantMsg = new HashMap<>();
                        assistantMsg.put("role", "assistant");
                        assistantMsg.put("content", conversationHistory.get(i + 1));
                        messages.add(assistantMsg);
                    }
                }
            }
            
            // Add current user message
            Map<String, String> currentUserMessage = new HashMap<>();
            currentUserMessage.put("role", "user");
            currentUserMessage.put("content", userMessage);
            messages.add(currentUserMessage);
            
            // Build request body
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", model);
            requestBody.put("messages", messages);
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.setBearerAuth(apiKey);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            // Make API call
            ResponseEntity<String> response = restTemplate.exchange(
                    MISTRAL_API_URL,
                    HttpMethod.POST,
                    request,
                    String.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                JsonNode jsonNode = objectMapper.readTree(response.getBody());
                JsonNode choices = jsonNode.get("choices");
                if (choices != null && choices.isArray() && choices.size() > 0) {
                    JsonNode message = choices.get(0).get("message");
                    if (message != null) {
                        JsonNode content = message.get("content");
                        if (content != null) {
                            String responseText = content.asText();
                            return new com.chatbot.dto.ChatCompletionResult(responseText, retrieverSpan);
                        }
                    }
                }
                throw new RuntimeException("No response content in Mistral API response");
            } else {
                throw new RuntimeException("Mistral API returned status: " + response.getStatusCode());
            }
        } catch (Exception e) {
            throw new RuntimeException("Error calling Mistral API: " + e.getMessage(), e);
        }
    }
}

