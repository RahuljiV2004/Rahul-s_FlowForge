# Workflow Builder - No-Code/Low-Code Intelligent Workflow Application

A comprehensive web application that enables users to visually create and interact with intelligent workflows. Build workflows by connecting components that handle user input, extract knowledge from documents, interact with language models, and return answers through a chat interface.

## 🎯 Features
![Home Diagram](assets/floeforge.png)
### Core Components

1. **User Query Component** - Entry point for user queries
2. **Knowledge Base Component** - Document upload, processing, and vector-based retrieval
3. **LLM Engine Component** - Language model processing with OpenAI GPT and Google Gemini support
4. **Output Component** - Chat interface for displaying responses

### Key Capabilities

- **Visual Workflow Builder** - Drag-and-drop interface using React Flow
- **Document Processing** - PDF text extraction and embedding generation
- **Vector Search** - ChromaDB integration for semantic search
- **Multiple LLM Support** - OpenAI GPT and Google Gemini
- **Web Search Integration** - SerpAPI and Brave Search support
- **Chat Interface** - Interactive querying with conversation history
- **Workflow Persistence** - Save and load workflows from database

## 🏗️ Architecture

![Architecture Diagram](assets/Architecture.png)


## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- PostgreSQL 15+ (if running database separately)
- API Keys:
  - OpenAI API Key
  - Google Gemini API Key (optional)
  - SerpAPI Key (optional, for web search)
  - Brave Search API Key (optional, for web search)

## 🚀 Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd workflow-builder
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   Edit `backend/.env` and add your API keys:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@postgres:5432/workflow_db
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   SERPAPI_API_KEY=your_serpapi_key_here
   BRAVE_API_KEY=your_brave_api_key_here
   COHERE_API_KEY=your_cohere_api_key_here
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🛠️ Local Development Setup

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb workflow_db
   # Or use Docker:
   docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=workflow_db -p 5432:5432 postgres:15-alpine
   ```

6. **Run database migrations** (tables are auto-created on startup)
   ```bash
   # The application will create tables automatically
   ```

7. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000

## 📖 Usage Guide

### Building a Workflow

1. **Open the Workflow Builder**
   - Access http://localhost:3000
   - You'll see the workflow builder interface

2. **Add Components**
   - Drag components from the left panel onto the canvas
   - Required components: User Query, LLM Engine, Output
   - Optional: Knowledge Base (for document-based queries)

3. **Connect Components**
   - Click and drag from a component's output to another component's input
   - Typical flow: User Query → Knowledge Base → LLM Engine → Output

4. **Configure Components**
   - Click on a component to open the configuration panel
   - Configure settings:
     - **Knowledge Base**: Set knowledge base ID, embedding model, top K results
     - **LLM Engine**: Choose provider (OpenAI/Gemini), model, custom prompt, web search options

5. **Save Workflow**
   - Enter a workflow name
   - Click "Save & Chat" to validate and save the workflow

### Uploading Documents

1. **Upload PDF Documents**
   ```bash
   curl -X POST "http://localhost:8000/api/documents/upload" \
     -F "file=@document.pdf" \
     -F "knowledge_base_id=my_kb" \
     -F "embedding_model=openai"
   ```

2. **List Documents**
   ```bash
   curl http://localhost:8000/api/documents/
   ```

### Chatting with Workflow

1. **Start Chat**
   - After saving a workflow, you'll be redirected to the chat interface
   - Or click "Chat with Stack" after building

2. **Ask Questions**
   - Type your question in the chat input
   - The workflow will process your query through all connected components
   - View the response in the chat interface

3. **Follow-up Questions**
   - Continue the conversation
   - Chat history is maintained for context

## 🔌 API Endpoints

### Documents
- `POST /api/documents/upload` - Upload and process a document
- `GET /api/documents/` - List all documents
- `GET /api/documents/{id}` - Get document details
- `DELETE /api/documents/{id}` - Delete a document

### Workflows
- `POST /api/workflows/` - Create a workflow
- `GET /api/workflows/` - List all workflows
- `GET /api/workflows/{id}` - Get workflow details
- `PUT /api/workflows/{id}` - Update a workflow
- `DELETE /api/workflows/{id}` - Delete a workflow
- `POST /api/workflows/{id}/validate` - Validate a workflow

### Chat
- `POST /api/chat/query` - Send a query through a workflow
- `GET /api/chat/sessions/{session_id}/history` - Get chat history
- `GET /api/chat/sessions` - List chat sessions
- `DELETE /api/chat/sessions/{session_id}` - Delete a session

### Embeddings
- `POST /api/embeddings/search` - Search for similar documents

## 🐳 Docker Deployment

### Build Images
```bash
docker-compose build
```

### Run Services
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

### Clean Up (including volumes)
```bash
docker-compose down -v
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📁 Project Structure

```
workflow-builder/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py           # Database configuration
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── routers/              # API routes
│   │   │   ├── documents.py
│   │   │   ├── workflows.py
│   │   │   ├── chat.py
│   │   │   └── embeddings.py
│   │   └── services/             # Business logic
│   │       ├── document_processor.py
│   │       ├── embedding_service.py
│   │       ├── llm_service.py
│   │       └── workflow_executor.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── WorkflowBuilder.jsx
│   │   │   ├── ComponentLibrary.jsx
│   │   │   ├── ComponentConfigPanel.jsx
│   │   │   └── ChatInterface.jsx
│   │   ├── utils/
│   │   │   └── nodeFactory.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key
- `GOOGLE_API_KEY` - Google Gemini API key
- `SERPAPI_API_KEY` - SerpAPI key (optional)
- `BRAVE_API_KEY` - Brave Search API key (optional)
- `SECRET_KEY` - Secret key for application
- `ENVIRONMENT` - Environment (development/production)

## 🚧 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check DATABASE_URL in .env file
   - Verify database exists

2. **API Key Errors**
   - Verify all required API keys are set in .env
   - Check API key validity

3. **Port Already in Use**
   - Change ports in docker-compose.yml
   - Or stop services using those ports

4. **ChromaDB Persistence**
   - ChromaDB data is stored in `./chroma_db`
   - Ensure write permissions

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on the repository.

## 🎓 Learning Resources

- [React Flow Documentation](https://reactflow.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

**Built with ❤️ using React, FastAPI, PostgreSQL, and ChromaDB**
