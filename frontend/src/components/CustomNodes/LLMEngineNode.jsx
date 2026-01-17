import React, { useState } from 'react'
import { Handle, Position } from 'reactflow'
import './CustomNodes.css'

function LLMEngineNode({ data, selected }) {
  return (
    <div className={`custom-node llm-engine-node ${selected ? 'selected' : ''}`}>
      <div className="node-header">
        <div className="node-icon">🧠</div>
        <div className="node-title">LLM Engine</div>
      </div>
      <div className="node-description">Language model processing</div>
      
      <div className="node-content">
        <div className="config-field-inline">
          <label>LLM Provider</label>
          <select
            value={data.llmProvider || 'gemini'}
            onChange={(e) => data.onUpdate({ llmProvider: e.target.value })}
          >
            <option value="gemini">Google Gemini</option>
            <option value="openai">OpenAI GPT</option>
            <option value="cohere">Cohere</option>
          </select>
        </div>

        {data.llmProvider === 'openai' && (
          <div className="config-field-inline">
            <label>Model</label>
            <select
              value={data.model || 'gpt-3.5-turbo'}
              onChange={(e) => data.onUpdate({ model: e.target.value })}
            >
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              <option value="gpt-4">GPT-4</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
            </select>
          </div>
        )}

        <div className="config-field-inline">
          <label>Custom Prompt (Optional)</label>
          <textarea
            value={data.customPrompt || ''}
            onChange={(e) => data.onUpdate({ customPrompt: e.target.value })}
            placeholder="Enter custom system prompt..."
            rows="3"
          />
        </div>

        <div className="config-field-inline checkbox-field">
          <label>
            <input
              type="checkbox"
              checked={data.useWebSearch || false}
              onChange={(e) => data.onUpdate({ useWebSearch: e.target.checked })}
            />
            Enable Web Search
          </label>
        </div>

        {data.useWebSearch && (
          <div className="config-field-inline">
            <label>Web Search Provider</label>
            <select
              value={data.webSearchProvider || 'serpapi'}
              onChange={(e) => data.onUpdate({ webSearchProvider: e.target.value })}
            >
              <option value="serpapi">SerpAPI</option>
              <option value="brave">Brave Search</option>
            </select>
          </div>
        )}
      </div>

      <Handle type="target" position={Position.Top} id="query" className="handle-query" />
      <Handle type="target" position={Position.Left} id="context" className="handle-context" style={{ top: '40%' }} />
      <Handle type="source" position={Position.Bottom} id="output" className="handle-output" />
    </div>
  )
}

export default LLMEngineNode
