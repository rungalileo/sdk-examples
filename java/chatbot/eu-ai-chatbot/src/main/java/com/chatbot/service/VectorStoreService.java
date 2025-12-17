package com.chatbot.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class VectorStoreService {
    
    @Autowired
    private EmbeddingService embeddingService;
    
    // In-memory vector store: document ID -> (embedding, text)
    private final Map<String, DocumentVector> vectors = new HashMap<>();
    
    public static class DocumentVector {
        private final String id;
        private final String text;
        private final List<Float> embedding;
        
        public DocumentVector(String id, String text, List<Float> embedding) {
            this.id = id;
            this.text = text;
            this.embedding = embedding;
        }
        
        public String getId() { return id; }
        public String getText() { return text; }
        public List<Float> getEmbedding() { return embedding; }
    }
    
    public void addDocument(String id, String text) {
        List<Float> embedding = embeddingService.getEmbedding(text);
        vectors.put(id, new DocumentVector(id, text, embedding));
    }
    
    public List<String> searchSimilar(String query, int topK) {
        if (vectors.isEmpty()) {
            return new ArrayList<>();
        }
        
        // Get embedding for query
        List<Float> queryEmbedding = embeddingService.getEmbedding(query);
        
        // Calculate cosine similarity for all documents
        List<SimilarityResult> results = new ArrayList<>();
        for (DocumentVector doc : vectors.values()) {
            double similarity = cosineSimilarity(queryEmbedding, doc.getEmbedding());
            results.add(new SimilarityResult(doc.getText(), similarity));
        }
        
        // Sort by similarity (descending) and return top K
        return results.stream()
                .sorted((a, b) -> Double.compare(b.similarity, a.similarity))
                .limit(topK)
                .map(r -> r.text)
                .collect(Collectors.toList());
    }
    
    private double cosineSimilarity(List<Float> vec1, List<Float> vec2) {
        if (vec1.size() != vec2.size()) {
            throw new IllegalArgumentException("Vectors must have the same dimension");
        }
        
        double dotProduct = 0.0;
        double norm1 = 0.0;
        double norm2 = 0.0;
        
        for (int i = 0; i < vec1.size(); i++) {
            dotProduct += vec1.get(i) * vec2.get(i);
            norm1 += vec1.get(i) * vec1.get(i);
            norm2 += vec2.get(i) * vec2.get(i);
        }
        
        return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
    }
    
    private static class SimilarityResult {
        final String text;
        final double similarity;
        
        SimilarityResult(String text, double similarity) {
            this.text = text;
            this.similarity = similarity;
        }
    }
    
    public void clear() {
        vectors.clear();
    }
    
    public int size() {
        return vectors.size();
    }
}

