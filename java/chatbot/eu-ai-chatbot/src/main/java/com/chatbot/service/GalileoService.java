package com.chatbot.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.Instant;
import java.util.*;

@Service
public class GalileoService {
    
    private final String apiKey;
    private final String apiUrl;
    private final String projectId;
    private final String projectName;
    private final String logStreamId;
    private final String stageName;
    private final String stageId;
    private final Integer stageVersion;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private String currentSessionId;
    private volatile boolean sessionInitialized = false;
    private final Object sessionLock = new Object();
    
    public GalileoService(
            @Value("${galileo.api-key:}") String apiKey,
            @Value("${galileo.api-url:}") String apiUrl,
            @Value("${galileo.project-id:}") String projectId,
            @Value("${galileo.project-name:}") String projectName,
            @Value("${galileo.log-stream-id:}") String logStreamId,
            @Value("${galileo.stage-name:}") String stageName,
            @Value("${galileo.stage-id:}") String stageId,
            @Value("${galileo.stage-version:0}") Integer stageVersion) {
        this.apiKey = apiKey;
        this.apiUrl = apiUrl;
        this.projectId = projectId;
        this.projectName = projectName;
        this.logStreamId = logStreamId;
        this.stageName = stageName;
        this.stageId = stageId;
        this.stageVersion = stageVersion;
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
    }
    
    /**
     * Check if logging to Galileo is enabled
     * Requires: apiKey, projectId, logStreamId
     */
    public boolean isLoggingEnabled() {
        boolean enabled = apiKey != null && !apiKey.isEmpty() && !apiKey.equals("YOUR_GALILEO_API_KEY")
                && projectId != null && !projectId.isEmpty()
                && logStreamId != null && !logStreamId.isEmpty();
        
        if (!enabled) {
            System.out.println("Galileo Logging Status Check:");
            System.out.println("  apiKey: " + (apiKey != null && !apiKey.isEmpty() && !apiKey.equals("YOUR_GALILEO_API_KEY") ? "✓" : "✗"));
            System.out.println("  projectId: " + (projectId != null && !projectId.isEmpty() ? "✓" : "✗"));
            System.out.println("  logStreamId: " + (logStreamId != null && !logStreamId.isEmpty() ? "✓" : "✗"));
        }
        
        return enabled;
    }
    
    /**
     * Check if Galileo Protect is enabled
     * Requires: apiKey, stageName
     */
    public boolean isProtectEnabled() {
        boolean enabled = apiKey != null && !apiKey.isEmpty() && !apiKey.equals("YOUR_GALILEO_API_KEY")
                && stageName != null && !stageName.isEmpty();
        
        if (!enabled) {
            System.out.println("Galileo Protect Status Check:");
            System.out.println("  apiKey: " + (apiKey != null && !apiKey.isEmpty() && !apiKey.equals("YOUR_GALILEO_API_KEY") ? "✓" : "✗"));
            System.out.println("  stageName: " + (stageName != null && !stageName.isEmpty() ? "✓" : "✗"));
        }
        
        return enabled;
    }
    
    /**
     * @deprecated Use isLoggingEnabled() or isProtectEnabled() instead
     */
    @Deprecated
    public boolean isEnabled() {
        return isLoggingEnabled();
    }
    
    public String startSession() {
        if (!isLoggingEnabled()) {
            return null;
        }
        
        // Use synchronized block to ensure only one session is created at a time
        synchronized (sessionLock) {
            // Check if session already exists
            if (sessionInitialized && currentSessionId != null) {
                System.out.println("⚠️ Session already exists (" + currentSessionId + "). Skipping duplicate session creation.");
                return currentSessionId;
            }
            
            // Set flag immediately to prevent concurrent creation attempts
            sessionInitialized = true;
        }
        
        try {
            // Generate a unique external session ID
            String externalSessionId = UUID.randomUUID().toString();
            
            // Create session via Galileo v2 API
            Map<String, Object> sessionPayload = new HashMap<>();
            sessionPayload.put("log_stream_id", logStreamId);
            sessionPayload.put("name", "Chatbot Session " + externalSessionId.substring(0, 8));
            sessionPayload.put("external_id", externalSessionId);
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("Galileo-API-Key", apiKey);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(sessionPayload, headers);
            
            // Build the endpoint URL - format: /v2/projects/{project_id}/sessions
            String baseUrl = apiUrl.endsWith("/") ? apiUrl.substring(0, apiUrl.length() - 1) : apiUrl;
            String endpoint = baseUrl + "/v2/projects/" + projectId + "/sessions";
            
            try {
                ResponseEntity<String> response = restTemplate.exchange(
                        endpoint,
                        HttpMethod.POST,
                        request,
                        String.class
                );
                
                if (response.getStatusCode() == HttpStatus.OK || 
                    response.getStatusCode() == HttpStatus.CREATED) {
                    // Parse response to get the session ID generated by Galileo
                    if (response.getBody() != null) {
                        try {
                            JsonNode jsonNode = objectMapper.readTree(response.getBody());
                            JsonNode idNode = jsonNode.get("id");
                            if (idNode != null && !idNode.isNull()) {
                                this.currentSessionId = idNode.asText();
                                System.out.println("Galileo session created with ID: " + currentSessionId);
                                return currentSessionId;
                            }
                        } catch (Exception parseException) {
                            System.err.println("Error parsing session response: " + parseException.getMessage());
                            System.err.println("Response body: " + response.getBody());
                        }
                    }
                    // Fallback: use external_id if we can't parse the response
                    System.err.println("Could not parse session ID from response, using external_id");
                    this.currentSessionId = externalSessionId;
                    return currentSessionId;
                } else {
                    System.err.println("Failed to create Galileo session. Status: " + 
                                     response.getStatusCode() + " Response: " + response.getBody());
                    // Fallback: use external_id as session_id
                    this.currentSessionId = externalSessionId;
                    return currentSessionId;
                }
            } catch (Exception e) {
                System.err.println("Error creating Galileo session: " + e.getMessage());
                if (e.getCause() != null) {
                    System.err.println("Cause: " + e.getCause().getMessage());
                }
                // Fallback: use external_id as session_id even if API call fails
                this.currentSessionId = externalSessionId;
                return currentSessionId;
            }
        } catch (Exception e) {
            System.err.println("Error starting Galileo session: " + e.getMessage());
            e.printStackTrace();
            // Reset flag on error so retry is possible
            synchronized (sessionLock) {
                this.sessionInitialized = false;
            }
            return null;
        }
    }
    
    public void closeSession() {
        if (!isLoggingEnabled() || currentSessionId == null) {
            return;
        }
        
        try {
            // Just close the session without logging a trace
            String closedSessionId = this.currentSessionId;
            this.currentSessionId = null;
            this.sessionInitialized = false;
            System.out.println("Galileo session closed: " + closedSessionId);
        } catch (Exception e) {
            System.err.println("Error closing Galileo session: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    public void logChatInteraction(String userInput, String assistantOutput, String provider, String model,
                                   long durationNs, String traceId, Map<String, Object> retrieverSpan, String originalLlmResponse, Double protectProbability,
                                   Map<String, Object> protectInputSpan, Map<String, Object> protectOutputSpan, List<Map<String, String>> fullMessages) {
        System.out.println("Galileo: logChatInteraction called");
        System.out.println("Galileo: isLoggingEnabled() = " + isLoggingEnabled());
        
        if (!isLoggingEnabled()) {
            System.out.println("⚠️ Galileo: Logging is disabled, skipping trace logging");
            return;
        }
        
        try {
            System.out.println("Galileo: Starting to log chat interaction");
            // Use provided traceId or generate a new one
            if (traceId == null || traceId.isEmpty()) {
                traceId = UUID.randomUUID().toString();
            }
            
            // Build input/output data
            Map<String, Object> inputData = new HashMap<>();
            inputData.put("role", "user");
            inputData.put("content", userInput);
            
            Map<String, Object> outputData = new HashMap<>();
            outputData.put("role", "assistant");
            outputData.put("content", assistantOutput);
            
            // Estimate token counts (rough approximation: 1 token ≈ 4 characters)
            int inputTokens = Math.max(1, userInput.length() / 4);
            int outputTokens = Math.max(1, assistantOutput.length() / 4);
            int totalTokens = inputTokens + outputTokens;
            
            // Create trace metadata
            Map<String, Object> traceMetadata = new HashMap<>();
            traceMetadata.put("trace_id", traceId);
            traceMetadata.put("session_id", currentSessionId);
            traceMetadata.put("provider", provider);
            traceMetadata.put("model", model);
            traceMetadata.put("input_tokens", inputTokens);
            traceMetadata.put("output_tokens", outputTokens);
            traceMetadata.put("total_tokens", totalTokens);
            traceMetadata.put("duration_ns", durationNs);
            traceMetadata.put("timestamp", Instant.now().toString());
            // Add original LLM response to metadata if it was overridden
            if (originalLlmResponse != null && !originalLlmResponse.isEmpty() && !originalLlmResponse.equals(assistantOutput)) {
                traceMetadata.put("original_llm_response", originalLlmResponse);
            }
            // Add protect probability to metadata if available
            if (protectProbability != null) {
                traceMetadata.put("context_adherence_luna_protect_probability", protectProbability);
            }
            
            // Log the trace with optional retriever span and Protect span as children
            System.out.println("Galileo: Calling logTraceWithSpans with:");
            System.out.println("  - retrieverSpan: " + (retrieverSpan != null ? "present" : "null"));
            System.out.println("  - protectOutputSpan: " + (protectOutputSpan != null ? "present" : "null"));
            System.out.println("  - fullMessages: " + (fullMessages != null ? fullMessages.size() + " messages" : "null"));
            logTraceWithSpans("chat_interaction", traceMetadata, inputData, outputData, retrieverSpan, traceId, protectInputSpan, protectOutputSpan, fullMessages);
            System.out.println("Galileo: logTraceWithSpans completed");
            
        } catch (Exception e) {
            System.err.println("❌ Error logging to Galileo: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    private void logTrace(String eventType, Map<String, Object> metadata, 
                         Map<String, Object> input, Map<String, Object> output) {
        if (!isLoggingEnabled()) {
            return;
        }
        
        try {
            // Build the trace according to Galileo v2 API format
            Map<String, Object> trace = new HashMap<>();
            
            if (input != null) {
                // For chat interactions, format input as a message
                if (input.containsKey("content")) {
                    trace.put("input", input.get("content"));
                } else {
                    trace.put("input", input);
                }
            }
            
            if (output != null) {
                // For chat interactions, format output as a message
                if (output.containsKey("content")) {
                    trace.put("output", output.get("content"));
                } else {
                    trace.put("output", output);
                }
            }
            
            // Add metadata fields
            if (metadata != null) {
                if (metadata.containsKey("timestamp")) {
                    trace.put("created_at", metadata.get("timestamp"));
                }
                if (metadata.containsKey("duration_ns")) {
                    Map<String, Object> metrics = new HashMap<>();
                    metrics.put("duration_ns", metadata.get("duration_ns"));
                    trace.put("metrics", metrics);
                }
            }
            
            // Build the request payload according to Galileo v2 API
            Map<String, Object> tracePayload = new HashMap<>();
            tracePayload.put("log_stream_id", logStreamId);
            
            if (currentSessionId != null) {
                tracePayload.put("session_id", currentSessionId);
            }
            
            // Extract trace_id from metadata if available
            String traceIdValue = null;
            if (metadata != null && metadata.containsKey("trace_id")) {
                traceIdValue = metadata.get("trace_id").toString();
                tracePayload.put("trace_id", traceIdValue);
            }
            
            List<Map<String, Object>> tracesList = new ArrayList<>();
            tracesList.add(trace);
            tracePayload.put("traces", tracesList);
            
            // Set up headers - Galileo v2 API uses Galileo-API-Key header
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("Galileo-API-Key", apiKey);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(tracePayload, headers);
            
            // Build the endpoint URL - format: /v2/projects/{project_id}/traces
            String baseUrl = apiUrl.endsWith("/") ? apiUrl.substring(0, apiUrl.length() - 1) : apiUrl;
            String endpoint = baseUrl + "/v2/projects/" + projectId + "/traces";
            
            try {
                ResponseEntity<String> response = restTemplate.exchange(
                        endpoint,
                        HttpMethod.POST,
                        request,
                        String.class
                );
                
                if (response.getStatusCode() != HttpStatus.OK && 
                    response.getStatusCode() != HttpStatus.CREATED) {
                    System.err.println("Galileo API returned status: " + response.getStatusCode() + 
                                     " Response: " + response.getBody());
                }
            } catch (Exception e) {
                System.err.println("Error calling Galileo API at " + endpoint + ": " + e.getMessage());
                if (e.getCause() != null) {
                    System.err.println("Cause: " + e.getCause().getMessage());
                }
                // Don't throw - we don't want to break the app if logging fails
            }
            
        } catch (Exception e) {
            System.err.println("Error creating trace payload: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    public String getCurrentSessionId() {
        return currentSessionId;
    }
    
    public Map<String, Object> createRetrieverSpan(String query, List<String> retrievedDocuments) {
        if (!isLoggingEnabled()) {
            return null;
        }
        
        try {
            // Build the retriever span for document retrieval
            Map<String, Object> span = new HashMap<>();
            span.put("created_at", Instant.now().toString());
            span.put("type", "retriever");
            span.put("name", "Documents Retrieval");
            
            // Input: the query (string)
            span.put("input", query);
            
            // Output: array of objects (each document as an object)
            List<Map<String, Object>> outputArray = new ArrayList<>();
            if (retrievedDocuments != null && !retrievedDocuments.isEmpty()) {
                for (String doc : retrievedDocuments) {
                    Map<String, Object> docObj = new HashMap<>();
                    docObj.put("content", doc);
                    outputArray.add(docObj);
                }
            }
            span.put("output", outputArray);
            
            // Metrics: number of documents retrieved
            Map<String, Object> metrics = new HashMap<>();
            metrics.put("documents_retrieved", retrievedDocuments != null ? retrievedDocuments.size() : 0);
            span.put("metrics", metrics);
            
            // Status code
            span.put("status_code", 200);
            
            return span;
        } catch (Exception e) {
            System.err.println("Error creating retriever span: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }
    
    private void logTraceWithSpans(String eventType, Map<String, Object> metadata, 
                                   Map<String, Object> input, Map<String, Object> output,
                                   Map<String, Object> retrieverSpan, String traceId,
                                   Map<String, Object> protectInputSpan, Map<String, Object> protectOutputSpan,
                                   List<Map<String, String>> fullMessages) {
        if (!isLoggingEnabled()) {
            return;
        }
        
        try {
            // Build the trace that can contain child spans
            Map<String, Object> trace = new HashMap<>();
            trace.put("type", "trace");
            trace.put("created_at", metadata != null && metadata.containsKey("timestamp") 
                ? metadata.get("timestamp").toString() 
                : Instant.now().toString());
            
            if (input != null) {
                if (input.containsKey("content")) {
                    trace.put("input", input.get("content"));
                } else {
                    trace.put("input", input);
                }
            }
            
            if (output != null) {
                if (output.containsKey("content")) {
                    trace.put("output", output.get("content"));
                } else {
                    trace.put("output", output);
                }
            }
            
            // Add user_metadata if original_llm_response or context_adherence_luna_protect_probability is present
            if (metadata != null && (metadata.containsKey("original_llm_response") || metadata.containsKey("context_adherence_luna_protect_probability"))) {
                Map<String, Object> userMetadata = new HashMap<>();
                if (metadata.containsKey("original_llm_response")) {
                    userMetadata.put("original_llm_response", metadata.get("original_llm_response"));
                }
                if (metadata.containsKey("context_adherence_luna_protect_probability")) {
                    // Convert to string as user_metadata requires string values
                    Object probValue = metadata.get("context_adherence_luna_protect_probability");
                    if (probValue != null) {
                        userMetadata.put("context_adherence_luna_protect_probability", String.valueOf(probValue));
                    }
                }
                trace.put("user_metadata", userMetadata);
            }
            
            // Add child spans (retriever span, Protect spans, and LLM span)
            List<Map<String, Object>> childSpans = new ArrayList<>();
            
            // Add retriever span if provided
            if (retrieverSpan != null) {
                retrieverSpan.put("trace_id", traceId);
                childSpans.add(retrieverSpan);
            }
            
            // Add LLM span for the chat completion
            Map<String, Object> llmSpan = new HashMap<>();
            llmSpan.put("type", "llm");
            llmSpan.put("created_at", Instant.now().toString());
            llmSpan.put("name", "Chat Completion");
            
            // Use the full messages array if available (includes system message with RAG context!)
            if (fullMessages != null && !fullMessages.isEmpty()) {
                System.out.println("📊 [GalileoService] Using full messages array for LLM span (" + fullMessages.size() + " messages)");
                // Convert to List<Map<String, Object>> for Galileo
                List<Map<String, Object>> inputMessages = new ArrayList<>();
                for (Map<String, String> msg : fullMessages) {
                    Map<String, Object> msgCopy = new HashMap<>(msg);
                    inputMessages.add(msgCopy);
                }
                llmSpan.put("input", inputMessages);
            } else if (input != null && input.containsKey("content")) {
                // Fallback to just the user message if full messages not available
                System.out.println("⚠️  [GalileoService] Full messages not available, using fallback (user message only)");
                List<Map<String, Object>> inputMessages = new ArrayList<>();
                Map<String, Object> userMsg = new HashMap<>();
                userMsg.put("role", "user");
                userMsg.put("content", input.get("content"));
                inputMessages.add(userMsg);
                llmSpan.put("input", inputMessages);
            }
            if (output != null && output.containsKey("content")) {
                Map<String, Object> assistantMsg = new HashMap<>();
                assistantMsg.put("role", "assistant");
                assistantMsg.put("content", output.get("content"));
                llmSpan.put("output", assistantMsg);
            }
            if (metadata != null) {
                Map<String, Object> llmMetrics = new HashMap<>();
                if (metadata.containsKey("input_tokens")) {
                    llmMetrics.put("input_tokens", metadata.get("input_tokens"));
                }
                if (metadata.containsKey("output_tokens")) {
                    llmMetrics.put("output_tokens", metadata.get("output_tokens"));
                }
                if (metadata.containsKey("total_tokens")) {
                    llmMetrics.put("total_tokens", metadata.get("total_tokens"));
                }
                if (metadata.containsKey("duration_ns")) {
                    llmMetrics.put("duration_ns", metadata.get("duration_ns"));
                }
                if (!llmMetrics.isEmpty()) {
                    llmSpan.put("metrics", llmMetrics);
                }
                
                // Add user_metadata to LLM span if original_llm_response or context_adherence_luna_protect_probability is present
                if (metadata.containsKey("original_llm_response") || metadata.containsKey("context_adherence_luna_protect_probability")) {
                    Map<String, Object> llmUserMetadata = new HashMap<>();
                    if (metadata.containsKey("original_llm_response")) {
                        llmUserMetadata.put("original_llm_response", metadata.get("original_llm_response"));
                    }
                    if (metadata.containsKey("context_adherence_luna_protect_probability")) {
                        // Convert to string as user_metadata requires string values
                        Object probValue = metadata.get("context_adherence_luna_protect_probability");
                        if (probValue != null) {
                            llmUserMetadata.put("context_adherence_luna_protect_probability", String.valueOf(probValue));
                        }
                    }
                    llmSpan.put("user_metadata", llmUserMetadata);
                }
            }
            llmSpan.put("trace_id", traceId);
            childSpans.add(llmSpan);
            
            // Add Protect tool span if provided (after LLM - only one Protect span)
            if (protectOutputSpan != null) {
                protectOutputSpan.put("trace_id", traceId);
                protectOutputSpan.put("parent_id", traceId);
                childSpans.add(protectOutputSpan);
            }
            
            if (!childSpans.isEmpty()) {
                trace.put("spans", childSpans);
            }
            
            // Build the request payload
            Map<String, Object> tracePayload = new HashMap<>();
            tracePayload.put("log_stream_id", logStreamId);
            
            if (currentSessionId != null) {
                tracePayload.put("session_id", currentSessionId);
            }
            
            tracePayload.put("trace_id", traceId);
            
            List<Map<String, Object>> tracesList = new ArrayList<>();
            tracesList.add(trace);
            tracePayload.put("traces", tracesList);
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("Galileo-API-Key", apiKey);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(tracePayload, headers);
            
            // Build the endpoint URL - format: /v2/projects/{project_id}/traces
            String baseUrl = apiUrl.endsWith("/") ? apiUrl.substring(0, apiUrl.length() - 1) : apiUrl;
            String endpoint = baseUrl + "/v2/projects/" + projectId + "/traces";
            
            try {
                System.out.println("Galileo: Sending trace to " + endpoint);
                System.out.println("Galileo: Trace ID: " + traceId);
                System.out.println("Galileo: Session ID: " + currentSessionId);
                System.out.println("Galileo: Log Stream ID: " + logStreamId);
                System.out.println("Galileo: Number of child spans: " + (childSpans != null ? childSpans.size() : 0));
                
                ResponseEntity<String> response = restTemplate.exchange(
                        endpoint,
                        HttpMethod.POST,
                        request,
                        String.class
                );
                
                System.out.println("Galileo: API response status: " + response.getStatusCode());
                if (response.getStatusCode() == HttpStatus.OK || 
                    response.getStatusCode() == HttpStatus.CREATED) {
                    System.out.println("✅ Galileo: Trace logged successfully");
                    if (response.getBody() != null) {
                        System.out.println("Galileo: Response body: " + response.getBody());
                    }
                } else {
                    System.err.println("❌ Galileo API returned status: " + response.getStatusCode() + 
                                     " Response: " + response.getBody());
                }
            } catch (Exception e) {
                System.err.println("❌ Error calling Galileo API at " + endpoint + ": " + e.getMessage());
                e.printStackTrace();
                if (e.getCause() != null) {
                    System.err.println("Cause: " + e.getCause().getMessage());
                    e.getCause().printStackTrace();
                }
                // Don't throw - we don't want to break the app if logging fails
            }
            
        } catch (Exception e) {
            System.err.println("❌ Error creating trace with spans payload: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Result wrapper for Protect invocation that includes both the result and tool span
     */
    public static class ProtectInvocationResult {
        private final ProtectResult result;
        private final Map<String, Object> toolSpan;
        
        public ProtectInvocationResult(ProtectResult result, Map<String, Object> toolSpan) {
            this.result = result;
            this.toolSpan = toolSpan;
        }
        
        public ProtectResult getResult() {
            return result;
        }
        
        public Map<String, Object> getToolSpan() {
            return toolSpan;
        }
    }
    
    /**
     * Invoke Galileo Protect to check input/output for security issues
     * @param input The input text to check (user message only)
     * @param output The output text to check (can be null for input-only checks)
     * @param context The context/documents retrieved from RAG (can be null)
     * @param originalLlmResponse The original LLM response to include in metadata (can be null)
     * @param checkType "input" or "output" to identify the type of check
     * @param traceId The trace ID to link the tool span to
     * @param fullMessages The complete messages array sent to the LLM (includes system message with RAG context)
     * @return ProtectInvocationResult containing both the result and tool span, or null if protect is disabled
     */
    public ProtectInvocationResult invokeProtect(String input, String output, String context, String originalLlmResponse, String checkType, String traceId, List<Map<String, String>> fullMessages) {
        System.out.println("Galileo Protect: Starting invocation check...");
        System.out.println("  stageName: " + (stageName != null ? stageName : "NULL"));
        System.out.println("  stageId: " + (stageId != null ? stageId : "NULL"));
        System.out.println("  stageVersion: " + stageVersion);
        
        if (!isProtectEnabled()) {
            System.out.println("❌ Galileo Protect: Service not enabled - check configuration");
            return null;
        }
        
        System.out.println("✅ Galileo Protect: All checks passed, proceeding with API call");
        
        try {
            // Build the protect request payload matching the example format
            Map<String, Object> requestBody = new HashMap<>();
            
            // Build the complete input from fullMessages if available (includes system message with RAG context)
            String fullInput = input;
            if (fullMessages != null && !fullMessages.isEmpty()) {
                StringBuilder sb = new StringBuilder();
                for (Map<String, String> msg : fullMessages) {
                    String role = msg.get("role");
                    String content = msg.get("content");
                    if (content != null) {
                        sb.append("[").append(role).append("]: ").append(content).append("\n\n");
                    }
                }
                fullInput = sb.toString();
                System.out.println("Galileo Protect: Using full messages array (" + fullMessages.size() + " messages, total length: " + fullInput.length() + " chars)");
            } else {
                System.out.println("Galileo Protect: Using simple input (no full messages available)");
            }
            
            // Payload with input, output, and context
            Map<String, Object> payload = new HashMap<>();
            payload.put("input", fullInput);
            if (output != null) {
                payload.put("output", output);
            }
            if (context != null && !context.isEmpty()) {
                payload.put("context", context);
                System.out.println("Galileo Protect: Adding context to payload (length: " + context.length() + " chars)");
            } else {
                System.out.println("Galileo Protect: No context available for payload");
            }
            requestBody.put("payload", payload);
            
            // Project and stage information (matching the example format)
            if (projectName != null && !projectName.isEmpty()) {
                requestBody.put("project_name", projectName);
            }
            // Optionally add project_id, stage_id, stage_version for extra safety
            if (projectId != null && !projectId.isEmpty()) {
                requestBody.put("project_id", projectId);
            }
            requestBody.put("stage_name", stageName);
            if (stageId != null && !stageId.isEmpty()) {
                requestBody.put("stage_id", stageId);
            }
            if (stageVersion != null) {
                requestBody.put("stage_version", stageVersion);
            }
            requestBody.put("timeout", 300);
            
            // Add metadata with source and original LLM response if available
            Map<String, Object> metadata = new HashMap<>();
            metadata.put("source", "java-ragbot");
            if (originalLlmResponse != null && !originalLlmResponse.isEmpty()) {
                metadata.put("original_llm_response", originalLlmResponse);
            }
            requestBody.put("metadata", metadata);
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("Galileo-API-Key", apiKey);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            // Build the endpoint URL - format: /v2/protect/invoke
            String baseUrl = apiUrl.endsWith("/") ? apiUrl.substring(0, apiUrl.length() - 1) : apiUrl;
            String endpoint = baseUrl + "/v2/protect/invoke";
            
            System.out.println("Galileo Protect: Calling " + endpoint);
            
            try {
                ResponseEntity<String> response = restTemplate.exchange(
                        endpoint,
                        HttpMethod.POST,
                        request,
                        String.class
                );
                
                System.out.println("Galileo Protect: Response status: " + response.getStatusCode());
                System.out.println("Galileo Protect: Response body: " + response.getBody());
                
                if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                    JsonNode jsonNode = objectMapper.readTree(response.getBody());
                    
                    String status = jsonNode.has("status") ? jsonNode.get("status").asText() : null;
                    String text = jsonNode.has("text") ? jsonNode.get("text").asText() : null;
                    
                    System.out.println("Galileo Protect: Status: " + status + ", Text: " + text);
                    
                    // Check if action was taken - use action_result only if present
                    String actionType = null;
                    String actionValue = null;
                    Double protectProbability = null;
                    
                    if (jsonNode.has("action_result")) {
                        JsonNode actionResult = jsonNode.get("action_result");
                        if (actionResult.has("type")) {
                            actionType = actionResult.get("type").asText();
                        }
                        if (actionResult.has("value")) {
                            JsonNode valueNode = actionResult.get("value");
                            if (valueNode.isTextual()) {
                                actionValue = valueNode.asText();
                            } else if (valueNode.isNumber()) {
                                // If value is a number, it might be a probability
                                double rawValue = valueNode.asDouble();
                                protectProbability = Math.round(rawValue * 10000.0) / 10000.0;
                            }
                        }
                        System.out.println("Galileo Protect: Action type: " + actionType + ", Action value: " + actionValue);
                    } else {
                        System.out.println("Galileo Protect: No action_result in response");
                    }
                    
                    // Use text from response if action_result.value is not available
                    if (actionValue == null && text != null) {
                        actionValue = text;
                    }
                    
                    // Extract probability from various possible locations in the response
                    // First, check if there's a "value" field directly at the top level
                    if (jsonNode.has("value") && jsonNode.get("value").isNumber()) {
                        double rawValue = jsonNode.get("value").asDouble();
                        protectProbability = Math.round(rawValue * 10000.0) / 10000.0;
                        System.out.println("Galileo Protect: Found probability at top level: " + protectProbability);
                    }
                    
                    // Check metric_results (look for prompt_injection or other metric values)
                    if (protectProbability == null && jsonNode.has("metric_results")) {
                        JsonNode metricResults = jsonNode.get("metric_results");
                        if (metricResults.isObject()) {
                            // Also check if metric_results has prompt_injection directly
                            if (metricResults.has("prompt_injection")) {
                                JsonNode promptInjection = metricResults.get("prompt_injection");
                                if (promptInjection.has("value") && promptInjection.get("value").isNumber()) {
                                    double rawValue = promptInjection.get("value").asDouble();
                                    protectProbability = Math.round(rawValue * 10000.0) / 10000.0;
                                    System.out.println("Galileo Protect: Found prompt_injection probability: " + protectProbability);
                                }
                            }
                            // Look for any metric with a numeric value
                            if (protectProbability == null) {
                                java.util.Iterator<java.util.Map.Entry<String, JsonNode>> fields = metricResults.fields();
                                while (fields.hasNext() && protectProbability == null) {
                                    java.util.Map.Entry<String, JsonNode> entry = fields.next();
                                    JsonNode metricResult = entry.getValue();
                                    if (metricResult.has("value") && metricResult.get("value").isNumber()) {
                                        double rawValue = metricResult.get("value").asDouble();
                                        protectProbability = Math.round(rawValue * 10000.0) / 10000.0;
                                        System.out.println("Galileo Protect: Found probability in metric " + entry.getKey() + ": " + protectProbability);
                                    }
                                }
                            }
                        }
                    }
                    
                    // Also check action_result for value (could be a number)
                    if (protectProbability == null && jsonNode.has("action_result")) {
                        JsonNode actionResult = jsonNode.get("action_result");
                        if (actionResult.has("value")) {
                            JsonNode valueNode = actionResult.get("value");
                            if (valueNode.isNumber()) {
                                double rawValue = valueNode.asDouble();
                                protectProbability = Math.round(rawValue * 10000.0) / 10000.0;
                                System.out.println("Galileo Protect: Found probability in action_result.value: " + protectProbability);
                            }
                        }
                    }
                    
                    ProtectResult result = new ProtectResult(status, text, actionType, actionValue, protectProbability);
                    System.out.println("Galileo Protect: Was overridden: " + result.wasOverridden());
                    if (protectProbability != null) {
                        System.out.println("Galileo Protect: Probability: " + protectProbability);
                    }
                    
                    // Create tool span for this Protect invocation
                    Map<String, Object> toolSpan = createProtectToolSpan(
                        payload, response.getBody(), result, checkType, traceId, 
                        response.getStatusCode().value(), protectProbability
                    );
                    
                    return new ProtectInvocationResult(result, toolSpan);
                } else {
                    System.err.println("Galileo Protect API returned status: " + response.getStatusCode() + 
                                     " Response: " + response.getBody());
                    
                    // Create tool span even for failed requests
                    Map<String, Object> toolSpan = createProtectToolSpan(
                        payload, response.getBody(), null, checkType, traceId,
                        response.getStatusCode().value(), null
                    );
                    
                    return new ProtectInvocationResult(null, toolSpan);
                }
            } catch (Exception e) {
                System.err.println("Error calling Galileo Protect API at " + endpoint + ": " + e.getMessage());
                e.printStackTrace();
                if (e.getCause() != null) {
                    System.err.println("Cause: " + e.getCause().getMessage());
                }
                // Don't throw - we don't want to break the app if protect fails
                // Create tool span for error case
                Map<String, Object> toolSpan = createProtectToolSpan(
                    payload, "Error: " + e.getMessage(), null, checkType, traceId,
                    500, null
                );
                return new ProtectInvocationResult(null, toolSpan);
            }
            
        } catch (Exception e) {
            System.err.println("Error creating protect request payload: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }
    
    /**
     * Create a tool span for a Protect invocation
     */
    private Map<String, Object> createProtectToolSpan(
            Map<String, Object> requestPayload, String responseBody, ProtectResult result,
            String checkType, String traceId, int statusCode, Double protectProbability) {
        
        if (!isLoggingEnabled()) {
            return null;
        }
        
        try {
            Map<String, Object> toolSpan = new HashMap<>();
            toolSpan.put("type", "tool");
            toolSpan.put("name", "GalileoProtect");
            toolSpan.put("created_at", Instant.now().toString());
            
            // Input: the Protect request payload as JSON string
            try {
                String inputJson = objectMapper.writeValueAsString(requestPayload);
                toolSpan.put("input", inputJson);
            } catch (Exception e) {
                toolSpan.put("input", requestPayload.toString());
            }
            
            // Output: the Protect response as JSON string (or error message)
            if (responseBody != null) {
                toolSpan.put("output", responseBody);
            } else if (result != null) {
                // Fallback: create a simple output from the result
                Map<String, Object> outputMap = new HashMap<>();
                outputMap.put("status", result.getStatus());
                outputMap.put("text", result.getText());
                try {
                    toolSpan.put("output", objectMapper.writeValueAsString(outputMap));
                } catch (Exception e) {
                    toolSpan.put("output", outputMap.toString());
                }
            }
            
            // Status code from the HTTP response
            toolSpan.put("status_code", statusCode);
            
            // User metadata
            Map<String, Object> userMetadata = new HashMap<>();
            userMetadata.put("check_type", checkType != null ? checkType : "unknown");
            if (result != null) {
                userMetadata.put("protect_status", result.getStatus() != null ? result.getStatus() : "unknown");
                userMetadata.put("was_overridden", String.valueOf(result.wasOverridden()));
            }
            if (protectProbability != null) {
                userMetadata.put("protect_probability", String.valueOf(protectProbability));
            }
            toolSpan.put("user_metadata", userMetadata);
            
            // Link to trace
            toolSpan.put("trace_id", traceId);
            toolSpan.put("parent_id", traceId); // Parent is the trace itself
            if (currentSessionId != null) {
                toolSpan.put("session_id", currentSessionId);
            }
            
            return toolSpan;
        } catch (Exception e) {
            System.err.println("Error creating Protect tool span: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }
    
    /**
     * Result from Galileo Protect invocation
     */
    public static class ProtectResult {
        private final String status;
        private final String text;
        private final String actionType;
        private final String actionValue;
        private final Double protectProbability;
        
        public ProtectResult(String status, String text, String actionType, String actionValue, Double protectProbability) {
            this.status = status;
            this.text = text;
            this.actionType = actionType;
            this.actionValue = actionValue;
            this.protectProbability = protectProbability;
        }
        
        public String getStatus() {
            return status;
        }
        
        public String getText() {
            return text;
        }
        
        public String getActionType() {
            return actionType;
        }
        
        public String getActionValue() {
            return actionValue;
        }
        
        public Double getProtectProbability() {
            return protectProbability;
        }
        
        /**
         * Determine if the response was overridden.
         * Canonical signal: status=="triggered" + text != null
         * Falls back to action_result.type == "OVERRIDE" if present
         */
        public boolean wasOverridden() {
            // Canonical signal: status=="triggered" + text != null
            if ("triggered".equals(status) && text != null && !text.isEmpty()) {
                return true;
            }
            // Fallback: use action_result if present
            if (actionType != null && "OVERRIDE".equals(actionType)) {
                return true;
            }
            return false;
        }
        
        /**
         * Get the override text to use.
         * Prefers action_result.value if available, otherwise uses text from response.
         */
        public String getOverrideText() {
            if (actionValue != null && !actionValue.isEmpty()) {
                return actionValue;
            }
            if (text != null && !text.isEmpty()) {
                return text;
            }
            return null;
        }
    }
}

