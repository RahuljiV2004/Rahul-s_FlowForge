import React, { useState, useEffect } from 'react'
import axios from 'axios'

const HomePage = ({ onCreateStack, onEditStack }) => {
  const [workflows, setWorkflows] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingLoading, setEditingLoading] = useState(false)

  useEffect(() => {
    fetchWorkflows()
  }, [])

  const fetchWorkflows = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/workflows/')
      setWorkflows(response.data)
    } catch (error) {
      console.error('Error fetching workflows:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleEditStack = async (workflow) => {
    setEditingLoading(true)
    try {
      const response = await axios.get(
        `http://localhost:8000/api/workflows/${workflow.id}`
      )

      onEditStack(response.data)
    } catch (error) {
      console.error('Error fetching workflow details:', error)
      onEditStack(workflow)
    } finally {
      setEditingLoading(false)
    }
  }

  const handleDeleteWorkflow = async (workflowId) => {
    try {
      await axios.delete(
        `http://localhost:8000/api/workflows/${workflowId}`
      )
      setWorkflows(workflows.filter((wf) => wf.id !== workflowId))
    } catch (error) {
      console.error('Error deleting workflow:', error)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <div className="homepage">

      {/* HEADER */}
      <header className="header">
        <div className="header-content">
          <div className="brand">
            
            <h1 className="brand-title">Rahul's FlowForge</h1>
          </div>

          <button onClick={onCreateStack} className="green-btn">
            + Create Stack
          </button>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <div className="main-content">

        {/* RECTANGULAR CREATE BOX */}
  <div className="create-rectangle">

    <h3 className="create-heading">Start a New Workflow</h3>

    <p className="create-text">
      Build and customize your AI automation stack using our visual workflow builder.
    </p>

    <button onClick={onCreateStack} className="green-btn">
      Create New Stack
    </button>

  </div>

        {/* LOADING STATE */}
        {loading && (
          <div className="loading-state">
            <p>Loading your stacks...</p>
          </div>
        )}

        {/* EMPTY STATE */}
        {!loading && workflows.length === 0 && (
          <div className="empty-state">
            <p>No stacks yet</p>
            <button onClick={onCreateStack} className="green-btn">
              Create Your First Stack
            </button>
          </div>
        )}

        {/* WORKFLOWS GRID */}
        {!loading && workflows.length > 0 && (
          <div className="workflows-section">

            <h3 className="section-title">Your Stacks</h3>

            <div className="workflows-grid">

              {workflows.map((workflow) => (
                <div key={workflow.id} className="workflow-card">

                  <div className="card-header">
                    <h4>{workflow.name}</h4>

                    <div className="card-actions">
        

                      <button
                        onClick={() =>
                          handleDeleteWorkflow(workflow.id)
                        }
                        className="icon-btn delete"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>

                  <p className="card-description">
                    {workflow.description || 'No description'}
                  </p>

                  <div className="card-meta">
                    <span>
                      {formatDate(workflow.created_at)}
                    </span>

                    <span
                      className={
                        workflow.is_active
                          ? 'active'
                          : 'inactive'
                      }
                    >
                      {workflow.is_active
                        ? 'Active'
                        : 'Inactive'}
                    </span>
                  </div>

                  <button
                    onClick={() => handleEditStack(workflow)}
                    className="green-btn open-btn"
                  >
                    Open Stack →
                  </button>

                </div>
              ))}

            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default HomePage
