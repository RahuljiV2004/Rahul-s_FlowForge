const nodeColors = {
  userQuery: '#2196F3',
  knowledgeBase: '#FF9800',
  llmEngine: '#9C27B0',
  output: '#4CAF50',
}

const nodeLabels = {
  userQuery: 'User Query',
  knowledgeBase: 'Knowledge Base',
  llmEngine: 'LLM Engine',
  output: 'Output',
}

const generateId = () => {
  return `node_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

export const createNode = (type, position, onUpdateCallback = null) => {
  const id = generateId()
  
  // Map to custom node types
  const nodeTypeMap = {
    'userQuery': 'userQuery',
    'knowledgeBase': 'knowledgeBase',
    'llmEngine': 'llmEngine',
    'output': 'output',
  }
  
  const baseNode = {
    id,
    type: nodeTypeMap[type] || type,
    position,
    data: {
      label: nodeLabels[type] || type,
      type,
      onUpdate: onUpdateCallback || (() => {}),
    },
  }

  // Add default config based on type
  switch (type) {
    case 'knowledgeBase':
      baseNode.data = {
        ...baseNode.data,
        knowledgeBaseId: '',
        embeddingModel: 'gemini',  // Default to Gemini
        topK: 5,
      }
      break
    case 'llmEngine':
      baseNode.data = {
        ...baseNode.data,
        llmProvider: 'gemini',  // Default to Gemini
        model: 'gpt-3.5-turbo',  // This won't be used for Gemini
        customPrompt: '',
        useWebSearch: false,
        webSearchProvider: 'serpapi',
      }
      break
    default:
      break
  }

  return baseNode
}
