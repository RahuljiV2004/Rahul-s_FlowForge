import React from 'react'
import { Handle, Position } from 'reactflow'
import './CustomNodes.css'

function UserQueryNode({ data, selected }) {
  return (
    <div className={`custom-node user-query-node ${selected ? 'selected' : ''}`}>
      <div className="node-header">
        <div className="node-icon">📝</div>
        <div className="node-title">User Query</div>
      </div>
      <div className="node-description">Entry point for user queries</div>
      
      <div className="node-content">
        <div className="config-field-inline">
          <label>Component Name</label>
          <input
            type="text"
            value={data.name || 'User Query'}
            onChange={(e) => data.onUpdate({ name: e.target.value })}
            placeholder="Component name"
          />
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} id="query" className="handle-query" />
    </div>
  )
}

export default UserQueryNode
