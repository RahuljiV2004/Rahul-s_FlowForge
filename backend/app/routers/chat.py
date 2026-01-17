from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.database import get_db
from app.models import Workflow, ChatSession, ChatMessage
from app.services.workflow_executor import WorkflowExecutor
import uuid
from datetime import datetime

router = APIRouter()
executor = WorkflowExecutor()

class ChatRequest(BaseModel):
    query: str
    workflow_id: int
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    execution_log: List[Dict]

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest, db: Session = Depends(get_db)):
    """Process a chat query through a workflow"""
    # Get workflow
    workflow = db.query(Workflow).filter(Workflow.id == request.workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if not workflow.is_active:
        raise HTTPException(status_code=400, detail="Workflow is not active")
    
    # Get or create session
    session_id = request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        db_session = ChatSession(
            workflow_id=workflow.id,
            session_id=session_id
        )
        db.add(db_session)
        db.commit()
    else:
        db_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")
    
    # Save user message
    user_message = ChatMessage(
        session_id=db_session.id,
        role="user",
        content=request.query
    )
    db.add(user_message)
    db.commit()
    
    # Get chat history
    previous_messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == db_session.id
    ).order_by(ChatMessage.created_at).all()
    
    chat_history = [
        {"role": msg.role, "content": msg.content}
        for msg in previous_messages
    ]
    
    # Execute workflow
    try:
        result = executor.execute_workflow(
            nodes=workflow.nodes,
            edges=workflow.edges,
            query=request.query,
            chat_history=chat_history
        )
        
        # Save assistant message
        assistant_message = ChatMessage(
            session_id=db_session.id,
            role="assistant",
            content=result["result"],
            message_metadata={"execution_log": result["execution_log"]}
        )
        db.add(assistant_message)
        db.commit()
        
        return ChatResponse(
            response=result["result"],
            session_id=session_id,
            execution_log=result["execution_log"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing workflow: {str(e)}")

@router.get("/sessions/{session_id}/history")
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for a session"""
    db_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == db_session.id
    ).order_by(ChatMessage.created_at).all()
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "metadata": msg.message_metadata,
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        }
        for msg in messages
    ]

@router.get("/sessions")
async def list_sessions(workflow_id: Optional[int] = None, db: Session = Depends(get_db)):
    """List chat sessions"""
    query = db.query(ChatSession)
    if workflow_id:
        query = query.filter(ChatSession.workflow_id == workflow_id)
    
    sessions = query.all()
    
    return [
        {
            "id": session.id,
            "session_id": session.session_id,
            "workflow_id": session.workflow_id,
            "created_at": session.created_at.isoformat() if session.created_at else None
        }
        for session in sessions
    ]

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session"""
    db_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(db_session)
    db.commit()
    
    return {"message": "Session deleted successfully"}
