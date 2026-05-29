package com.chatbot.service;

import com.azure.ai.openai.OpenAIClient;
import com.azure.ai.openai.OpenAIClientBuilder;
import com.azure.ai.openai.models.ChatCompletions;
import com.azure.ai.openai.models.ChatCompletionsOptions;
import com.azure.core.credential.AzureKeyCredential;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class AzureOpenAIService {
    
    private final OpenAIClient client;
    private final String deploymentName;
    
    @Autowired
    private DocumentService documentService;
    
    @Autowired(required = false)
    private GalileoService galileoService;
    
    public AzureOpenAIService(
            @Value("${azure.openai.endpoint}") String endpoint,
            @Value("${azure.openai.api-key}") String apiKey,
            @Value("${azure.openai.deployment-name:gpt-5-nano}") String deploymentName) {
        this.deploymentName = deploymentName;
        // Ensure endpoint ends with a slash
        String normalizedEndpoint = endpoint.endsWith("/") ? endpoint : endpoint + "/";
        this.client = new OpenAIClientBuilder()
                .endpoint(normalizedEndpoint)
                .credential(new AzureKeyCredential(apiKey))
                .buildClient();
    }
    
    public com.chatbot.dto.ChatCompletionResult getChatCompletion(String userMessage, List<String> conversationHistory, String traceId, List<String> relevantContext) {
        try {
            List<com.azure.ai.openai.models.ChatRequestMessage> messages = new ArrayList<>();
            
            // Context is already retrieved in ChatController, so we just use it here
            // Retriever span is created in ChatController, so we don't create it here
            Map<String, Object> retrieverSpan = null;
            
            String contextText = "";
            if (relevantContext != null && !relevantContext.isEmpty()) {
                contextText = "\n\nRelevant context from knowledge base:\n" + 
                    relevantContext.stream()
                        .map(ctx -> "- " + ctx)
                        .collect(Collectors.joining("\n"));
            }
            
            // Build system message with RAG context and 30-word limit
            String systemPrompt = "You are a helpful assistant. " +
                "Answer questions concisely using the provided context when available. " +
                "IMPORTANT: Keep your responses to 30 words or less. " +
                "Be direct and brief." + contextText;
            
            // Add system message
            messages.add(new com.azure.ai.openai.models.ChatRequestSystemMessage(systemPrompt));
            
            // Add conversation history (excluding the current message which is already in userMessage)
            if (conversationHistory != null && !conversationHistory.isEmpty()) {
                // The history should be in pairs: [user1, assistant1, user2, assistant2, ...]
                // But we exclude the last item if it's the current user message
                int historySize = conversationHistory.size();
                // If the last item matches the current message, exclude it
                if (historySize > 0 && conversationHistory.get(historySize - 1).equals(userMessage)) {
                    historySize--; // Exclude the last item
                }
                
                for (int i = 0; i < historySize; i += 2) {
                    if (i < historySize) {
                        messages.add(new com.azure.ai.openai.models.ChatRequestUserMessage(
                            conversationHistory.get(i)
                        ));
                    }
                    if (i + 1 < historySize) {
                        messages.add(new com.azure.ai.openai.models.ChatRequestAssistantMessage(
                            conversationHistory.get(i + 1)
                        ));
                    }
                }
            }
            
            // Add current user message
            messages.add(new com.azure.ai.openai.models.ChatRequestUserMessage(userMessage));
            
            ChatCompletionsOptions options = new ChatCompletionsOptions(messages);
            
            ChatCompletions chatCompletions = client.getChatCompletions(deploymentName, options);
            
            if (chatCompletions.getChoices() == null || chatCompletions.getChoices().isEmpty()) {
                throw new RuntimeException("No response choices returned from Azure OpenAI");
            }
            
            String response = chatCompletions.getChoices().get(0).getMessage().getContent();
            
            // Convert Azure messages to common format for Galileo logging
            List<Map<String, String>> messagesForGalileo = new ArrayList<>();
            for (com.azure.ai.openai.models.ChatRequestMessage msg : messages) {
                Map<String, String> msgMap = new HashMap<>();
                if (msg instanceof com.azure.ai.openai.models.ChatRequestSystemMessage) {
                    msgMap.put("role", "system");
                    msgMap.put("content", ((com.azure.ai.openai.models.ChatRequestSystemMessage) msg).getContent().toString());
                } else if (msg instanceof com.azure.ai.openai.models.ChatRequestUserMessage) {
                    msgMap.put("role", "user");
                    msgMap.put("content", ((com.azure.ai.openai.models.ChatRequestUserMessage) msg).getContent().toString());
                } else if (msg instanceof com.azure.ai.openai.models.ChatRequestAssistantMessage) {
                    msgMap.put("role", "assistant");
                    msgMap.put("content", ((com.azure.ai.openai.models.ChatRequestAssistantMessage) msg).getContent().toString());
                }
                messagesForGalileo.add(msgMap);
            }
            
            return new com.chatbot.dto.ChatCompletionResult(response, retrieverSpan, messagesForGalileo);
        } catch (Exception e) {
            throw new RuntimeException("Error calling Azure OpenAI: " + e.getMessage(), e);
        }
    }
}

