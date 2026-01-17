import React, { useState, useRef } from 'react'
import { Handle, Position } from 'reactflow'
import toast from 'react-hot-toast'
import './CustomNodes.css'

function KnowledgeBaseNode({ data, selected }) {
  const [uploading, setUploading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState(data.uploadedFiles || [])
  const fileInputRef = useRef(null)
  
  // Auto-detect default embedding model - prefer gemini if not specified
  const defaultEmbeddingModel = data.embeddingModel || 'gemini'

  const handleFileSelect = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.pdf')) {
      toast.error('Only PDF files are supported')
      return
    }

    if (!data.knowledgeBaseId) {
      toast.error('Please enter a Knowledge Base ID first')
      return
    }

    setUploading(true)

    // try {
    //   const formData = new FormData()
    //   formData.append('file', file)
    //   formData.append('knowledge_base_id', data.knowledgeBaseId)
    //   // Use the embedding model from the node config, or let backend auto-detect
    //   const embeddingModel = defaultEmbeddingModel
    //   formData.append('embedding_model', embeddingModel)

    //   const response = await fetch('http://localhost:8000/api/documents/upload', {
    //     method: 'POST',
    //     body: formData,
    //   })

    //   if (response.ok) {
    //     const result = await response.json()
    //     const newFiles = [...uploadedFiles, {
    //       name: file.name,
    //       id: result.id,
    //       uploadedAt: new Date().toLocaleString(),
    //     }]
    //     setUploadedFiles(newFiles)
    //     data.onUpdate({ uploadedFiles: newFiles })
    //     toast.success(`File "${file.name}" uploaded successfully!`)
    //   } else {
    //     const error = await response.json()
    //     toast.error(error.detail || 'Failed to upload file')
    //   }
    // } catch (error) {
    //   toast.error('Error uploading file: ' + error.message)
    // } finally {
    //   setUploading(false)
    //   // Reset file input
    //   if (fileInputRef.current) {
    //     fileInputRef.current.value = ''
    //   }
    // }
    try {
  const formData = new FormData()
  formData.append('file', file)

  const embeddingModel = defaultEmbeddingModel

  const response = await fetch(
    `http://localhost:8000/api/documents/upload?knowledge_base_id=${encodeURIComponent(
      data.knowledgeBaseId
    )}&embedding_model=${encodeURIComponent(embeddingModel)}`,
    {
      method: 'POST',
      body: formData,
    }
  )

  if (response.ok) {
    const result = await response.json()

    const newFiles = [
      ...uploadedFiles,
      {
        name: file.name,
        id: result.id,
        uploadedAt: new Date().toLocaleString(),
      },
    ]

    setUploadedFiles(newFiles)
    data.onUpdate({ uploadedFiles: newFiles })

    toast.success(`File "${file.name}" uploaded successfully!`)
  } else {
    const error = await response.json()
    toast.error(error.detail || 'Failed to upload file')
  }
} catch (error) {
  console.error("Upload Error:", error)
  toast.error('Error uploading file: ' + error.message)
} finally {
  setUploading(false)

  if (fileInputRef.current) {
    fileInputRef.current.value = ''
  }
}

  }

  const handleRemoveFile = (fileId) => {
    const newFiles = uploadedFiles.filter(f => f.id !== fileId)
    setUploadedFiles(newFiles)
    data.onUpdate({ uploadedFiles: newFiles })
    toast.success('File removed from list')
  }

  return (
    <div className={`custom-node knowledge-base-node ${selected ? 'selected' : ''}`}>
      <div className="node-header">
        <div className="node-icon">📚</div>
        <div className="node-title">Knowledge Base</div>
      </div>
      <div className="node-description">Document storage and retrieval</div>
      
      <div className="node-content">
        <div className="config-field-inline">
          <label>Knowledge Base ID</label>
          <input
            type="text"
            value={data.knowledgeBaseId || ''}
            onChange={(e) => data.onUpdate({ knowledgeBaseId: e.target.value })}
            placeholder="Enter knowledge base ID"
          />
        </div>

        <div className="config-field-inline">
          <label>Embedding Model</label>
          <select
            value={defaultEmbeddingModel}
            onChange={(e) => data.onUpdate({ embeddingModel: e.target.value })}
          >
            <option value="gemini">Gemini</option>
            <option value="openai">OpenAI</option>
            <option value="cohere">Cohere</option>
          </select>
        </div>

        <div className="config-field-inline">
          <label>Top K Results</label>
          <input
            type="number"
            value={data.topK || 5}
            onChange={(e) => data.onUpdate({ topK: parseInt(e.target.value) || 5 })}
            min="1"
            max="20"
          />
        </div>

        {/* File Upload Section */}
        <div className="file-upload-section">
          <label className="file-upload-label">Upload Document</label>
          <div 
            className={`file-upload-area ${uploading ? 'uploading' : ''}`}
            onClick={() => !uploading && fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              disabled={uploading}
            />
            {uploading ? (
              <div className="upload-status">
                <div className="upload-spinner"></div>
                <span>Uploading...</span>
              </div>
            ) : (
              <div className="file-upload-content">
                <div className="upload-icon">📄</div>
                <div className="upload-text">
                  <span className="upload-primary">Click to upload</span>
                  <span className="upload-secondary">or drag and drop</span>
                  <span className="upload-hint">PDF files only</span>
                </div>
              </div>
            )}
          </div>

          {/* Uploaded Files List */}
          {uploadedFiles.length > 0 && (
            <div className="uploaded-files-list">
              <label>Uploaded Files</label>
              {uploadedFiles.map((file) => (
                <div key={file.id} className="uploaded-file-item">
                  <span className="file-name">{file.name}</span>
                  <button
                    className="remove-file-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleRemoveFile(file.id)
                    }}
                    title="Remove from list"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <Handle type="target" position={Position.Top} id="query" className="handle-query" />
      <Handle type="source" position={Position.Bottom} id="context" className="handle-context" />
    </div>
  )
}

export default KnowledgeBaseNode
