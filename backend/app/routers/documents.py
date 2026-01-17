from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document
from app.services.document_processor import DocumentProcessor
import os
import uuid
from typing import List, Optional

router = APIRouter()
processor = DocumentProcessor()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_available_embedding_models():
    """Get list of available embedding models based on configured API keys"""
    available = []
    
    if os.getenv("OPENAI_API_KEY"):
        available.append("openai")
    if os.getenv("GOOGLE_API_KEY"):
        available.append("gemini")
    if os.getenv("COHERE_API_KEY"):
        available.append("cohere")
    
    return available

def get_default_embedding_model():
    """Detect which embedding model to use based on available API keys"""
    available = get_available_embedding_models()
    
    if not available:
        raise HTTPException(
            status_code=500,
            detail="No embedding API keys configured. Please set at least one of: OPENAI_API_KEY, GOOGLE_API_KEY, COHERE_API_KEY"
        )
    
    # Priority order: Cohere > OpenAI > Gemini (you can change this)
    if "cohere" in available:
        return "cohere"
    elif "openai" in available:
        return "openai"
    elif "gemini" in available:
        return "gemini"
    
    return available[0]

@router.get("/embedding-models")
async def list_embedding_models():
    """List available embedding models"""
    available = get_available_embedding_models()
    default = get_default_embedding_model() if available else None
    
    return {
        "available_models": available,
        "default_model": default,
        "models_info": {
            "openai": {
                "name": "OpenAI",
                "models": ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
                "default": "text-embedding-3-small",
                "available": "openai" in available
            },
            "gemini": {
                "name": "Google Gemini",
                "models": ["models/embedding-001"],
                "default": "models/embedding-001",
                "available": "gemini" in available
            },
            "cohere": {
                "name": "Cohere",
                "models": [
                    "embed-english-v3.0",
                    "embed-multilingual-v3.0",
                    "embed-english-light-v3.0",
                    "embed-multilingual-light-v3.0"
                ],
                "default": "embed-english-v3.0",
                "available": "cohere" in available
            }
        }
    }

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    knowledge_base_id: Optional[str] = None,
    embedding_model: Optional[str] = Query(None, description="Embedding model: openai, gemini, or cohere"),
    model_name: Optional[str] = Query(None, description="Specific model name (optional)"),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document
    
    Parameters:
    - file: PDF file to upload
    - knowledge_base_id: Optional knowledge base ID (auto-generated if not provided)
    - embedding_model: Provider to use (openai/gemini/cohere) - auto-detected if not provided
    - model_name: Specific model name (optional, uses provider default if not specified)
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Use provided embedding model or detect default based on available API keys
    if embedding_model is None:
        embedding_model = get_default_embedding_model()
    else:
        # Validate the provided embedding model
        available = get_available_embedding_models()
        if embedding_model not in available:
            raise HTTPException(
                status_code=400,
                detail=f"Embedding model '{embedding_model}' is not available. Available models: {available}"
            )
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    # Save file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create database record
    db_document = Document(
        filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type,
        knowledge_base_id=knowledge_base_id or file_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Process document
    try:
        result = processor.process_document(
            file_path=file_path,
            knowledge_base_id=db_document.knowledge_base_id,
            embedding_model=embedding_model,
            model_name=model_name
        )
        
        db_document.processed = True
        db.commit()
        
        return {
            "id": db_document.id,
            "filename": db_document.filename,
            "knowledge_base_id": db_document.knowledge_base_id,
            "processed": True,
            "chunks": result["total_chunks"],
            "embedding_model": embedding_model,
            "model_name": model_name or "default"
        }
    except Exception as e:
        db_document.processed = False
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.post("/batch-upload")
async def batch_upload_documents(
    files: List[UploadFile] = File(...),
    knowledge_base_id: Optional[str] = None,
    embedding_model: Optional[str] = Query(None, description="Embedding model: openai, gemini, or cohere"),
    model_name: Optional[str] = Query(None, description="Specific model name (optional)"),
    db: Session = Depends(get_db)
):
    """
    Upload and process multiple documents in batch
    
    All documents will be added to the same knowledge base for efficient retrieval
    """
    # Validate embedding model
    if embedding_model is None:
        embedding_model = get_default_embedding_model()
    else:
        available = get_available_embedding_models()
        if embedding_model not in available:
            raise HTTPException(
                status_code=400,
                detail=f"Embedding model '{embedding_model}' is not available. Available models: {available}"
            )
    
    # Use same knowledge base for all files or generate one
    kb_id = knowledge_base_id or str(uuid.uuid4())
    
    results = []
    errors = []
    
    for file in files:
        if not file.filename.endswith('.pdf'):
            errors.append({
                "filename": file.filename,
                "error": "Only PDF files are supported"
            })
            continue
        
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
            
            # Save file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # Create database record
            db_document = Document(
                filename=file.filename,
                file_path=file_path,
                file_size=len(content),
                mime_type=file.content_type,
                knowledge_base_id=kb_id
            )
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            
            # Process document
            result = processor.process_document(
                file_path=file_path,
                knowledge_base_id=kb_id,
                embedding_model=embedding_model,
                model_name=model_name
            )
            
            db_document.processed = True
            db.commit()
            
            results.append({
                "id": db_document.id,
                "filename": db_document.filename,
                "chunks": result["total_chunks"],
                "status": "success"
            })
            
        except Exception as e:
            if 'db_document' in locals():
                db_document.processed = False
                db.commit()
            
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "knowledge_base_id": kb_id,
        "embedding_model": embedding_model,
        "model_name": model_name or "default",
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

@router.get("/")
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    knowledge_base_id: Optional[str] = None,
    processed_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    List all documents with optional filtering
    
    Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    - knowledge_base_id: Filter by knowledge base ID
    - processed_only: Show only processed documents
    """
    query = db.query(Document)
    
    if knowledge_base_id:
        query = query.filter(Document.knowledge_base_id == knowledge_base_id)
    
    if processed_only:
        query = query.filter(Document.processed == True)
    
    total = query.count()
    documents = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "knowledge_base_id": doc.knowledge_base_id,
                "processed": doc.processed,
                "file_size": doc.file_size,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None
            }
            for doc in documents
        ]
    }

@router.get("/knowledge-bases")
async def list_knowledge_bases(db: Session = Depends(get_db)):
    """List all unique knowledge bases with document counts"""
    from sqlalchemy import func
    
    results = db.query(
        Document.knowledge_base_id,
        func.count(Document.id).label('document_count'),
        func.sum(func.case((Document.processed == True, 1), else_=0)).label('processed_count')
    ).group_by(Document.knowledge_base_id).all()
    
    return {
        "knowledge_bases": [
            {
                "id": kb_id,
                "document_count": doc_count,
                "processed_count": processed_count,
                "processing_complete": doc_count == processed_count
            }
            for kb_id, doc_count, processed_count in results
        ]
    }

@router.get("/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document with detailed information"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "filename": document.filename,
        "knowledge_base_id": document.knowledge_base_id,
        "processed": document.processed,
        "file_size": document.file_size,
        "mime_type": document.mime_type,
        "file_path": document.file_path,
        "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None
    }

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    delete_embeddings: bool = Query(True, description="Also delete embeddings from knowledge base"),
    db: Session = Depends(get_db)
):
    """
    Delete a document
    
    Parameters:
    - document_id: ID of the document to delete
    - delete_embeddings: Whether to also delete the embeddings (default: True)
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete embeddings if requested
    if delete_embeddings:
        try:
            # This would require additional implementation in document_processor
            # to track which embeddings belong to which document
            pass
        except Exception as e:
            # Log error but continue with file deletion
            print(f"Error deleting embeddings: {str(e)}")
    
    # Delete file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    db.delete(document)
    db.commit()
    
    return {
        "message": "Document deleted successfully",
        "id": document_id,
        "filename": document.filename
    }

@router.delete("/knowledge-base/{knowledge_base_id}")
async def delete_knowledge_base(
    knowledge_base_id: str,
    delete_files: bool = Query(True, description="Also delete document files"),
    db: Session = Depends(get_db)
):
    """
    Delete all documents in a knowledge base
    
    Parameters:
    - knowledge_base_id: ID of the knowledge base
    - delete_files: Whether to delete the actual files (default: True)
    """
    documents = db.query(Document).filter(Document.knowledge_base_id == knowledge_base_id).all()
    
    if not documents:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    deleted_count = 0
    errors = []
    
    for document in documents:
        try:
            # Delete file if requested
            if delete_files and os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            db.delete(document)
            deleted_count += 1
        except Exception as e:
            errors.append({
                "document_id": document.id,
                "filename": document.filename,
                "error": str(e)
            })
    
    db.commit()
    
    # Delete embeddings from ChromaDB
    try:
        from app.services.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()
        embedding_service.delete_collection(knowledge_base_id)
    except Exception as e:
        errors.append({
            "error": f"Failed to delete embeddings: {str(e)}"
        })
    
    return {
        "message": f"Deleted {deleted_count} documents from knowledge base",
        "knowledge_base_id": knowledge_base_id,
        "deleted_count": deleted_count,
        "errors": errors if errors else None
    }

@router.get("/stats/overview")
async def get_stats_overview(db: Session = Depends(get_db)):
    """Get overall statistics about documents and knowledge bases"""
    from sqlalchemy import func
    
    total_documents = db.query(func.count(Document.id)).scalar()
    processed_documents = db.query(func.count(Document.id)).filter(Document.processed == True).scalar()
    total_size = db.query(func.sum(Document.file_size)).scalar() or 0
    knowledge_base_count = db.query(func.count(func.distinct(Document.knowledge_base_id))).scalar()
    
    return {
        "total_documents": total_documents,
        "processed_documents": processed_documents,
        "pending_documents": total_documents - processed_documents,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "knowledge_base_count": knowledge_base_count,
        "available_embedding_models": get_available_embedding_models(),
        "default_embedding_model": get_default_embedding_model()
    }