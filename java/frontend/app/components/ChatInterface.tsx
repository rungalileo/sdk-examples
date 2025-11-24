'use client'

import { useState, useRef, useEffect } from 'react'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [provider, setProvider] = useState<'azure' | 'mistral'>('azure')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      // Build conversation history
      const history: string[] = []
      messages.forEach((msg) => {
        history.push(msg.content)
      })
      history.push(userMessage)

      const response = await fetch('http://localhost:8080/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          history: history,
          provider: provider,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response },
      ])
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.chatBox}>
        <div style={styles.header}>
          <h1 style={styles.title}>Galileo Chatbot</h1>
          <p style={styles.subtitle}>
            Powered by {provider === 'azure' ? 'Azure OpenAI' : 'Mistral AI'}
          </p>
        </div>

        <div style={styles.messagesContainer}>
          {messages.length === 0 && (
            <div style={styles.welcomeMessage}>
              <p>Hello! How can I help you today?</p>
            </div>
          )}
          {messages.map((message, index) => (
            <div
              key={index}
              style={{
                ...styles.message,
                ...(message.role === 'user'
                  ? styles.userMessage
                  : styles.assistantMessage),
              }}
            >
              <div style={styles.messageContent}>{message.content}</div>
            </div>
          ))}
          {isLoading && (
            <div style={{ ...styles.message, ...styles.assistantMessage }}>
              <div style={styles.messageContent}>
                <span style={styles.loading}>Thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div style={styles.inputContainer}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            style={styles.input}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            style={{
              ...styles.sendButton,
              ...(isLoading || !input.trim() ? styles.sendButtonDisabled : {}),
            }}
          >
            Send
          </button>
        </div>
        <div style={styles.toggleContainer}>
          <span style={styles.toggleLabel}>Azure</span>
          <label style={styles.toggleSwitch}>
            <input
              type="checkbox"
              checked={provider === 'mistral'}
              onChange={(e) => setProvider(e.target.checked ? 'mistral' : 'azure')}
              style={styles.toggleInput}
            />
            <span style={{
              ...styles.toggleSlider,
              backgroundColor: provider === 'mistral' ? '#667eea' : '#d1d5db',
            }}>
              <span style={{
                ...styles.toggleSliderButton,
                transform: provider === 'mistral' ? 'translateX(24px)' : 'translateX(2px)',
              }}></span>
            </span>
          </label>
          <span style={styles.toggleLabel}>Mistral</span>
        </div>
      </div>
    </div>
  )
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    width: '100%',
    maxWidth: '800px',
    height: '90vh',
    display: 'flex',
    flexDirection: 'column',
  },
  chatBox: {
    backgroundColor: 'white',
    borderRadius: '20px',
    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    overflow: 'hidden',
  },
  header: {
    padding: '24px',
    borderBottom: '1px solid #e5e7eb',
    backgroundColor: '#f9fafb',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#111827',
    margin: 0,
    marginBottom: '4px',
  },
  toggleContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    justifyContent: 'center',
    padding: '12px 20px',
    borderTop: '1px solid #e5e7eb',
    backgroundColor: '#f9fafb',
  },
  toggleLabel: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#6b7280',
  },
  toggleSwitch: {
    position: 'relative',
    display: 'inline-block',
    width: '50px',
    height: '26px',
    cursor: 'pointer',
  },
  toggleInput: {
    opacity: 0,
    width: 0,
    height: 0,
  },
  toggleSlider: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#d1d5db',
    transition: '0.3s',
    borderRadius: '26px',
    cursor: 'pointer',
  },
  toggleSliderButton: {
    position: 'absolute',
    content: '""',
    height: '20px',
    width: '20px',
    left: '3px',
    bottom: '3px',
    backgroundColor: 'white',
    transition: '0.3s',
    borderRadius: '50%',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
  },
  subtitle: {
    fontSize: '14px',
    color: '#6b7280',
  },
  messagesContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  welcomeMessage: {
    textAlign: 'center',
    color: '#6b7280',
    padding: '40px 20px',
    fontSize: '16px',
  },
  message: {
    maxWidth: '75%',
    padding: '12px 16px',
    borderRadius: '18px',
    wordWrap: 'break-word',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#667eea',
    color: 'white',
  },
  assistantMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#f3f4f6',
    color: '#111827',
  },
  messageContent: {
    fontSize: '15px',
    lineHeight: '1.5',
  },
  loading: {
    fontStyle: 'italic',
    color: '#6b7280',
  },
  inputContainer: {
    display: 'flex',
    padding: '20px',
    borderTop: '1px solid #e5e7eb',
    gap: '12px',
    backgroundColor: '#f9fafb',
  },
  input: {
    flex: 1,
    padding: '12px 16px',
    border: '1px solid #d1d5db',
    borderRadius: '12px',
    fontSize: '15px',
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  sendButton: {
    padding: '12px 24px',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '12px',
    fontSize: '15px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  sendButtonDisabled: {
    backgroundColor: '#d1d5db',
    cursor: 'not-allowed',
  },
}

