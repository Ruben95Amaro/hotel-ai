import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { hotelApi } from '../services/api'
import { Send, Loader2, Bot, User, X, ChevronDown, ChevronUp, Trash2, Copy, Check } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Chat() {
  const { user, isAuthenticated } = useAuth()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
  const [showHistory, setShowHistory] = useState(false)
  const messagesEndRef = useRef(null)
  const chatContainerRef = useRef(null)
  const navigate = useNavigate()

  const { register, handleSubmit } = React.useForm()

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input, timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])
    const currentInput = input
    setInput('')
    setLoading(true)

    try {
      // Call backend chat API
      const response = await hotelApi.chat(currentInput, sessionId)
      const botMessage = { 
        role: 'assistant', 
        content: response.data.response || response.data.message || 'I apologize, but I couldn\'t process that request.', 
        timestamp: new Date(),
        session_id: sessionId
      }
      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage = { 
        role: 'assistant', 
        content: 'I\'m sorry, I\'m having trouble connecting. Please try again in a moment.', 
        timestamp: new Date() 
      }
      setMessages(prev => [...prev, errorMessage])
      toast.error('Failed to send message')
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    toast.success('Chat cleared')
  }

  const copyMessage = (content) => {
    navigator.clipboard.writeText(content)
    toast.success('Copied to clipboard')
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12">
        <div className="container-custom text-center">
          <div className="card p-12 max-w-md mx-auto">
            <div className="w-16 h-16 mx-auto mb-6 bg-primary-100 rounded-full flex items-center justify-center">
              <Bot className="h-8 w-8 text-primary-600" />
            </div>
            <h2 className="font-display text-2xl font-medium text-gray-900 mb-3">Sign in to Chat</h2>
            <p className="text-gray-600 mb-6">Access your AI concierge for personalized assistance.</p>
            <div className="flex space-x-3">
              <button onClick={() => navigate('/login')} className="btn-primary flex-1">Sign In</button>
              <button onClick={() => navigate('/register')} className="btn-secondary flex-1">Sign Up</button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Chat Header */}
      <header className="bg-white border-b border-gray-100 sticky top-16 z-40">
        <div className="container-custom">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
                <Bot className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <h2 className="font-display text-lg font-medium text-gray-900">AI Concierge</h2>
                <p className="text-xs text-green-600 flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                  <span>Online</span>
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button onClick={clearChat} className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors" title="Clear chat">
                <Trash2 className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto p-4 lg:p-6" ref={chatContainerRef}>
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <div className="text-center py-12 lg:py-20">
              <div className="w-20 h-20 mx-auto mb-6 bg-primary-100 rounded-full flex items-center justify-center">
                <Bot className="h-10 w-10 text-primary-600" />
              </div>
              <h3 className="font-display text-xl font-medium text-gray-900 mb-2">Hello! How can I help you?</h3>
              <p className="text-gray-500 mb-6 max-w-sm mx-auto">
                I'm your personal AI concierge. Ask me about bookings, services, local recommendations, or anything else!
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-sm mx-auto">
                {[
                  'What are the check-in times?',
                  'Book a spa appointment',
                  'Restaurant recommendations nearby',
                  'Extend my current stay',
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => handleSend({ preventDefault: () => {} }, { target: { value: suggestion } })}
                    className="text-left p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-sm"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                  {message.role === 'assistant' && (
                    <div className="flex items-start space-x-2 mb-1">
                      <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <Bot className="h-4 w-4 text-primary-600" />
                      </div>
                    </div>
                  )}
                  <div className={`flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'} space-y-1`}>
                    <div className={`px-4 py-3 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white rounded-br-md'
                        : 'bg-white text-gray-900 border border-gray-100 rounded-bl-md shadow-sm'
                    }`}>
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`text-xs ${message.role === 'user' ? 'text-primary-400' : 'text-gray-400'}`}>
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      {message.role === 'assistant' && (
                        <button
                          onClick={() => copyMessage(message.content)}
                          className="p-1 text-gray-400 hover:text-primary-600 transition-colors"
                          title="Copy"
                        >
                          <Copy className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input */}
      <div className="bg-white border-t border-gray-100 p-4 lg:p-6">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSend} className="flex items-end space-x-3">
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
                placeholder="Ask me anything about your stay..."
                rows={1}
                className="input resize-none pr-12 min-h-[52px] max-h-32"
                style={{ height: '52px' }}
              />
            </div>
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="btn-primary p-3 h-12 flex-shrink-0 transition-opacity disabled:opacity-50"
              aria-label="Send message"
            >
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
            </button>
          </form>
          <p className="text-center text-xs text-gray-400 mt-2">
            Press Enter to send • Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  )
}