package com.chatbot.dto;

import java.util.List;
import java.util.Map;

public class ChatCompletionResult {
    private String response;
    private Map<String, Object> retrieverSpan;
    private List<Map<String, String>> fullMessages; // The complete messages array sent to the LLM
    
    public ChatCompletionResult(String response, Map<String, Object> retrieverSpan) {
        this.response = response;
        this.retrieverSpan = retrieverSpan;
        this.fullMessages = null;
    }
    
    public ChatCompletionResult(String response, Map<String, Object> retrieverSpan, List<Map<String, String>> fullMessages) {
        this.response = response;
        this.retrieverSpan = retrieverSpan;
        this.fullMessages = fullMessages;
    }
    
    public String getResponse() {
        return response;
    }
    
    public Map<String, Object> getRetrieverSpan() {
        return retrieverSpan;
    }
    
    public List<Map<String, String>> getFullMessages() {
        return fullMessages;
    }
}

