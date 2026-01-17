# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Docker and Docker Compose installed
- API keys (at minimum: OpenAI API key)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd workflow-builder

# Copy environment file
cp backend/.env.example backend/.env
```

### Step 2: Configure API Keys

Edit `backend/.env` and add your API keys:

```env
OPENAI_API_KEY=sk-your-key-here
GOOGLE_API_KEY=your-gemini-key-here  # Optional
SERPAPI_API_KEY=your-serpapi-key-here  # Optional
```

### Step 3: Start the Application

**On Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**On Windows:**
```bash
setup.bat
```

**Or manually:**
```bash
docker-compose up -d
```

### Step 4: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📝 Create Your First Workflow

### 1. Build a Simple Workflow

1. Open http://localhost:3000
2. Drag these components onto the canvas:
   - **User Query** (blue)
   - **LLM Engine** (purple)
   - **Output** (green)
3. Connect them: User Query → LLM Engine → Output
4. Click on **LLM Engine** and configure:
   - LLM Provider: OpenAI
   - Model: gpt-3.5-turbo
5. Enter a workflow name and click **Save & Chat**

### 2. Test the Workflow

1. In the chat interface, type: "What is artificial intelligence?"
2. The workflow will process your query and return a response

## 📚 Add Document Knowledge

### 1. Upload a Document

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@your_document.pdf" \
  -F "knowledge_base_id=my_kb" \
  -F "embedding_model=openai"
```

### 2. Update Your Workflow

1. Go back to the builder
2. Add a **Knowledge Base** component (orange)
3. Connect: User Query → Knowledge Base → LLM Engine → Output
4. Configure Knowledge Base:
   - Knowledge Base ID: `my_kb` (from upload)
   - Embedding Model: OpenAI
   - Top K Results: 5
5. Save and test with document-related questions

## 🎯 Example Workflows

### Workflow 1: Simple Q&A
```
User Query → LLM Engine → Output
```
**Use Case**: General questions, no document context needed

### Workflow 2: Document Q&A
```
User Query → Knowledge Base → LLM Engine → Output
```
**Use Case**: Answer questions based on uploaded documents

### Workflow 3: Web-Enhanced Q&A
```
User Query → LLM Engine (with web search) → Output
```
**Use Case**: Questions requiring current information from the web

### Workflow 4: Full Stack
```
User Query → Knowledge Base → LLM Engine (with web search) → Output
```
**Use Case**: Combine document knowledge with web information

## 🔧 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart
```

### API errors
- Verify API keys in `backend/.env`
- Restart backend: `docker-compose restart backend`

### Database connection issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View database logs
docker-compose logs postgres
```

## 📖 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Review [WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md) for flow diagrams

## 💡 Tips

1. **Start Simple**: Begin with basic workflows, then add complexity
2. **Test Incrementally**: Test each component as you add it
3. **Use Meaningful Names**: Name your workflows clearly
4. **Monitor Logs**: Check backend logs for debugging
5. **Save Often**: Save your workflows before testing

## 🆘 Need Help?

- Check the [README.md](README.md) for detailed information
- Review API documentation at http://localhost:8000/docs
- Check logs: `docker-compose logs -f`
