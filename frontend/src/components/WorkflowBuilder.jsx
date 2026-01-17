import React, { useState, useCallback, useRef, useEffect } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  MarkerType,
  useReactFlow,
} from 'reactflow'
import 'reactflow/dist/style.css'
import ComponentLibrary from './ComponentLibrary'
import { createNode } from '../utils/nodeFactory'
import UserQueryNode from './CustomNodes/UserQueryNode'
import KnowledgeBaseNode from './CustomNodes/KnowledgeBaseNode'
import LLMEngineNode from './CustomNodes/LLMEngineNode'
import OutputNode from './CustomNodes/OutputNode'
import toast from 'react-hot-toast'
import './WorkflowBuilder.css'
import './CustomNodes/CustomNodes.css'

const nodeTypes = {
  userQuery: UserQueryNode,
  knowledgeBase: KnowledgeBaseNode,
  llmEngine: LLMEngineNode,
  output: OutputNode,
}

const initialNodes = []
const initialEdges = []

function WorkflowBuilder({ editingWorkflow, onWorkflowReady, onBack }) {
  console.log('WorkflowBuilder received editingWorkflow:', editingWorkflow)
  const { fitView } = useReactFlow()
  
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [selectedNode, setSelectedNode] = useState(null)
  const [workflowName, setWorkflowName] = useState('')
  const [workflowDescription, setWorkflowDescription] = useState('')
  const reactFlowWrapper = useRef(null)

  console.log('Initial nodes:', nodes)
  console.log('Initial edges:', edges)

  // Update nodes and edges when editingWorkflow changes
  useEffect(() => {
    if (editingWorkflow) {
      console.log('Editing workflow changed, updating nodes and edges')
      console.log('Editing workflow nodes:', editingWorkflow.nodes)
      console.log('Editing workflow edges:', editingWorkflow.edges)
      
      // Process nodes to ensure they have the correct structure
      const processedNodes = editingWorkflow.nodes?.map(node => ({
        ...node,
        data: {
          ...node.data,
          onUpdate: (newData) => {
            setNodes((nds) =>
              nds.map((n) => {
                if (n.id === node.id) {
                  return { ...n, data: { ...n.data, ...newData } }
                }
                return n
              })
            )
          }
        }
      })) || []
      
      const processedEdges = editingWorkflow.edges?.map(edge => ({
        ...edge,
        type: 'smoothstep',
        animated: true,
        markerEnd: {
          type: MarkerType.ArrowClosed,
        },
      })) || []
      
      console.log('Processed nodes:', processedNodes)
      console.log('Processed edges:', processedEdges)
      
      setNodes(processedNodes)
      setEdges(processedEdges)
      setWorkflowName(editingWorkflow.name || '')
      setWorkflowDescription(editingWorkflow.description || '')
      
      // Fit view to show all nodes after a short delay
      setTimeout(() => {
        fitView({ padding: 0.2, duration: 800 })
      }, 100)
    } else {
      // Reset to empty state when no editing workflow
      setNodes([])
      setEdges([])
      setWorkflowName('')
      setWorkflowDescription('')
    }
  }, [editingWorkflow, setNodes, setEdges, fitView])

  const onConnect = useCallback(
    (params) => {
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            type: 'smoothstep',
            animated: true,
            markerEnd: {
              type: MarkerType.ArrowClosed,
            },
          },
          eds
        )
      )
    },
    [setEdges]
  )

  const onDragOver = useCallback((event) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const handleNodeUpdate = useCallback((nodeId, data) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return { ...node, data: { ...node.data, ...data } }
        }
        return node
      })
    )
  }, [setNodes])

  const onDrop = useCallback(
    (event) => {
      event.preventDefault()

      const type = event.dataTransfer.getData('application/reactflow')
      if (!type) {
        return
      }

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect()
      const position = {
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      }

      const newNode = createNode(type, position, null)
      
      // Set up the update callback after node is created
      newNode.data.onUpdate = (newData) => {
        handleNodeUpdate(newNode.id, newData)
      }
      
      setNodes((nds) => nds.concat(newNode))
    },
    [setNodes, handleNodeUpdate]
  )

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node)
  }, [])

  const onPaneClick = useCallback(() => {
    setSelectedNode(null)
  }, [])

  const onNodesDelete = useCallback((deleted) => {
    setNodes((nds) => nds.filter((node) => !deleted.find((d) => d.id === node.id)))
    if (selectedNode && deleted.find((d) => d.id === selectedNode.id)) {
      setSelectedNode(null)
    }
  }, [selectedNode, setNodes])


  const handleSaveWorkflow = async () => {
    if (!workflowName.trim()) {
      toast.error('Please enter a workflow name')
      return
    }

    // Validate workflow - check node.data.type (stored by nodeFactory) or fallback to node.type
    const hasUserQuery = nodes.some((n) => n.data?.type === 'userQuery' || n.type === 'userQuery')
    const hasLLM = nodes.some((n) => n.data?.type === 'llmEngine' || n.type === 'llmEngine')
    const hasOutput = nodes.some((n) => n.data?.type === 'output' || n.type === 'output')

    if (!hasUserQuery || !hasLLM || !hasOutput) {
      toast.error('Workflow must contain User Query, LLM Engine, and Output components')
      return
    }

    try {
      const workflowData = {
        name: workflowName,
        description: workflowDescription,
        nodes: nodes.map((node) => ({
          id: node.id,
          type: node.data?.type || node.type, // Use data.type (from nodeFactory) or fallback
          position: node.position,
          data: node.data,
        })),
        edges: edges.map((edge) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
        })),
      }

      const url = editingWorkflow 
        ? `http://localhost:8000/api/workflows/${editingWorkflow.id}`
        : 'http://localhost:8000/api/workflows/'
      
      const method = editingWorkflow ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowData),
      })

      if (response.ok) {
        const workflow = await response.json()
        toast.success(editingWorkflow ? 'Workflow updated successfully!' : 'Workflow saved successfully!')
        onWorkflowReady(workflow)
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to save workflow')
      }
    } catch (error) {
      toast.error('Error saving workflow: ' + error.message)
    }
  }

  return (
    <div className="workflow-builder">
      {/* <div className="workflow-header">
  <div className="brand-section">
    <div className="brand-logo">⚙️</div>
    <div className="brand-text">
      <h1>FlowForge</h1>
      <span className="subtitle">No-Code AI Workflow Studio</span>
    </div>
  </div>

  <div className="workflow-header-controls">
    <input
      type="text"
      placeholder="Enter workflow name..."
      value={workflowName}
      onChange={(e) => setWorkflowName(e.target.value)}
      className="workflow-name-input"
    />

    <button onClick={handleSaveWorkflow} className="save-workflow-btn">
      <span>🚀</span> Save & Chat
    </button>
  </div>
</div> */}
<div className="editor-header">

  <div className="editor-header-content">

    {/* LEFT SIDE – CLICKABLE BRAND */}
    <div className="editor-brand-section">

      <div 
        className="editor-brand-text clickable-brand" 
        onClick={onBack}
      >
        <h1>Rahul's FlowForge</h1>
        <span className="editor-subtitle">
          {editingWorkflow ? "Edit Workflow" : "Create New Workflow"}
        </span>
      </div>

    </div>

    {/* RIGHT SIDE CONTROLS (PUSHED EXTREME RIGHT) */}
    <div className="editor-controls">

      <input
        type="text"
        placeholder="Workflow name..."
        value={workflowName}
        onChange={(e) => setWorkflowName(e.target.value)}
        className="editor-input"
      />

      <input
        type="text"
        placeholder="Workflow description..."
        value={workflowDescription}
        onChange={(e) => setWorkflowDescription(e.target.value)}
        className="editor-input"
      />

      <button onClick={handleSaveWorkflow} className="green-btn">
        {editingWorkflow ? "Update & Chat" : "Save & Chat"}
      </button>

    </div>

  </div>

</div>



      <div className="workflow-content">
        <ComponentLibrary />
        
        <div className="workflow-canvas-wrapper" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            onNodesDelete={onNodesDelete}
            fitView
            className="workflow-canvas"
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>
      </div>
    </div>
  )
}

export default WorkflowBuilder
