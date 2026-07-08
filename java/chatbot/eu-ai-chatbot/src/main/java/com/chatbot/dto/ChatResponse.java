package com.chatbot.dto;

public class ChatResponse {
    private String response;
    
    public ChatResponse(String response) {
        this.response = response;
    }
    
    public String getResponse() {
        return response;
    }
    
    public void setResponse(String response) {
        this.response = response;
    }
}

