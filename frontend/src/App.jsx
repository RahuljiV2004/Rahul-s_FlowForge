import React, { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import { ReactFlowProvider } from 'reactflow'
import WorkflowBuilder from './components/WorkflowBuilder'
import ChatInterface from './components/ChatInterface'
import HomePage from './components/HomePage'
import './App.css'

function App() {
  const [activeWorkflow, setActiveWorkflow] = useState(null)
  const [showChat, setShowChat] = useState(false)
  const [currentView, setCurrentView] = useState('home') // 'home', 'builder', 'chat'
  const [editingWorkflow, setEditingWorkflow] = useState(null)

  const handleCreateStack = () => {
    setEditingWorkflow(null)
    setCurrentView('builder')
  }

  const handleEditStack = (workflow) => {
    console.log('App.jsx handleEditStack called with:', workflow)
    setEditingWorkflow(workflow)
    setCurrentView('builder')
  }

  const handleWorkflowReady = (workflow) => {
    setActiveWorkflow(workflow)
    setShowChat(true)
    setCurrentView('chat')
  }

  const handleBackToHome = () => {
    setCurrentView('home')
    setEditingWorkflow(null)
  }

  const handleBackToBuilder = () => {
    setShowChat(false)
    setCurrentView('builder')
  }

  return (
    <div className="app">
      <Toaster position="top-right" />
      
      {currentView === 'home' && (
        <HomePage 
          onCreateStack={handleCreateStack}
          onEditStack={handleEditStack}
        />
      )}
      
      {currentView === 'builder' && (
        <ReactFlowProvider>
          <WorkflowBuilder 
            editingWorkflow={editingWorkflow}
            onWorkflowReady={handleWorkflowReady}
            onBack={handleBackToHome}
          />
        </ReactFlowProvider>
      )}
      
      {currentView === 'chat' && (
        <ChatInterface 
          workflow={activeWorkflow}
          onBack={handleBackToBuilder}
        />
      )}
    </div>
  )
}

export default App
