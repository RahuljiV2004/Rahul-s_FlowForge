import React, { useState, useEffect } from 'react'
import './ComponentConfigPanel.css'

function ComponentConfigPanel({ node, onUpdate }) {
  const [config, setConfig] = useState({})

  useEffect(() => {
    if (node) {
      setConfig(node.data || {})
    } else {
      setConfig({})
    }
  }, [node])

  if (!node) {
    return (
      <div className="config-panel">
        <div className="config-panel-empty">
          <p>Select a component to configure</p>
        </div>
      </div>
    )
  }

  const handleChange = (key, value) => {
    const newConfig = { ...config, [key]: value }
    setConfig(newConfig)
    onUpdate(node.id, newConfig)
  }

  const renderConfigFields = () => {
    // Get the actual type from node.data.type (stored by nodeFactory) or fallback to node.type
    const nodeType = node.data?.type || node.type
    
    switch (nodeType) {
      case 'userQuery':
        return (
          <div className="config-field">
            <label>Component Name</label>
            <input
              type="text"
              value={config.name || 'User Query'}
              onChange={(e) => handleChange('name', e.target.value)}
            />
          </div>
        )

      case 'knowledgeBase':
        return (
          <>
            <div className="config-field">
              <label>Knowledge Base ID</label>
              <input
                type="text"
                value={config.knowledgeBaseId || ''}
                onChange={(e) => handleChange('knowledgeBaseId', e.target.value)}
                placeholder="Enter knowledge base ID"
              />
            </div>
            <div className="config-field">
              <label>Embedding Model</label>
              <select
                value={config.embeddingModel || 'openai'}
                onChange={(e) => handleChange('embeddingModel', e.target.value)}
              >
                <option value="openai">OpenAI</option>
                <option value="gemini">Gemini</option>
              </select>
            </div>
            <div className="config-field">
              <label>Top K Results</label>
              <input
                type="number"
                value={config.topK || 5}
                onChange={(e) => handleChange('topK', parseInt(e.target.value))}
                min="1"
                max="20"
              />
            </div>
          </>
        )

      case 'llmEngine':
        return (
          <>
            <div className="config-field">
              <label>LLM Provider</label>
              <select
                value={config.llmProvider || 'openai'}
                onChange={(e) => handleChange('llmProvider', e.target.value)}
              >
                <option value="openai">OpenAI GPT</option>
                <option value="gemini">Google Gemini</option>
              </select>
            </div>
            {config.llmProvider === 'openai' && (
              <div className="config-field">
                <label>Model</label>
                <select
                  value={config.model || 'gpt-3.5-turbo'}
                  onChange={(e) => handleChange('model', e.target.value)}
                >
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                </select>
              </div>
            )}
            <div className="config-field">
              <label>Custom Prompt (Optional)</label>
              <textarea
                value={config.customPrompt || ''}
                onChange={(e) => handleChange('customPrompt', e.target.value)}
                placeholder="Enter custom system prompt..."
                rows="4"
              />
            </div>
            <div className="config-field">
              <label>
                <input
                  type="checkbox"
                  checked={config.useWebSearch || false}
                  onChange={(e) => handleChange('useWebSearch', e.target.checked)}
                />
                Enable Web Search
              </label>
            </div>
            {config.useWebSearch && (
              <div className="config-field">
                <label>Web Search Provider</label>
                <select
                  value={config.webSearchProvider || 'serpapi'}
                  onChange={(e) => handleChange('webSearchProvider', e.target.value)}
                >
                  <option value="serpapi">SerpAPI</option>
                  <option value="brave">Brave Search</option>
                </select>
              </div>
            )}
          </>
        )

      case 'output':
        return (
          <div className="config-field">
            <label>Component Name</label>
            <input
              type="text"
              value={config.name || 'Output'}
              onChange={(e) => handleChange('name', e.target.value)}
            />
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="config-panel">
      <div className="config-panel-header">
        <h3>Configuration</h3>
        <div className="component-type-badge">{node.data?.type || node.type}</div>
      </div>
      <div className="config-panel-content">
        {renderConfigFields()}
      </div>
    </div>
  )
}

export default ComponentConfigPanel
