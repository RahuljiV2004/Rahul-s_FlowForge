from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import documents, workflows, chat, embeddings
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Workflow Builder API",
    description="No-Code/Low-Code Workflow Builder Backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(embeddings.router, prefix="/api/embeddings", tags=["embeddings"])

@app.get("/")
async def root():
    return {"message": "Workflow Builder API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
