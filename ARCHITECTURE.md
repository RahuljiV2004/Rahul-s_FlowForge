# Architecture Documentation

## System Overview

The Workflow Builder is a full-stack application that enables users to create intelligent workflows through a visual interface. The system is built with a microservices architecture using Docker containers.

## Component Architecture

### Frontend (React.js)

**Technology Stack:**
- React 18.2
- React Flow 11.10 (for workflow visualization)
- Vite (build tool)
- Axios (HTTP client)
- React Hot Toast (notifications)

**Key Components:**
1. **WorkflowBuilder** - Main canvas for building workflows
2. **ComponentLibrary** - Draggable component palette
3. **ComponentConfigPanel** - Dynamic configuration forms
4. **ChatInterface** - Interactive chat for querying workflows

**State Management:**
- React hooks (useState, useCallback)
- Local component state
- API calls for persistence

### Backend (FastAPI)

**Technology Stack:**
- FastAPI 0.104
- SQLAlchemy 2.0 (ORM)
- PostgreSQL (database)
- ChromaDB (vector store)
- PyMuPDF (PDF processing)

**API Structure:**
```
/api/
  /documents/     - Document upload and management
  /workflows/     - Workflow CRUD operations
  /chat/          - Chat interface endpoints
  /embeddings/    - Vector search operations
```

**Service Layer:**
1. **DocumentProcessor** - PDF text extraction and chunking
2. **EmbeddingService** - Embedding generation and vector storage
3. **LLMService** - Language model interactions
4. **WorkflowExecutor** - Workflow execution engine

### Database (PostgreSQL)

**Tables:**
- `documents` - Document metadata
- `document_chunks` - Text chunks from documents
- `workflows` - Workflow definitions (nodes and edges)
- `chat_sessions` - Chat session tracking
- `chat_messages` - Message history

### Vector Store (ChromaDB)

**Purpose:**
- Store document embeddings
- Enable semantic search
- Retrieve relevant context for queries

**Collections:**
- One collection per knowledge base
- Stores embeddings, documents, and metadata

## Workflow Execution Flow

```
User Query
    ↓
User Query Component (Entry Point)
    ↓
Knowledge Base Component (Optional)
    ├─→ Query Embedding
    ├─→ Vector Search
    └─→ Context Retrieval
    ↓
LLM Engine Component
    ├─→ Combine Query + Context
    ├─→ Optional: Web Search
    └─→ LLM Generation
    ↓
Output Component
    └─→ Display Response
```

## Data Flow

### Document Processing
1. User uploads PDF
2. Backend extracts text using PyMuPDF
3. Text is chunked (1000 chars with 200 overlap)
4. Chunks are embedded using OpenAI/Gemini
5. Embeddings stored in ChromaDB
6. Metadata saved to PostgreSQL

### Workflow Execution
1. User sends query via chat
2. Workflow executor traverses nodes
3. Each component processes data:
   - User Query: Passes query forward
   - Knowledge Base: Retrieves relevant context
   - LLM Engine: Generates response
   - Output: Displays result
4. Execution log is created
5. Response and history saved to database

## Security Considerations

1. **API Keys**: Stored in environment variables
2. **File Uploads**: Validated for PDF only
3. **CORS**: Configured for specific origins
4. **Database**: Connection string in environment
5. **Input Validation**: Pydantic models for API requests

## Scalability

### Horizontal Scaling
- Frontend: Stateless, can be replicated
- Backend: Stateless API, can be load balanced
- Database: PostgreSQL can be replicated
- Vector Store: ChromaDB can be distributed

### Performance Optimizations
- Database indexing on frequently queried fields
- Embedding caching (future enhancement)
- Connection pooling for database
- Async operations where possible

## Deployment Architecture

### Docker Compose Setup
```
┌─────────────────┐
│   Frontend      │  Port 3000
│   (React)       │
└─────────────────┘
        │
        │ HTTP
        │
┌─────────────────┐
│   Backend       │  Port 8000
│   (FastAPI)     │
└─────────────────┘
        │
        ├──────────────┬──────────────┐
        │              │              │
┌───────▼────┐  ┌──────▼────┐  ┌─────▼─────┐
│ PostgreSQL │  │ ChromaDB  │  │ External  │
│  Port 5432 │  │  (Local)   │  │   APIs    │
└────────────┘  └───────────┘  └───────────┘
```

### Kubernetes Deployment (Optional)

**Services:**
- Frontend Service (ClusterIP/NodePort)
- Backend Service (ClusterIP)
- PostgreSQL Service (StatefulSet)
- ChromaDB Service (StatefulSet)

**ConfigMaps:**
- Application configuration
- Environment variables (non-sensitive)

**Secrets:**
- API keys
- Database credentials

## Monitoring (Optional)

### Metrics Collection
- Prometheus for metrics
- Key metrics:
  - API request rate
  - Response times
  - Error rates
  - Workflow execution times

### Logging
- Structured logging (JSON format)
- ELK Stack for aggregation
- Log levels: DEBUG, INFO, WARNING, ERROR

## Future Enhancements

1. **Authentication & Authorization**
   - User accounts
   - Role-based access
   - Workflow sharing

2. **Advanced Features**
   - Workflow templates
   - Component marketplace
   - Version control for workflows
   - A/B testing for workflows

3. **Performance**
   - Caching layer (Redis)
   - CDN for static assets
   - Database read replicas

4. **Monitoring**
   - Real-time execution logs
   - Performance dashboards
   - Alerting system
