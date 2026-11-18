import React, { useState, useEffect, useRef } from 'react'
import { hotelApi } from '../services/api'
import { Send, Loader2, Bot, User, X, MessageSquare } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [typing, setTyping] = useState(false)
  const [sessionId] = useState(() => 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9))
  const messagesEndRef = useRef(null)

  useEffect(() => {
    scrollToBottom()
  }, [messages, typing])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSend = async (e) => {
    if (e) e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input, timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])
    const currentInput = input
    setInput('')
    setLoading(true)
    setTyping(true)

    try {
      const response = await hotelApi.chat(currentInput, sessionId)
      
      // Show typing indicator for 2 seconds
      await new Promise(resolve => setTimeout(resolve, 2000))
      setTyping(false)
      
      const botMessage = { 
        role: 'assistant', 
        content: response.data.response || response.data.message || "I apologize, but I couldn't process that request.", 
        timestamp: new Date(),
        session_id: sessionId
      }
      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Chat error:', error)
      setTyping(false)
      const errorMessage = { 
        role: 'assistant', 
        content: "I'm sorry, I'm having trouble connecting. Please try again in a moment.", 
        timestamp: new Date() 
      }
      setMessages(prev => [...prev, errorMessage])
      toast.error('Failed to send message')
    } finally {
      setLoading(false)
    }
  }

  const copyMessage = (content) => {
    navigator.clipboard.writeText(content)
    toast.success('Copied to clipboard')
  }

  const toggleChat = () => {
    setIsOpen(!isOpen)
  }

  const suggestions = [
    'What are the check-in times?',
    'What room types are available?',
    'What facilities does the hotel have?',
    'Are pets allowed?',
  ]

  // Render a single message
  const renderMessage = (message, index) => {
    const isUser = message.role === 'user'
    return (
      <div key={index} className={"flex " + (isUser ? 'justify-end' : 'justify-start')}>
        <div className={"max-w-[85%] " + (isUser ? 'order-2' : 'order-1')}>
          {!isUser && (
            <div className="flex items-start space-x-2 mb-1">
              <div className="w-7 h-7 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="h-3.5 w-3.5 text-primary-600" />
              </div>
            </div>
          )}
          <div className={"flex flex-col " + (isUser ? 'items-end' : 'items-start') + " space-y-1"}>
            <div className={"px-4 py-2.5 rounded-2xl " + (
              isUser
                ? 'bg-primary-600 text-white rounded-br-md'
                : 'bg-gray-50 text-gray-900 border border-gray-100 rounded-bl-md shadow-sm'
            )}>
              <p className="whitespace-pre-wrap text-sm">{message.content}</p>
            </div>
            <div className="flex items-center space-x-1.5 mt-1">
              <span className={"text-xs " + (isUser ? 'text-primary-400' : 'text-gray-400')}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              {!isUser && (
                <button
                  onClick={() => copyMessage(message.content)}
                  className="p-1 text-gray-400 hover:text-primary-600 transition-colors"
                  title="Copy"
                >
                  <Send className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Render typing indicator
  const renderTyping = () => {
    return (
      <div key="typing" className="flex justify-start">
        <div className="max-w-[85%] order-1">
          <div className="flex items-start space-x-2 mb-1">
            <div className="w-7 h-7 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
              <Bot className="h-3.5 w-3.5 text-primary-600" />
            </div>
          </div>
          <div className="flex flex-col items-start space-y-1">
            <div className="px-4 py-2.5 bg-gray-50 text-gray-900 border border-gray-100 rounded-2xl rounded-bl-md shadow-sm">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}} />
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}} />
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}} />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!isOpen) {
    return (
      <button
        onClick={toggleChat}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-primary-600 text-white rounded-full shadow-lg flex items-center justify-center hover:bg-primary-700 transition-all duration-300 hover:scale-105"
        aria-label="Open chat"
      >
        <MessageSquare className="h-7 w-7" />
      </button>
    )
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 w-full max-w-md lg:max-w-lg h-[500px] lg:h-[600px] bg-white rounded-2xl shadow-xl border border-gray-100 flex flex-col overflow-hidden">
      {/* Chat Header */}
      <header className="bg-primary-600 text-white p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-display font-medium text-lg">AI Concierge</h3>
            <p className="text-xs text-primary-100 flex items-center space-x-1">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
              <span>Online</span>
            </p>
          </div>
        </div>
        <button
          onClick={toggleChat}
          className="p-2 text-white/80 hover:text-white transition-colors rounded-lg hover:bg-white/10"
          aria-label="Close chat"
        >
          <X className="h-5 w-5" />
        </button>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto p-4 space-y-4" ref={messagesEndRef}>
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 mx-auto mb-4 bg-primary-100 rounded-full flex items-center justify-center">
              <Bot className="h-8 w-8 text-primary-600" />
            </div>
            <h4 className="font-display font-medium text-gray-900 mb-2">Hello! How can I help you?</h4>
            <p className="text-gray-500 text-sm mb-4 max-w-sm mx-auto">
              I'm your personal AI concierge. Ask me about bookings, services, local recommendations, or anything else!
            </p>
            <div className="grid grid-cols-2 gap-2 max-w-sm mx-auto">
              {suggestions.map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={(e) => {
                    e.preventDefault()
                    setInput(suggestion)
                    handleSend()
                  }}
                  className="text-left p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-xs"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => renderMessage(message, index))}
            {typing && renderTyping()}
            <div ref={messagesEndRef} />
          </>
        )}
      </main>

      {/* Input */}
      <div className="border-t border-gray-100 p-4 bg-white">
        <form onSubmit={handleSend} className="flex items-end space-x-2">
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend(e)
                }
              }}
              placeholder="Ask me anything..."
              rows={1}
              className="input resize-none pr-10 min-h-[48px] max-h-28"
              style={{ height: '48px' }}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="btn-primary p-2.5 h-10 flex-shrink-0 transition-opacity disabled:opacity-50"
            aria-label="Send message"
          >
            {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
          </button>
        </form>
      </div>
    </div>
  )
}