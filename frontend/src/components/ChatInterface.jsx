import React, { useState, useEffect, useRef } from 'react'
import { FaArrowLeft, FaPaperPlane, FaTrash, FaComments, FaExpand } from 'react-icons/fa'
import axios from 'axios'
import toast from 'react-hot-toast'
import './ChatInterface.css'

function ChatInterface({ workflow, onBack }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [chatSessions, setChatSessions] = useState([])
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    loadChatSessions()
  }, [workflow])

  useEffect(() => {
    if (sessionId) {
      loadChatHistory()
    }
  }, [sessionId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadChatSessions = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/chat/sessions?workflow_id=${workflow.id}`
      )
      setChatSessions(response.data)
    } catch (error) {
      console.error('Error loading chat sessions:', error)
    }
  }

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/chat/sessions/${sessionId}/history`
      )
      setMessages(
        response.data.map((msg) => ({
          role: msg.role,
          content: msg.content,
        }))
      )
    } catch (error) {
      console.error('Error loading chat history:', error)
    }
  }

  const handleSessionClick = (session) => {
    setSessionId(session.session_id)
    // Don't close sidebar - keep it open
  }

  const handleNewChat = () => {
    setSessionId(null)
    setMessages([])
    // Don't close sidebar - keep it open
  }

  const handleDeleteSession = async (session, e) => {
    e.stopPropagation()
    try {
      await axios.delete(
        `http://localhost:8000/api/chat/sessions/${session.session_id}`
      )
      setChatSessions(chatSessions.filter(s => s.session_id !== session.session_id))
      if (sessionId === session.session_id) {
        setSessionId(null)
        setMessages([])
      }
      toast.success('Chat session deleted')
    } catch (error) {
      toast.error('Error deleting chat session')
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await axios.post('http://localhost:8000/api/chat/query', {
        query: userMessage,
        workflow_id: workflow.id,
        session_id: sessionId,
      })

      setSessionId(response.data.session_id)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.data.response },
      ])
      
      // Refresh sessions list to get latest
      loadChatSessions()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error processing query')
      setMessages((prev) => prev.slice(0, -1)) // Remove user message on error
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="chat-interface">
      {/* Sidebar */}
      <div className={`chat-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-title">
            <FaComments />
            <span>Chat History</span>
          </div>
          <button 
            className="new-chat-btn"
            onClick={handleNewChat}
          >
            New Chat
          </button>
        </div>
        
        <div className="sessions-list">
          {chatSessions.map((session) => (
            <div
              key={session.session_id}
              className={`session-item ${sessionId === session.session_id ? 'active' : ''}`}
              onClick={() => handleSessionClick(session)}
            >
              <div className="session-info">
                <div className="session-name">
                  {formatDate(session.created_at)}
                </div>
                <div className="session-date">
                  {new Date(session.created_at).toLocaleDateString()}
                </div>
              </div>
              <button
                className="delete-session-btn"
                onClick={(e) => handleDeleteSession(session, e)}
                title="Delete session"
              >
                <FaTrash />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        <div className="chat-header">
          <div className="chat-header-content">
            <button 
              className="sidebar-toggle"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <FaExpand />
            </button>
            
            <div className="chat-brand" onClick={onBack}>
              <h2 className="chat-title">
                Rahul's FlowForge
              </h2>
              <span className="chat-subtitle">
                Chat Mode – {workflow.name}
              </span>
            </div>
          </div>
        </div>

        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="chat-empty">
              <p>Start a conversation with your workflow</p>
              <p className="chat-empty-subtitle">
                Ask questions and workflow will process them through the configured components
              </p>
            </div>
          )}
          {messages.map((message, index) => (
            <div
              key={index}
              className={`chat-message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
            >
              <div className="message-content">{message.content}</div>
            </div>
          ))}
          {loading && (
            <div className="chat-message assistant-message">
              <div className="message-content">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSend} className="chat-input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="chat-input"
            disabled={loading}
          />
          <button type="submit" className="chat-send-button" disabled={loading || !input.trim()}>
            <FaPaperPlane />
          </button>
        </form>
      </div>
    </div>
  )
}

export default ChatInterface
