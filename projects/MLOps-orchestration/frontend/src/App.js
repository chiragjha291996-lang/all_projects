import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import ReactMarkdown from 'react-markdown';
import { Send, Upload, Bot, User, FileText, Loader2 } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'agent',
      content: "👋 Hello! I'm your Conversational MLOps Agent. I can help you with:\n\n• Setting up new ML pipelines\n• Registering and running Prefect flows\n• Tracking experiments with MLflow\n• Managing model versions\n• Uploading files to Google Cloud Storage\n\nWhat would you like to do today?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'text/x-python': ['.py']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setUploadedFile(acceptedFiles[0]);
      }
    }
  });

  const sendMessage = async () => {
    if (!inputMessage.trim() && !uploadedFile) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage || `Uploaded file: ${uploadedFile?.name}`,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      let response;
      
      if (uploadedFile) {
        // Send message with file
        const formData = new FormData();
        formData.append('message', inputMessage || 'Please process this file');
        formData.append('file', uploadedFile);
        
        response = await axios.post(`${API_BASE_URL}/chat-with-file`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      } else {
        // Send text message only
        response = await axios.post(`${API_BASE_URL}/chat`, {
          message: inputMessage
        });
      }

      const agentMessage = {
        id: Date.now() + 1,
        type: 'agent',
        content: response.data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, agentMessage]);
      setUploadedFile(null);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'agent',
        content: `❌ Sorry, I encountered an error: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        type: 'agent',
        content: "👋 Hello! I'm your Conversational MLOps Agent. How can I help you today?",
        timestamp: new Date()
      }
    ]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Bot className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Conversational MLOps Agent</h1>
                <p className="text-sm text-gray-600">Powered by LangGraph, Prefect & MLflow</p>
              </div>
            </div>
            <button
              onClick={clearChat}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Clear Chat
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* File Upload Area */}
        <div className="mb-6">
          <div
            {...getRootProps()}
            className={`file-upload-area rounded-lg p-6 text-center cursor-pointer ${
              isDragActive ? 'dragover' : ''
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
            {uploadedFile ? (
              <div className="text-green-600">
                <FileText className="h-6 w-6 mx-auto mb-2" />
                <p className="font-medium">{uploadedFile.name}</p>
                <p className="text-sm">Click to change file</p>
              </div>
            ) : (
              <div>
                <p className="text-gray-600 mb-1">
                  {isDragActive ? 'Drop your Python file here' : 'Drag & drop a Python file here, or click to select'}
                </p>
                <p className="text-sm text-gray-500">Only .py files are supported</p>
              </div>
            )}
          </div>
        </div>

        {/* Chat Messages */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="chat-container p-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex mb-4 ${
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`flex items-start space-x-3 message-bubble rounded-lg p-4 ${
                    message.type === 'user' ? 'user-message' : 'agent-message'
                  }`}
                >
                  {message.type === 'agent' ? (
                    <Bot className="h-5 w-5 mt-0.5 text-blue-600" />
                  ) : (
                    <User className="h-5 w-5 mt-0.5 text-white" />
                  )}
                  <div className="flex-1">
                    <ReactMarkdown className="prose prose-sm max-w-none">
                      {message.content}
                    </ReactMarkdown>
                    <p className="text-xs opacity-70 mt-2">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="flex items-start space-x-3 message-bubble rounded-lg p-4 agent-message">
                  <Bot className="h-5 w-5 mt-0.5 text-blue-600" />
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t p-4">
            <div className="flex space-x-3">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
                className="flex-1 resize-none border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={2}
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || (!inputMessage.trim() && !uploadedFile)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <Send className="h-4 w-4" />
                <span>Send</span>
              </button>
            </div>
          </div>
        </div>

        {/* Quick Commands */}
        <div className="mt-6 bg-white rounded-lg shadow-sm border p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Commands</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {[
              "Set up a new churn model pipeline",
              "Upload my pipeline script",
              "Run my pipeline",
              "What was the accuracy?",
              "Promote this model to staging",
              "List all pipelines"
            ].map((command) => (
              <button
                key={command}
                onClick={() => setInputMessage(command)}
                className="text-left text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 p-2 rounded border border-gray-200"
              >
                {command}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;


