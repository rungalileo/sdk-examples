package com.chatbot.config;

import com.chatbot.service.DocumentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class DocumentInitializer implements CommandLineRunner {
    
    @Autowired
    private DocumentService documentService;
    
    @Override
    public void run(String... args) throws Exception {
        System.out.println("📚 Initializing vector store with sample documents...");
        
        // Sample documents about AI and machine learning
        String[] sampleDocuments = {
            "Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. " +
            "These processes include learning (the acquisition of information and rules for using the information), reasoning (using rules to reach approximate or definite conclusions), and self-correction. " +
            "AI can be categorized as either weak or strong. Weak AI, also known as narrow AI, is designed to perform a narrow task (e.g., facial recognition). " +
            "Strong AI, also known as artificial general intelligence (AGI), can understand, learn, and apply knowledge in ways indistinguishable from humans.",
            
            "Machine Learning (ML) is a subset of AI that focuses on the development of algorithms that can learn from and make predictions or decisions based on data. " +
            "There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning. " +
            "Supervised learning uses labeled training data to learn the relationship between input and output. " +
            "Unsupervised learning finds hidden patterns in unlabeled data. Reinforcement learning learns through trial and error using feedback from actions and experiences.",
            
            "Deep Learning is a subset of machine learning that uses neural networks with multiple layers (hence 'deep') to model complex patterns in data. " +
            "Deep learning has revolutionized computer vision, natural language processing, and speech recognition. " +
            "Popular deep learning architectures include Convolutional Neural Networks (CNNs) for image processing, Recurrent Neural Networks (RNNs) for sequential data, " +
            "and Transformers for natural language understanding. The success of deep learning is largely due to the availability of large datasets and powerful GPUs for training.",
            
            "Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret, and manipulate human language. " +
            "NLP draws from many disciplines, including computer science and computational linguistics. " +
            "Common NLP tasks include text classification, named entity recognition, sentiment analysis, machine translation, and question answering. " +
            "Modern NLP heavily relies on transformer-based models like BERT, GPT, and T5, which have achieved remarkable performance on various language understanding tasks.",
            
            "Large Language Models (LLMs) are neural networks trained on vast amounts of text data to understand and generate human-like text. " +
            "Examples include GPT-4, Claude, and LLaMA. These models can perform a wide range of tasks including text generation, summarization, translation, and question answering. " +
            "LLMs use the transformer architecture and are trained using unsupervised learning on diverse internet text. " +
            "The emergence of LLMs has led to new applications in conversational AI, content creation, and code generation.",
            
            "Retrieval-Augmented Generation (RAG) is a technique that combines information retrieval with text generation to improve the accuracy and relevance of AI responses. " +
            "In RAG systems, relevant documents are first retrieved from a knowledge base using semantic search, and then these documents are used as context for generating responses. " +
            "This approach helps reduce hallucinations and provides more factual, grounded answers. RAG systems typically use vector databases to store and retrieve document embeddings efficiently. " +
            "Common components include an embedding model, a vector store (like Chroma or Pinecone), and a language model for generation.",
            
            "Vector embeddings are numerical representations of text that capture semantic meaning. They convert words, sentences, or documents into dense vectors in high-dimensional space. " +
            "Similar concepts are positioned close together in this vector space, enabling semantic search and similarity comparisons. " +
            "Embedding models like OpenAI's text-embedding-ada-002 or sentence-transformers are commonly used to create these vector representations. " +
            "The quality of embeddings directly impacts the performance of RAG systems and other semantic search applications.",
            
            "Prompt engineering is the practice of designing and optimizing input prompts to get better responses from language models. " +
            "Effective prompts provide clear instructions, relevant context, and examples of desired outputs. " +
            "Techniques include few-shot learning (providing examples), chain-of-thought prompting (encouraging step-by-step reasoning), and role-playing (assigning a specific persona to the model). " +
            "Well-crafted prompts can significantly improve model performance without requiring additional training or fine-tuning.",
            
            "AI Safety and Ethics are critical considerations in the development and deployment of AI systems. " +
            "Key concerns include bias and fairness, transparency and explainability, privacy and data protection, and accountability. " +
            "AI systems can inadvertently perpetuate or amplify societal biases present in training data. " +
            "Responsible AI practices involve rigorous testing, monitoring for unintended consequences, and ensuring that AI systems align with human values and societal norms. " +
            "Organizations should implement AI governance frameworks to ensure ethical development and deployment of AI technologies."
        };
        
        // Add each document chunk to the vector store
        int chunkCount = 0;
        for (String document : sampleDocuments) {
            try {
                documentService.addDocument(document);
                chunkCount++;
                System.out.println("  ✓ Added chunk " + chunkCount + " (" + document.substring(0, Math.min(50, document.length())) + "...)");
            } catch (Exception e) {
                System.err.println("  ✗ Error adding chunk: " + e.getMessage());
            }
        }
        
        System.out.println("✅ Vector store initialized with " + chunkCount + " document chunks");
        System.out.println("📊 Total documents in store: " + documentService.getDocumentCount());
    }
}

