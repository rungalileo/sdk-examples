package com.chatbot.dto;

import java.util.Map;

public class ChatCompletionResult {
    private String response;
    private Map<String, Object> retrieverSpan;
    
    public ChatCompletionResult(String response, Map<String, Object> retrieverSpan) {
        this.response = response;
        this.retrieverSpan = retrieverSpan;
    }
    
    public String getResponse() {
        return response;
    }
    
    public Map<String, Object> getRetrieverSpan() {
        return retrieverSpan;
    }
}

