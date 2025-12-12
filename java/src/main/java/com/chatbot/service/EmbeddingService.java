package com.chatbot.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class EmbeddingService {
    
    private final String mistralApiKey;
    private final String azureEndpoint;
    private final String azureApiKey;
    private final String azureEmbeddingDeployment;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private static final String MISTRAL_EMBEDDINGS_API_URL = "https://api.mistral.ai/v1/embeddings";
    private static final String MISTRAL_EMBED_MODEL = "mistral-embed";
    private static final String AZURE_API_VERSION = "2024-02-15-preview";
    
    public EmbeddingService(
            @Value("${mistral.api-key}") String mistralApiKey,
            @Value("${azure.openai.endpoint:}") String azureEndpoint,
            @Value("${azure.openai.api-key:}") String azureApiKey,
            @Value("${azure.openai.embedding-deployment-name:text-embedding-ada-002}") String azureEmbeddingDeployment) {
        this.mistralApiKey = mistralApiKey;
        this.azureEndpoint = azureEndpoint;
        this.azureApiKey = azureApiKey;
        this.azureEmbeddingDeployment = azureEmbeddingDeployment;
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
    }
    
    public List<Float> getEmbedding(String text) {
        // Try Mistral first
        try {
            return getMistralEmbedding(text);
        } catch (org.springframework.web.client.HttpClientErrorException e) {
            // If rate limited, fallback to Azure
            if (e.getStatusCode() == HttpStatus.TOO_MANY_REQUESTS) {
                System.err.println("⚠️ Mistral embeddings API rate limit exceeded (429). Falling back to Azure OpenAI embeddings.");
                return getAzureEmbedding(text);
            }
            throw new RuntimeException("Error generating embedding: " + e.getMessage() + " - " + e.getResponseBodyAsString(), e);
        } catch (Exception e) {
            // If any other error, try Azure as fallback
            if (e.getMessage() != null && e.getMessage().contains("Rate limit")) {
                System.err.println("⚠️ Mistral embeddings API rate limit exceeded. Falling back to Azure OpenAI embeddings.");
                return getAzureEmbedding(text);
            }
            throw new RuntimeException("Error generating embedding: " + e.getMessage(), e);
        }
    }
    
    private List<Float> getMistralEmbedding(String text) {
        // Build request body for Mistral embeddings API
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("model", MISTRAL_EMBED_MODEL);
        requestBody.put("input", text);
        
        // Set up headers
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(mistralApiKey);
        
        HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
        
        // Make API call
        ResponseEntity<String> response = restTemplate.exchange(
                MISTRAL_EMBEDDINGS_API_URL,
                HttpMethod.POST,
                request,
                String.class
        );
        
        if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
            JsonNode jsonNode;
            try {
                jsonNode = objectMapper.readTree(response.getBody());
            } catch (Exception parseException) {
                throw new RuntimeException("Error parsing Mistral API response: " + parseException.getMessage(), parseException);
            }
            JsonNode data = jsonNode.get("data");
            
            if (data != null && data.isArray() && data.size() > 0) {
                JsonNode embeddingNode = data.get(0);
                JsonNode embeddingArray = embeddingNode.get("embedding");
                
                if (embeddingArray != null && embeddingArray.isArray()) {
                    // Convert JsonNode array to List<Float>
                    List<Float> floatEmbedding = new ArrayList<>();
                    for (JsonNode value : embeddingArray) {
                        floatEmbedding.add((float) value.asDouble());
                    }
                    return floatEmbedding;
                }
            }
            throw new RuntimeException("No embedding data returned from Mistral API");
        } else {
            // Handle rate limiting and other HTTP errors
            if (response.getStatusCode() == HttpStatus.TOO_MANY_REQUESTS) {
                throw new RuntimeException("Rate limit exceeded: " + response.getBody());
            }
            throw new RuntimeException("Mistral embeddings API returned status: " + response.getStatusCode() + " - " + response.getBody());
        }
    }
    
    private List<Float> getAzureEmbedding(String text) {
        if (azureEndpoint == null || azureEndpoint.isEmpty() || 
            azureApiKey == null || azureApiKey.isEmpty()) {
            throw new RuntimeException("Azure OpenAI embeddings not configured. Cannot fallback from Mistral rate limit.");
        }
        
        try {
            // Build Azure OpenAI embeddings endpoint
            String normalizedEndpoint = azureEndpoint.endsWith("/") 
                ? azureEndpoint.substring(0, azureEndpoint.length() - 1) 
                : azureEndpoint;
            String endpoint = normalizedEndpoint + "/openai/deployments/" + azureEmbeddingDeployment + 
                           "/embeddings?api-version=" + AZURE_API_VERSION;
            
            // Build request body for Azure OpenAI embeddings API
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("input", text);
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("api-key", azureApiKey);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            // Make API call
            ResponseEntity<String> response = restTemplate.exchange(
                    endpoint,
                    HttpMethod.POST,
                    request,
                    String.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                JsonNode jsonNode;
                try {
                    jsonNode = objectMapper.readTree(response.getBody());
                } catch (Exception parseException) {
                    throw new RuntimeException("Error parsing Azure OpenAI API response: " + parseException.getMessage(), parseException);
                }
                JsonNode data = jsonNode.get("data");
                
                if (data != null && data.isArray() && data.size() > 0) {
                    JsonNode embeddingNode = data.get(0);
                    JsonNode embeddingArray = embeddingNode.get("embedding");
                    
                    if (embeddingArray != null && embeddingArray.isArray()) {
                        // Convert JsonNode array to List<Float>
                        List<Float> floatEmbedding = new ArrayList<>();
                        for (JsonNode value : embeddingArray) {
                            floatEmbedding.add((float) value.asDouble());
                        }
                        System.out.println("✅ Successfully used Azure OpenAI embeddings (fallback from Mistral rate limit)");
                        return floatEmbedding;
                    }
                }
                throw new RuntimeException("No embedding data returned from Azure OpenAI API");
            } else {
                throw new RuntimeException("Azure OpenAI embeddings API returned status: " + response.getStatusCode() + " - " + response.getBody());
            }
        } catch (Exception e) {
            throw new RuntimeException("Error generating Azure OpenAI embedding: " + e.getMessage(), e);
        }
    }
}

