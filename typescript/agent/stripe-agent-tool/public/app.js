class GalileoGizmosChat {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.loading = document.getElementById('loading');
        this.floatingGizmo = document.getElementById('floatingGizmo');
        this.themeToggle = document.getElementById('themeToggle');
        
        this.isProcessing = false;
        this.conversation = [];
        this.sessionId = null;
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        
        this.initializeTheme();
        this.initializeEventListeners();
        this.generateStars();
        this.initializeWebSocket();
    }

    initializeEventListeners() {
        // Form submission
        const inputForm = document.querySelector('.input-area');
        inputForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // Send message on button click (backup)
        this.sendBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // Theme toggle
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
        
        // Tool buttons
        document.querySelectorAll('.tool-button').forEach(btn => {
            btn.addEventListener('click', () => this.handleToolClick(btn.dataset.tool));
        });
        
        // Example buttons
        document.querySelectorAll('.example-item').forEach(item => {
            item.addEventListener('click', () => this.sendExampleMessage(item.dataset.example));
        });
        
        // Resource buttons
        document.querySelectorAll('.resource-button').forEach(btn => {
            btn.addEventListener('click', () => this.handleResourceClick(btn.dataset.resource));
        });
        
        // Floating gizmo easter egg
        this.floatingGizmo.addEventListener('click', () => this.showGizmoMessage());
        
        // Keyboard navigation for chat messages
        this.chatMessages.addEventListener('keydown', (e) => {
            if (e.key === 'Home') {
                this.chatMessages.scrollTop = 0;
            } else if (e.key === 'End') {
                this.scrollToBottom();
            }
        });
    }

    generateStars() {
        const stars = document.getElementById('stars');
        const numStars = 100;
        
        for (let i = 0; i < numStars; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            star.style.left = Math.random() * 100 + '%';
            star.style.top = Math.random() * 100 + '%';
            star.style.width = Math.random() * 3 + 1 + 'px';
            star.style.height = star.style.width;
            star.style.animationDelay = Math.random() * 3 + 's';
            stars.appendChild(star);
        }
    }

    initializeTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        this.updateThemeToggle();
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
        this.updateThemeToggle();
        
        // Announce theme change to screen readers
        const announcement = `Theme switched to ${this.currentTheme} mode`;
        this.announceToScreenReader(announcement);
    }

    updateThemeToggle() {
        const icon = this.themeToggle.querySelector('.theme-icon');
        const text = this.themeToggle.querySelector('.theme-text');
        
        if (this.currentTheme === 'dark') {
            icon.textContent = '🌙';
            text.textContent = 'Dark';
            this.themeToggle.setAttribute('aria-pressed', 'false');
            this.themeToggle.setAttribute('aria-label', 'Switch to light theme');
        } else {
            icon.textContent = '☀️';
            text.textContent = 'Light';
            this.themeToggle.setAttribute('aria-pressed', 'true');
            this.themeToggle.setAttribute('aria-label', 'Switch to dark theme');
        }
    }

    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.style.position = 'absolute';
        announcement.style.left = '-10000px';
        announcement.style.width = '1px';
        announcement.style.height = '1px';
        announcement.style.overflow = 'hidden';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        setTimeout(() => document.body.removeChild(announcement), 1000);
    }

    initializeWebSocket() {
        // For now, we'll use HTTP requests
        // In a real deployment, you might want WebSocket for real-time updates
        console.log('🚀 Galileo\'s Gizmos Chat Interface Initialized');
        
        // Hook end-of-session events for web runtime
        this.setupSessionCleanupHooks();
    }

    setupSessionCleanupHooks() {
        // Web: attach beforeunload event to flush buffered traces
        window.addEventListener('beforeunload', async (event) => {
            if (this.sessionId) {
                try {
                    // Send synchronous request to flush buffered traces
                    const response = await fetch('/api/session/flush', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ sessionId: this.sessionId }),
                        keepalive: true // Ensures request completes even if page is closing
                    });
                    console.log('📊 Session flushed on page unload');
                } catch (error) {
                    console.error('Failed to flush session on unload:', error);
                }
            }
        });

        // Also handle page visibility changes (mobile/tab switching)
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden' && this.sessionId) {
                this.flushSession();
            }
        });
    }

    async flushSession() {
        if (this.sessionId) {
            try {
                await fetch('/api/session/flush', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ sessionId: this.sessionId }),
                    keepalive: true
                });
                console.log('📊 Session flushed');
            } catch (error) {
                console.error('Failed to flush session:', error);
            }
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isProcessing) return;
        
        // Handle developer commands
        if (message === '!end') {
            this.addMessage('system', '📊 Developer command: Forcing buffered trace flush...');
            try {
                await this.flushSession();
                this.addMessage('system', '✅ Buffered traces flushed successfully');
            } catch (error) {
                this.addMessage('system', `❌ Error flushing buffered traces: ${error.message}`, null, true);
            }
            this.messageInput.value = '';
            return;
        }
        
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.setProcessing(true);
        
        try {
            const response = await this.callAgent(message);
            this.addMessage('assistant', response.message, response.data);
        } catch (error) {
            this.addDisconnectMessage(error.message);
        } finally {
            this.setProcessing(false);
        }
    }

    async callAgent(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    message,
                    sessionId: this.sessionId 
                })
            });

            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            // Store session ID for future requests
            if (data.sessionId) {
                this.sessionId = data.sessionId;
            }
            
            // Update connection status
            this.updateConnectionStatus(true);
            
            return data;
        } catch (error) {
            // Update connection status
            this.updateConnectionStatus(false);
            
            // Throw error to be handled by the caller
            throw new Error(`Backend Connection Failed: ${error.message}`);
        }
    }

    addMessage(role, content, data = null, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        messageDiv.setAttribute('role', role === 'system' ? 'status' : 'log');
        
        if (isError) {
            messageDiv.style.borderColor = 'var(--space-red)';
            messageDiv.style.background = 'rgba(239, 68, 68, 0.2)';
            messageDiv.setAttribute('aria-label', 'Error message');
        } else {
            const speaker = role === 'user' ? 'You' : role === 'system' ? 'System' : 'Gizmo';
            messageDiv.setAttribute('aria-label', `Message from ${speaker}`);
        }
        
        const timestamp = new Date().toLocaleTimeString();
        
        let messageHTML = `
            <div class="message-content">${this.formatMessage(content, role)}</div>
            <div class="message-meta" aria-label="Message timestamp">
                ${role === 'user' ? '🚀 You' : role === 'system' ? '🌟 System' : '🛸 Gizmo'} • ${timestamp}
            </div>
        `;
        
        if (data && data.toolsUsed && data.toolsUsed.length > 0) {
            messageHTML += `
                <div class="tool-usage" aria-label="Tools used in this response">
                    🔧 Tools Used: ${data.toolsUsed.join(', ')} • ⏱️ ${data.executionTime}ms
                </div>
            `;
        }
        
        messageDiv.innerHTML = messageHTML;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Announce new messages to screen readers
        if (role === 'assistant') {
            this.announceToScreenReader(`New message from Gizmo: ${content.substring(0, 100)}${content.length > 100 ? '...' : ''}`);
        }
        
        // Add to conversation history
        this.conversation.push({ role, content, timestamp: new Date(), data });
    }

    formatMessage(content, role) {
        if (role === 'assistant') {
            // Enhanced formatting for assistant messages
            let formatted = content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" style="color: var(--space-cyan); text-decoration: underline;">$1</a>')
                .replace(/✅/g, '<span style="color: var(--space-green);">✅</span>')
                .replace(/❌/g, '<span style="color: var(--space-red);">❌</span>')
                .replace(/🔗/g, '<span style="color: var(--space-cyan);">🔗</span>');
            
            return formatted;
        }
        
        return content;
    }

    sendExampleMessage(example) {
        this.messageInput.value = example;
        this.sendMessage();
    }

    handleToolClick(tool) {
        const prompts = {
            'payment-link': 'Create a payment link for a space product',
            'customer': 'Add a new customer to our space registry',
            'product': 'Create a new space product',
            'list-products': 'Show me our current space product catalog',
            'invoice': 'Create an invoice for a space mission'
        };
        
        const prompt = prompts[tool];
        if (prompt) {
            this.messageInput.value = prompt;
            this.messageInput.focus();
        }
    }
    
    handleResourceClick(resource) {
        if (resource === 'about') {
            this.addMessage('system', '🛸 Welcome to Galileo Gizmos! We\'re your premier destination for cutting-edge space commerce solutions. From interstellar payment processing to cosmic customer management, we\'ve got all the tools you need to launch your business into the stars! 🌟');
        } else if (resource === 'tutorial') {
            this.addMessage('system', '🎓 Ready to master space commerce? Our interactive tutorial will guide you through creating payment links, managing customers, and processing interstellar transactions. Type "Start tutorial" or ask me "How do I create a payment link?" to begin your cosmic journey! 🚀');
        }
    }

    showGizmoMessage() {
        const messages = [
            "🛸 *Beep boop* Gizmo here! Ready for space commerce!",
            "🌌 The cosmos are infinite, and so are your sales possibilities!",
            "🚀 *Whirrs excitedly* Another satisfied space customer!",
            "⭐ Did someone say interstellar transactions?",
            "🎯 *Calculates trajectory* Your business is going to the moon!"
        ];
        
        const randomMessage = messages[Math.floor(Math.random() * messages.length)];
        this.addMessage('system', randomMessage);
    }

    setProcessing(processing) {
        this.isProcessing = processing;
        this.sendBtn.disabled = processing;
        this.loading.classList.toggle('active', processing);
        
        if (processing) {
            this.sendBtn.textContent = '🔄 Processing...';
        } else {
            this.sendBtn.textContent = '🚀 Launch';
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    addDisconnectMessage(errorMessage) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message disconnect';
        messageDiv.style.background = 'rgba(239, 68, 68, 0.2)';
        messageDiv.style.borderColor = 'var(--space-red)';
        messageDiv.style.border = '2px solid var(--space-red)';
        messageDiv.style.textAlign = 'center';
        messageDiv.style.maxWidth = '90%';
        messageDiv.style.margin = '0 auto';
        
        const timestamp = new Date().toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="disconnect-content">
                <div style="font-size: 2em; margin-bottom: 10px;">🚨</div>
                <div style="font-weight: bold; color: var(--space-red); margin-bottom: 10px;">
                    BACKEND CONNECTION LOST
                </div>
                <div style="margin-bottom: 10px;">
                    ${errorMessage}
                </div>
                <div style="font-size: 0.9em; opacity: 0.8;">
                    🔧 Check that the backend server is running with: <code>npm run web</code>
                </div>
                <button 
                    class="retry-btn" 
                    onclick="location.reload()" 
                    style="
                        background: var(--space-red);
                        border: none;
                        color: white;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        margin-top: 15px;
                        font-family: 'Space Mono', monospace;
                    "
                >
                    🔄 Retry Connection
                </button>
            </div>
            <div class="message-meta">
                ⚠️ System Error • ${timestamp}
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    updateConnectionStatus(isConnected) {
        const statusIndicator = document.querySelector('.status-indicator');
        if (statusIndicator) {
            if (isConnected) {
                statusIndicator.style.background = 'rgba(16, 185, 129, 0.3)';
                statusIndicator.style.borderColor = 'var(--space-green)';
                statusIndicator.title = 'Connected to Galileo Gizmos Backend';
                statusIndicator.style.animation = 'pulse 2s infinite';
                
                // Enable input when connected
                this.messageInput.disabled = false;
                this.sendBtn.disabled = false;
                this.messageInput.placeholder = 'Ask me anything about your space commerce needs...';
            } else {
                statusIndicator.style.background = 'rgba(239, 68, 68, 0.3)';
                statusIndicator.style.borderColor = 'var(--space-red)';
                statusIndicator.title = 'Disconnected from Backend';
                statusIndicator.style.animation = 'pulse-error 1s infinite';
                
                // Disable input when disconnected
                this.messageInput.disabled = true;
                this.sendBtn.disabled = true;
                this.messageInput.placeholder = 'Backend connection required - please start the server...';
            }
        }
    }

    async checkBackendHealth() {
        try {
            const response = await fetch('/api/health');
            return response.ok;
        } catch (error) {
            return false;
        }
    }
}

// Initialize the chat interface
document.addEventListener('DOMContentLoaded', async () => {
    // Use the main chat interface (with backend connection checking)
    const chat = new GalileoGizmosChat();
    
    // Check backend health on startup
    const isBackendHealthy = await chat.checkBackendHealth();
    
    // Add startup message based on connection status
    setTimeout(() => {
        if (isBackendHealthy) {
            chat.addMessage('system', '🌟 Galileo\'s Gizmos systems online! All space commerce tools ready.');
            chat.updateConnectionStatus(true);
        } else {
            chat.addMessage('system', '⚠️ Backend connection unavailable. Please ensure the server is running with `npm run web`.');
            chat.updateConnectionStatus(false);
        }
    }, 1000);
});

// Add some cosmic ambiance
setInterval(() => {
    const colors = ['#06b6d4', '#6b46c1', '#10b981', '#f59e0b'];
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    document.documentElement.style.setProperty('--current-glow', randomColor);
}, 5000);
