import { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, Loader2, FileText, User as UserIcon, Bot } from 'lucide-react';
import { useLoaderData, useFetcher, Form } from 'react-router';
import { useForm, getFormProps, getInputProps } from '@conform-to/react';
import { parseWithZod } from '@conform-to/zod';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeSanitize from 'rehype-sanitize';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDateTime } from '@/lib/utils';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { handleFormSubmission } from '@/lib/utils/action-utils';
import { serverApi } from '@/lib/api.server';
import { chatMessageSchema } from '@/lib/schemas';
import type { ChatMessage, ChatRequest, User } from '@/lib/types';
import type { LoaderFunctionArgs, ActionFunctionArgs } from 'react-router';

interface ChatData {
  user: User;
}

// Loader function - handle authentication
export async function loader({ request }: LoaderFunctionArgs) {
  try {
    // Require authentication
    const user = await requireAuth(request);
    
    return {
      user
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

// Action function - handle message submissions
export async function action({ request }: ActionFunctionArgs) {
  const user = await requireAuth(request);
  const cookieHeader = request.headers.get('Cookie');
  const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
  
  if (!token) {
    throw new Response('Authentication required', { status: 401 });
  }

  return handleFormSubmission(request, chatMessageSchema, async (data) => {
    const chatRequest: ChatRequest = {
      message: data.message,
      context_department: user.department,
      max_results: 5
    };
    
    const response = await serverApi.askQuestion(chatRequest, token);
    
    // Return the response for the fetcher
    return Response.json({
      success: true,
      response: response.response,
      sources: response.sources,
      token_count: response.token_count
    });
  });
}

export default function Chat() {
  const { user } = useLoaderData<ChatData>();
  const fetcher = useFetcher();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [form, fields] = useForm({
    onValidate({ formData }) {
      return parseWithZod(formData, { schema: chatMessageSchema });
    }
  });
  
  const isLoading = fetcher.state === 'submitting';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      type: 'system',
      content: `Welcome to the Healthcare Support Portal Chat Assistant! I'm here to help you with medical information, protocols, and answer questions based on your available documents. How can I assist you today?`,
      timestamp: new Date().toISOString()
    };
    setMessages([welcomeMessage]);
  }, []);
  
  useEffect(() => {
    // Handle fetcher response
    if (fetcher.data && fetcher.state === 'idle') {
      if (fetcher.data.success) {
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: fetcher.data.response,
          timestamp: new Date().toISOString(),
          sources: fetcher.data.sources,
          token_count: fetcher.data.token_count
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: `I apologize, but I encountered an error while processing your request. Please try again later.`,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    }
  }, [fetcher.data, fetcher.state]);

  const handleSendMessage = (formData: FormData) => {
    const message = formData.get('message') as string;
    if (!message?.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    
    // Submit via fetcher
    fetcher.submit(formData, { method: 'post' });
    
    // Reset form
    form.reset();
  };

  const renderMessage = (message: ChatMessage) => {
    switch (message.type) {
      case 'user':
        return (
          <div className="flex justify-end mb-4">
            <div className="flex items-start space-x-2 max-w-xs lg:max-w-md">
              <div className="chat-bubble-user">
                {message.content}
              </div>
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center">
                  <UserIcon className="h-4 w-4 text-white" />
                </div>
              </div>
            </div>
          </div>
        );

      case 'assistant':
        return (
          <div className="flex justify-start mb-4">
            <div className="flex items-start space-x-2 max-w-xs lg:max-w-md">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-green-600 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-white" />
                </div>
              </div>
              <div className="space-y-2">
                <div className="chat-bubble-assistant markdown-content">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeSanitize, rehypeHighlight]}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
                {message.sources && message.sources.length > 0 && (
                  <div className="text-xs text-gray-500">
                    <div className="font-medium mb-1">Sources:</div>
                    <div className="space-y-1">
                      {message.sources.slice(0, 3).map((source, idx) => (
                        <div key={idx} className="flex items-center space-x-1">
                          <FileText className="h-3 w-3" />
                          <span className="truncate">{source.title}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {message.token_count && (
                  <div className="text-xs text-gray-400">
                    {message.token_count} tokens used
                  </div>
                )}
              </div>
            </div>
          </div>
        );

      case 'system':
        return (
          <div className="flex justify-center mb-4">
            <div className="chat-bubble-system">
              {message.content}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const suggestedQuestions = [
    "What are the latest diabetes management protocols?",
    "Show me emergency procedures for cardiac events",
    "What are the medication guidelines for pediatric patients?",
    "How do I handle patient data privacy?",
    "What are the current vaccination schedules?"
  ];

  return (
    <div className="h-[calc(100vh-12rem)] flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <div className="md:flex md:items-center md:justify-between">
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
              Chat Assistant
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Get AI-powered assistance with medical information and protocols
            </p>
          </div>
          <div className="mt-4 flex md:ml-4 md:mt-0">
            <Badge variant={user.role as any}>
              Context: {user.department}
            </Badge>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <Card className="flex-1 flex flex-col">
        <CardHeader className="pb-4">
          <div className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5 text-healthcare-blue" />
            <CardTitle className="text-lg">Healthcare AI Assistant</CardTitle>
          </div>
          <CardDescription>
            Ask questions about medical protocols, patient care, or search through available documents
          </CardDescription>
        </CardHeader>

        <CardContent className="flex-1 flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto mb-4 space-y-4 min-h-0">
            {messages.length === 1 && (
              <div className="space-y-4">
                {renderMessage(messages[0])}
                <div className="border-t pt-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Try asking about:
                  </p>
                  <div className="space-y-2">
                    {suggestedQuestions.map((question, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          const messageInput = document.querySelector('input[name="message"]') as HTMLInputElement;
                          if (messageInput) {
                            messageInput.value = question;
                            messageInput.focus();
                          }
                        }}
                        className="block w-full text-left p-2 text-sm text-gray-600 hover:bg-gray-50 rounded border"
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
            
            {messages.length > 1 && messages.slice(1).map(renderMessage)}
            
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="flex items-start space-x-2">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 rounded-full bg-green-600 flex items-center justify-center">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                  </div>
                  <div className="chat-bubble-assistant">
                    <div className="flex items-center space-x-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Thinking...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <fetcher.Form 
            {...getFormProps(form)}
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              handleSendMessage(formData);
            }}
            className="flex space-x-2"
          >
            <Input
              {...getInputProps(fields.message, { type: 'text' })}
              placeholder="Ask a question about medical protocols, patient care, or search documents..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button 
              type="submit" 
              disabled={isLoading}
              variant="healthcare"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </fetcher.Form>
        </CardContent>
      </Card>

      {/* Info Panel */}
      <Card className="mt-4">
        <CardContent className="p-4">
          <div className="text-sm text-gray-600">
            <p className="font-medium mb-1">How it works:</p>
            <ul className="text-xs space-y-1 text-gray-500">
              <li>• Ask questions in natural language</li>
              <li>• The AI searches through authorized documents in your department</li>
              <li>• Responses are tailored to your role as a {user.role}</li>
              <li>• Sources are provided when available</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}