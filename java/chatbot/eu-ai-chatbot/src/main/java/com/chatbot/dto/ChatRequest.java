package com.chatbot.dto;

import java.util.List;

public class ChatRequest {
    private String message;
    private List<String> history;
    private String provider; // "azure" or "mistral"
    
    public String getMessage() {
        return message;
    }
    
    public void setMessage(String message) {
        this.message = message;
    }
    
    public List<String> getHistory() {
        return history;
    }
    
    public void setHistory(List<String> history) {
        this.history = history;
    }
    
    public String getProvider() {
        return provider;
    }
    
    public void setProvider(String provider) {
        this.provider = provider;
    }
}

