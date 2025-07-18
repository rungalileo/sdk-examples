import express from 'express';
import path from 'path';
import cors from 'cors';
import { StripeAgent } from './agents/StripeAgent';
import { env } from './config/environment';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// Store active sessions (web sessionId -> agent instance)
const activeSessions = new Map<string, StripeAgent>();

// API Routes
app.post('/api/chat', async (req, res) => {
    try {
        const { message, sessionId } = req.body;
        
        if (!message || typeof message !== 'string') {
            return res.status(400).json({
                success: false,
                message: 'Invalid message format'
            });
        }

        // Start new session if needed
        let currentSessionId = sessionId;
        let agent: StripeAgent;
        
        if (!currentSessionId || !activeSessions.has(currentSessionId)) {
            currentSessionId = `web-session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
            agent = new StripeAgent();
            await agent.init();
            await agent.startGalileoSession('Galileo Gizmos Web Chat Session');
            activeSessions.set(currentSessionId, agent);
        } else {
            agent = activeSessions.get(currentSessionId)!;
        }

        // Process the message
        const response = await agent.processMessage(message);
        
        // Log to console for debugging
        console.log(`[${new Date().toISOString()}] User: ${message}`);
        console.log(`[${new Date().toISOString()}] Gizmo: ${response.message}`);
        if (response.data?.toolsUsed && response.data.toolsUsed.length > 0) {
            console.log(`[${new Date().toISOString()}] Tools: ${response.data.toolsUsed.join(', ')}`);
        }

        res.json({
            ...response,
            sessionId: currentSessionId
        });
    } catch (error) {
        console.error('Chat API error:', error);
        res.status(500).json({
            success: false,
            message: 'Houston, we have a problem! Please try again.',
            error: error instanceof Error ? error.message : 'Unknown error'
        });
    }
});

// Get conversation history
app.get('/api/conversation/:sessionId', async (req, res) => {
    try {
        const { sessionId } = req.params;
        const agent = activeSessions.get(sessionId);
        
        if (!agent) {
            return res.status(404).json({
                success: false,
                message: 'Session not found'
            });
        }
        
        const conversationHistory = agent.getConversationHistory();
        res.json({
            success: true,
            conversation: conversationHistory
        });
    } catch (error) {
        console.error('Conversation API error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to retrieve conversation history'
        });
    }
});

// Clear conversation history
app.delete('/api/conversation/:sessionId', async (req, res) => {
    try {
        const { sessionId } = req.params;
        const agent = activeSessions.get(sessionId);
        
        if (!agent) {
            return res.status(404).json({
                success: false,
                message: 'Session not found'
            });
        }
        
        agent.clearConversationHistory();
        res.json({
            success: true,
            message: 'Conversation history cleared'
        });
    } catch (error) {
        console.error('Clear conversation API error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to clear conversation history'
        });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'Galileo Gizmos Space Commerce Assistant',
        version: '1.0.0'
    });
});

// Get agent capabilities
app.get('/api/capabilities', (req, res) => {
    res.json({
        success: true,
        capabilities: {
            tools: [
                'create_payment_link',
                'create_customer', 
                'create_product',
                'create_price',
                'list_customers',
                'list_products',
                'create_invoice',
                'finalize_invoice'
            ],
            features: [
                'Natural language processing',
                'Stripe API integration',
                'Galileo monitoring',
                'Space-themed responses',
                'Conversation history',
                'Real-time tool usage tracking'
            ]
        }
    });
});

// Serve the frontend
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/index.html'));
});

// Handle session cleanup on shutdown
process.on('SIGINT', async () => {
    console.log('\n🚀 Shutting down Galileo Gizmos server...');
    
    // Conclude all active sessions
    for (const [webSessionId, agent] of activeSessions) {
        try {
            // Log final conversation
            await agent.logConversationToGalileo();
            await agent.concludeGalileoSession();
            console.log(`✅ Session ${webSessionId} concluded successfully`);
        } catch (error) {
            console.error(`❌ Error concluding session ${webSessionId}:`, error);
        }
    }
    
    console.log('🌟 Galileo Gizmos server shutdown complete');
    process.exit(0);
});

// Start the server
app.listen(PORT, () => {
    console.log('🚀 Galileo\'s Gizmos Space Commerce HQ is online!');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(`🌟 Server running on http://localhost:${PORT}`);
    console.log(`📊 Galileo Project: ${env.galileo.projectName}`);
    console.log(`🛸 Ready to process interstellar commerce requests!`);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
});

// Export for testing
export { app };
