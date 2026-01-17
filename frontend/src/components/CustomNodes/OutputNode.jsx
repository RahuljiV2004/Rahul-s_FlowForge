import React from 'react'
import { Handle, Position } from 'reactflow'
import './CustomNodes.css'

function OutputNode({ data, selected }) {
  return (
    <div className={`custom-node output-node ${selected ? 'selected' : ''}`}>
      <div className="node-header">
        <div className="node-icon">💬</div>
        <div className="node-title">Output</div>
      </div>
      <div className="node-description">Display final response</div>
      
      <div className="node-content">
        <div className="config-field-inline">
          <label>Component Name</label>
          <input
            type="text"
            value={data.name || 'Output'}
            onChange={(e) => data.onUpdate({ name: e.target.value })}
            placeholder="Component name"
          />
        </div>
      </div>

      <Handle type="target" position={Position.Top} id="output" className="handle-output" />
    </div>
  )
}

export default OutputNode
