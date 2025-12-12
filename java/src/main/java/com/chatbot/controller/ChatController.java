package com.chatbot.controller;

import com.chatbot.dto.ChatRequest;
import com.chatbot.dto.ChatResponse;
import com.chatbot.service.AzureOpenAIService;
import com.chatbot.service.DocumentService;
import com.chatbot.service.GalileoService;
import com.chatbot.service.MistralService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/chat")
@CrossOrigin(origins = "http://localhost:3000")
public class ChatController {
    
    @Autowired
    private AzureOpenAIService azureOpenAIService;
    
    @Autowired
    private MistralService mistralService;
    
    @Autowired
    private GalileoService galileoService;
    
    @Autowired
    private DocumentService documentService;
    
    @Value("${azure.openai.deployment-name:gpt-5-nano}")
    private String azureModelName;
    
    @Value("${mistral.model:mistral-medium}")
    private String mistralModelName;
    
    @PostMapping
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatRequest request) {
        long startTime = System.nanoTime();
        String userInput = request.getMessage();
        
        // Check if user wants to end the session
        if (userInput != null && userInput.trim().equalsIgnoreCase("im finished")) {
            if (galileoService.isLoggingEnabled()) {
                galileoService.closeSession();
            }
            return ResponseEntity.ok(new ChatResponse("Session ended. Thank you!"));
        }
        
        String provider = request.getProvider() != null ? request.getProvider().toLowerCase() : "azure";
        String modelName = "azure".equals(provider) ? azureModelName : mistralModelName;
        String traceId = java.util.UUID.randomUUID().toString();
        
        // Retrieve relevant context using RAG (happens first, independently)
        List<String> relevantContext = documentService.retrieveRelevantContext(userInput, 3);
        String contextText = relevantContext != null && !relevantContext.isEmpty()
            ? relevantContext.stream().collect(Collectors.joining("\n\n"))
            : null;
        
        // Create retriever span NOW (before Protect) so it's independent
        java.util.Map<String, Object> retrieverSpan = null;
        if (galileoService.isLoggingEnabled()) {
            retrieverSpan = galileoService.createRetrieverSpan(userInput, relevantContext);
        }
        
        com.chatbot.dto.ChatCompletionResult completionResult = null;
        
        try {
            // Now call the LLM (after document retrieval, no Protect input check)
            // Pass the already-retrieved context to avoid duplicate retrieval
            if ("mistral".equals(provider)) {
                completionResult = mistralService.getChatCompletion(
                    request.getMessage(),
                    request.getHistory(),
                    traceId,
                    relevantContext
                );
            } else {
                // Default to Azure
                completionResult = azureOpenAIService.getChatCompletion(
                    request.getMessage(),
                    request.getHistory(),
                    traceId,
                    relevantContext
                );
            }
            
            long durationNs = System.nanoTime() - startTime;
            String originalLlmResponse = completionResult != null ? completionResult.getResponse() : null;
            String response = originalLlmResponse;
            // Retriever span was already created above, before Protect
            
            // Invoke Protect on output after getting response (only one Protect check)
            GalileoService.ProtectInvocationResult protectInvocation = null;
            if (galileoService.isProtectEnabled() && response != null) {
                System.out.println("=== PROTECT CHECK ===");
                protectInvocation = galileoService.invokeProtect(userInput, response, contextText, originalLlmResponse, "output", traceId);
                if (protectInvocation != null && protectInvocation.getResult() != null) {
                    GalileoService.ProtectResult protectResult = protectInvocation.getResult();
                    if (protectResult.wasOverridden()) {
                        // Output was blocked, use the override message but keep original in metadata
                        String overrideText = protectResult.getOverrideText();
                        System.out.println("🚫 PROTECT BLOCKED OUTPUT - Using override, but original LLM response saved in metadata");
                        System.out.println("  Original LLM response: " + originalLlmResponse);
                        System.out.println("  Override message: " + overrideText);
                        response = overrideText;
                    } else {
                        System.out.println("✅ PROTECT ALLOWED OUTPUT");
                    }
                }
                System.out.println("=== END PROTECT CHECK ===");
            }
            
            // Log the interaction to Galileo (1 trace per input/output)
            // Include original LLM response and protect probability in metadata if available
            if (galileoService.isLoggingEnabled() && response != null) {
                String originalForMetadata = (originalLlmResponse != null && !originalLlmResponse.equals(response)) 
                    ? originalLlmResponse 
                    : null;
                // Extract protect probability from the Protect check result
                Double protectProbability = (protectInvocation != null && protectInvocation.getResult() != null) 
                    ? protectInvocation.getResult().getProtectProbability() 
                    : null;
                // Extract tool span from Protect invocation (only one Protect span)
                Map<String, Object> protectSpan = (protectInvocation != null) ? protectInvocation.getToolSpan() : null;
                galileoService.logChatInteraction(userInput, response, provider, modelName, durationNs, traceId, retrieverSpan, originalForMetadata, protectProbability, null, protectSpan);
            }
            
            return ResponseEntity.ok(new ChatResponse(response));
        } catch (Exception e) {
            long durationNs = System.nanoTime() - startTime;
            e.printStackTrace(); // Log the full stack trace
            String errorMessage = e.getMessage();
            if (e.getCause() != null) {
                errorMessage += " (Cause: " + e.getCause().getMessage() + ")";
            }
            
            // Log error to Galileo if enabled
            if (galileoService.isLoggingEnabled()) {
                galileoService.logChatInteraction(userInput, "Error: " + errorMessage, provider, modelName, durationNs, traceId, null, null, null, null, null);
            }
            
            return ResponseEntity.status(500)
                .body(new ChatResponse("Error: " + errorMessage));
        }
    }
}

