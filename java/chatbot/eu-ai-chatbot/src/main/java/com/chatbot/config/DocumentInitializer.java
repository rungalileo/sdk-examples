package com.chatbot.config;

import com.chatbot.service.DocumentService;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import java.io.ByteArrayInputStream;
import java.io.InputStream;

@Component
public class DocumentInitializer implements CommandLineRunner {
    
    @Autowired
    private DocumentService documentService;
    
    @Override
    public void run(String... args) throws Exception {
        // Load AI EU Act summary from PDF
        try {
            ClassPathResource resource = new ClassPathResource("ai_eu_act_summary.pdf");
            String aiEuActText = extractTextFromPdf(resource.getInputStream());
            if (aiEuActText != null && !aiEuActText.trim().isEmpty()) {
                documentService.addDocument(aiEuActText);
                System.out.println("Loaded AI EU Act summary from PDF into vector store");
            } else {
                System.err.println("Warning: PDF file is empty or could not be read");
            }
        } catch (Exception e) {
            System.err.println("Error loading AI EU Act PDF: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    private String extractTextFromPdf(InputStream inputStream) throws Exception {
        byte[] pdfBytes = inputStream.readAllBytes();
        try (ByteArrayInputStream bis = new ByteArrayInputStream(pdfBytes);
             PDDocument document = PDDocument.load(bis)) {
            PDFTextStripper stripper = new PDFTextStripper();
            return stripper.getText(document);
        }
    }
}

