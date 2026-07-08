package com.chatbot.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
public class DocumentService {
    
    @Autowired
    private VectorStoreService vectorStoreService;
    
    public String addDocument(String text) {
        String id = UUID.randomUUID().toString();
        vectorStoreService.addDocument(id, text);
        return id;
    }
    
    public List<String> retrieveRelevantContext(String query, int topK) {
        try {
            return vectorStoreService.searchSimilar(query, topK);
        } catch (Exception e) {
            // If RAG retrieval fails (e.g., rate limiting on embeddings), return empty list
            // This allows the chat to continue without RAG context
            System.err.println("⚠️ Error retrieving RAG context: " + e.getMessage());
            System.err.println("   Chat will continue without RAG context");
            return java.util.Collections.emptyList();
        }
    }
    
    public void clearDocuments() {
        vectorStoreService.clear();
    }
    
    public int getDocumentCount() {
        return vectorStoreService.size();
    }
}

