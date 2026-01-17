import React from 'react'
import { FaQuestionCircle, FaDatabase, FaBrain, FaCommentDots } from 'react-icons/fa'
import './ComponentLibrary.css'

const components = [
  {
    type: 'userQuery',
    label: 'User Query',
    icon: FaQuestionCircle,
    color: '#2196F3',
    description: 'Entry point for user queries',
  },
  {
    type: 'knowledgeBase',
    label: 'Knowledge Base',
    icon: FaDatabase,
    color: '#FF9800',
    description: 'Document storage and retrieval',
  },
  {
    type: 'llmEngine',
    label: 'LLM Engine',
    icon: FaBrain,
    color: '#9C27B0',
    description: 'Language model processing',
  },
  {
    type: 'output',
    label: 'Output',
    icon: FaCommentDots,
    color: '#4CAF50',
    description: 'Display final response',
  },
]

function ComponentLibrary() {
  const onDragStart = (event, componentType) => {
    event.dataTransfer.setData('application/reactflow', componentType)
    event.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div className="component-library">
      <h2>Components</h2>
      <div className="component-list">
        {components.map((component) => {
          const Icon = component.icon
          return (
            <div
              key={component.type}
              className="component-item"
              draggable
              onDragStart={(e) => onDragStart(e, component.type)}
              style={{ borderLeftColor: component.color }}
            >
              <div className="component-icon" style={{ color: component.color }}>
                <Icon />
              </div>
              <div className="component-info">
                <div className="component-label">{component.label}</div>
                <div className="component-description">{component.description}</div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ComponentLibrary
