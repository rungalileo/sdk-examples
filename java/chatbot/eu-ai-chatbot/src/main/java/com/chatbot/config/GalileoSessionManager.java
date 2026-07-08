package com.chatbot.config;

import com.chatbot.service.GalileoService;
import jakarta.annotation.PreDestroy;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class GalileoSessionManager implements CommandLineRunner {
    
    @Autowired
    private GalileoService galileoService;
    
    @Override
    public void run(String... args) throws Exception {
        // Start a new session when the application starts
        // Note: This may be called multiple times by Spring DevTools auto-restart
        // The startSession() method has guards to prevent duplicate sessions
        System.out.println("GalileoSessionManager: Application starting, attempting to create session...");
        if (galileoService.isLoggingEnabled()) {
            String sessionId = galileoService.startSession();
            if (sessionId != null) {
                System.out.println("GalileoSessionManager: Session started successfully: " + sessionId);
            } else {
                System.out.println("GalileoSessionManager: Session creation returned null (may already exist)");
            }
        } else {
            System.out.println("GalileoSessionManager: Logging is disabled, skipping session creation");
        }
    }
    
    @PreDestroy
    public void onShutdown() {
        // Silently close the session on shutdown (no trace logging)
        // Sessions should be closed by user saying "im finished"
        if (galileoService.isLoggingEnabled()) {
            galileoService.closeSession();
        }
    }
}

