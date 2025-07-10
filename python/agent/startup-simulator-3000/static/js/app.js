// Startum Sim 3000 - 8-bit Frontend
class StartumSim {
    constructor() {
        this.currentScreen = 'start-screen';
        this.selectedMode = null;
        this.inputs = {
            industry: '',
            audience: '',
            randomWord: ''
        };
        this.loadingSteps = {
            silly: [
                '► Fetching HackerNews trends...',
                '► Analyzing startup ecosystem...',
                '► Generating silly pitch...',
                '► Finalizing absurd results...'
            ],
            serious: [
                '► Fetching market news...',
                '► Analyzing competitive landscape...',
                '► Generating business plan...',
                '► Finalizing professional pitch...'
            ]
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.initTheme();
        this.playStartupSound();
    }
    
    bindEvents() {
        // Start button
        document.getElementById('start-button').addEventListener('click', () => {
            this.showScreen('mode-screen');
            this.playSound('beep');
        });
        
        // Mode selection
        document.getElementById('silly-mode').addEventListener('click', () => {
            this.selectMode('silly');
        });
        
        document.getElementById('serious-mode').addEventListener('click', () => {
            this.selectMode('serious');
        });
        
        // Generate button
        document.getElementById('generate-btn').addEventListener('click', () => {
            this.handleGenerate();
        });
        
        // New game button
        document.getElementById('new-game-btn').addEventListener('click', () => {
            this.resetGame();
        });
        
        // Copy button
        document.getElementById('copy-btn').addEventListener('click', () => {
            this.copyResult();
        });
        
        // Retry button
        document.getElementById('retry-btn').addEventListener('click', () => {
            this.showScreen('input-screen');
        });
        
        // Theme toggle button
        document.getElementById('theme-toggle-btn').addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            this.handleKeypress(e);
        });
        
        // Input validation
        const inputs = ['industry', 'audience', 'randomWord'];
        inputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            input.addEventListener('input', (e) => {
                this.inputs[inputId] = e.target.value.trim();
                this.updateGenerateButton();
                this.playSound('type');
            });
            
            input.addEventListener('focus', () => {
                this.playSound('focus');
            });
        });
    }
    
    handleKeypress(e) {
        switch(e.key) {
            case 'Enter':
                if (this.currentScreen === 'start-screen') {
                    this.showScreen('mode-screen');
                    this.playSound('beep');
                } else if (this.currentScreen === 'input-screen') {
                    this.handleGenerate();
                }
                break;
            case 'Escape':
                if (this.currentScreen !== 'start-screen') {
                    this.resetGame();
                }
                break;
            case 't':
            case 'T':
                // Toggle theme with 't' key
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.toggleTheme();
                }
                break;
        }
    }
    
    selectMode(mode) {
        this.selectedMode = mode;
        
        // Update visual selection
        document.querySelectorAll('.mode-option').forEach(option => {
            option.classList.remove('selected');
        });
        document.getElementById(`${mode}-mode`).classList.add('selected');
        
        // Update the generator title and mode status
        const title = mode === 'serious' ? 'PROFESSIONAL STARTUP GENERATOR v3.0' : 'SILLY STARTUP GENERATOR v3.0';
        document.getElementById('generator-title').textContent = title;
        
        // Update mode status
        const modeStatus = mode === 'serious' ? 'MODE: PROFESSIONAL' : 'MODE: SILLY';
        document.querySelector('.stats span').textContent = modeStatus;
        
        // Go to input screen after a brief delay
        setTimeout(() => {
            this.showScreen('input-screen');
            this.playSound('beep');
        }, 500);
    }

    showScreen(screenId) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        // Show target screen
        document.getElementById(screenId).classList.add('active');
        this.currentScreen = screenId;
        
        // Focus first input if on input screen
        if (screenId === 'input-screen') {
            setTimeout(() => {
                document.getElementById('industry').focus();
            }, 100);
        }
    }
    
    updateGenerateButton() {
        const btn = document.getElementById('generate-btn');
        const allFilled = this.inputs.industry && this.inputs.audience && this.inputs.randomWord;
        
        btn.disabled = !allFilled;
        btn.style.opacity = allFilled ? '1' : '0.5';
    }
    
    async handleGenerate() {
        if (!this.inputs.industry || !this.inputs.audience || !this.inputs.randomWord) {
            this.showError('Please fill in all fields!');
            return;
        }
        
        this.showScreen('loading-screen');
        this.playSound('power-up');
        this.startLoadingAnimation();
        
        try {
            const requestData = {
                ...this.inputs,
                mode: this.selectedMode || 'silly'
            };
            
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Unknown error occurred');
            }
            
            // Ensure loading animation runs for at least 3 seconds
            await this.waitForLoadingComplete();
            
            this.showResult(data.result);
            this.playSound('success');
            
        } catch (error) {
            console.error('Error:', error);
            this.showError(error.message || 'Something went wrong. Please try again.');
            this.playSound('error');
        }
    }
    
    startLoadingAnimation() {
        const progressBar = document.querySelector('.loading-progress');
        const steps = document.querySelectorAll('.loading-step');
        
        // Update loading steps based on mode
        const currentSteps = this.loadingSteps[this.selectedMode || 'silly'];
        steps.forEach((step, index) => {
            if (currentSteps[index]) {
                step.textContent = currentSteps[index];
            }
        });
        
        // Reset animation
        progressBar.style.width = '0%';
        steps.forEach(step => step.classList.remove('active'));
        
        let currentStep = 0;
        const stepDuration = 750; // 3 seconds / 4 steps
        
        const animateStep = () => {
            if (currentStep < steps.length) {
                // Deactivate previous step
                if (currentStep > 0) {
                    steps[currentStep - 1].classList.remove('active');
                }
                
                // Activate current step
                steps[currentStep].classList.add('active');
                currentStep++;
                
                setTimeout(animateStep, stepDuration);
            }
        };
        
        animateStep();
        
        // Animate progress bar
        setTimeout(() => {
            progressBar.style.transition = 'width 3s ease-in-out';
            progressBar.style.width = '100%';
        }, 100);
    }
    
    waitForLoadingComplete() {
        return new Promise(resolve => {
            setTimeout(resolve, 3000); // Minimum 3 seconds loading
        });
    }
    
    showResult(result) {
        document.getElementById('result-text').textContent = result;
        this.showScreen('result-screen');
    }
    
    showError(message) {
        document.getElementById('error-message').textContent = message;
        this.showScreen('error-screen');
    }
    
    async copyResult() {
        try {
            const resultText = document.getElementById('result-text').textContent;
            await navigator.clipboard.writeText(resultText);
            
            // Show feedback
            const btn = document.getElementById('copy-btn');
            const originalText = btn.textContent;
            btn.textContent = 'COPIED!';
            btn.style.background = 'linear-gradient(45deg, #00aa00, #00ff00)';
            
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = 'linear-gradient(45deg, #666666, #999999)';
            }, 2000);
            
            this.playSound('beep');
        } catch (error) {
            console.error('Failed to copy text:', error);
            this.playSound('error');
        }
    }
    
    resetGame() {
        this.inputs = {
            industry: '',
            audience: '',
            randomWord: ''
        };
        this.selectedMode = null;
        
        // Clear inputs
        document.getElementById('industry').value = '';
        document.getElementById('audience').value = '';
        document.getElementById('randomWord').value = '';
        
        // Clear mode selection
        document.querySelectorAll('.mode-option').forEach(option => {
            option.classList.remove('selected');
        });
        
        // Reset mode status
        document.querySelector('.stats span').textContent = 'MODE: READY';
        
        this.updateGenerateButton();
        this.showScreen('mode-screen');
        this.playSound('beep');
    }
    
    // Sound effects using Web Audio API
    playSound(type) {
        if (!this.audioContext) {
            try {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            } catch (e) {
                return; // Audio not supported
            }
        }
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        // Different sound patterns for different actions
        switch(type) {
            case 'beep':
                oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime);
                oscillator.frequency.exponentialRampToValueAtTime(400, this.audioContext.currentTime + 0.1);
                gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1);
                oscillator.start();
                oscillator.stop(this.audioContext.currentTime + 0.1);
                break;
                
            case 'type':
                oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime);
                gainNode.gain.setValueAtTime(0.05, this.audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.05);
                oscillator.start();
                oscillator.stop(this.audioContext.currentTime + 0.05);
                break;
                
            case 'focus':
                oscillator.frequency.setValueAtTime(1000, this.audioContext.currentTime);
                oscillator.frequency.exponentialRampToValueAtTime(1200, this.audioContext.currentTime + 0.05);
                gainNode.gain.setValueAtTime(0.08, this.audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.05);
                oscillator.start();
                oscillator.stop(this.audioContext.currentTime + 0.05);
                break;
                
            case 'power-up':
                oscillator.frequency.setValueAtTime(200, this.audioContext.currentTime);
                oscillator.frequency.exponentialRampToValueAtTime(800, this.audioContext.currentTime + 0.3);
                gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
                oscillator.start();
                oscillator.stop(this.audioContext.currentTime + 0.3);
                break;
                
            case 'success':
                // Play a success melody
                this.playSuccessMelody();
                return;
                
            case 'error':
                oscillator.frequency.setValueAtTime(150, this.audioContext.currentTime);
                oscillator.frequency.exponentialRampToValueAtTime(100, this.audioContext.currentTime + 0.3);
                gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
                oscillator.start();
                oscillator.stop(this.audioContext.currentTime + 0.3);
                break;
        }
    }
    
    playSuccessMelody() {
        const notes = [440, 554, 659, 880]; // A4, C#5, E5, A5
        const duration = 0.15;
        
        notes.forEach((freq, index) => {
            setTimeout(() => {
                const osc = this.audioContext.createOscillator();
                const gain = this.audioContext.createGain();
                
                osc.connect(gain);
                gain.connect(this.audioContext.destination);
                
                osc.frequency.setValueAtTime(freq, this.audioContext.currentTime);
                gain.gain.setValueAtTime(0.1, this.audioContext.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
                
                osc.start();
                osc.stop(this.audioContext.currentTime + duration);
            }, index * duration * 1000);
        });
    }
    
    playStartupSound() {
        // Play startup sound after a brief delay
        setTimeout(() => {
            this.playSound('power-up');
        }, 500);
    }
    
    initTheme() {
        // Get saved theme or default to dark
        const savedTheme = localStorage.getItem('startup-sim-theme') || 'dark';
        this.setTheme(savedTheme);
    }
    
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
        this.playSound('beep');
    }
    
    setTheme(theme) {
        // Update document attribute
        if (theme === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
        
        // Update theme toggle button icon
        const themeIcon = document.querySelector('.theme-icon');
        if (themeIcon) {
            themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
        }
        
        // Save preference
        localStorage.setItem('startup-sim-theme', theme);
        
        console.log(`Theme switched to: ${theme}`);
    }
}

// Initialize the game when page loads
document.addEventListener('DOMContentLoaded', () => {
    new StartumSim();
});

// Add some fun easter eggs
let konamiCode = [];
const konamiSequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'KeyB', 'KeyA'];

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.code);
    if (konamiCode.length > konamiSequence.length) {
        konamiCode.shift();
    }
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
        // Easter egg activated!
        document.body.style.filter = 'hue-rotate(180deg)';
        setTimeout(() => {
            document.body.style.filter = '';
        }, 3000);
    }
});
