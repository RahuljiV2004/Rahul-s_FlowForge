from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from app.database import get_db
from app.models import Workflow
from app.services.workflow_executor import WorkflowExecutor

router = APIRouter()
executor = WorkflowExecutor()

class WorkflowCreate(BaseModel):
    name: str
    description: str = None
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class WorkflowUpdate(BaseModel):
    name: str = None
    description: str = None
    nodes: List[Dict[str, Any]] = None
    edges: List[Dict[str, Any]] = None
    is_active: bool = None

@router.post("/")
async def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    """Create a new workflow"""
    # Validate workflow
    validation_result = validate_workflow(workflow.nodes, workflow.edges)
    if not validation_result["valid"]:
        raise HTTPException(status_code=400, detail=validation_result["error"])
    
    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        nodes=workflow.nodes,
        edges=workflow.edges
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    
    return {
        "id": db_workflow.id,
        "name": db_workflow.name,
        "description": db_workflow.description,
        "nodes": db_workflow.nodes,
        "edges": db_workflow.edges,
        "created_at": db_workflow.created_at.isoformat() if db_workflow.created_at else None
    }

@router.get("/")
async def list_workflows(db: Session = Depends(get_db)):
    """List all workflows"""
    workflows = db.query(Workflow).all()
    return [
        {
            "id": wf.id,
            "name": wf.name,
            "description": wf.description,
            "is_active": wf.is_active,
            "created_at": wf.created_at.isoformat() if wf.created_at else None
        }
        for wf in workflows
    ]

@router.get("/{workflow_id}")
async def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Get a specific workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "nodes": workflow.nodes,
        "edges": workflow.edges,
        "is_active": workflow.is_active,
        "created_at": workflow.created_at.isoformat() if workflow.created_at else None
    }

@router.put("/{workflow_id}")
async def update_workflow(workflow_id: int, workflow_update: WorkflowUpdate, db: Session = Depends(get_db)):
    """Update a workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow_update.name is not None:
        workflow.name = workflow_update.name
    if workflow_update.description is not None:
        workflow.description = workflow_update.description
    if workflow_update.nodes is not None:
        workflow.nodes = workflow_update.nodes
    if workflow_update.edges is not None:
        workflow.edges = workflow_update.edges
    if workflow_update.is_active is not None:
        workflow.is_active = workflow_update.is_active
    
    # Validate if nodes/edges are updated
    if workflow_update.nodes is not None or workflow_update.edges is not None:
        validation_result = validate_workflow(workflow.nodes, workflow.edges)
        if not validation_result["valid"]:
            raise HTTPException(status_code=400, detail=validation_result["error"])
    
    db.commit()
    db.refresh(workflow)
    
    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "nodes": workflow.nodes,
        "edges": workflow.edges,
        "is_active": workflow.is_active
    }

@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Delete a workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    
    return {"message": "Workflow deleted successfully"}

@router.post("/{workflow_id}/validate")
async def validate_workflow_endpoint(workflow_id: int, db: Session = Depends(get_db)):
    """Validate a workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    validation_result = validate_workflow(workflow.nodes, workflow.edges)
    return validation_result

def validate_workflow(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """Validate workflow structure"""
    if not nodes:
        return {"valid": False, "error": "Workflow must contain at least one node"}
    
    # Check for required components
    node_types = [node.get("type") for node in nodes]
    
    if "userQuery" not in node_types:
        return {"valid": False, "error": "Workflow must contain a User Query component"}
    
    if "llmEngine" not in node_types:
        return {"valid": False, "error": "Workflow must contain an LLM Engine component"}
    
    if "output" not in node_types:
        return {"valid": False, "error": "Workflow must contain an Output component"}
    
    # Check connectivity
    node_ids = {node["id"] for node in nodes}
    edge_sources = {edge["source"] for edge in edges}
    edge_targets = {edge["target"] for edge in edges}
    
    # All edge sources and targets must be valid node IDs
    if not (edge_sources.issubset(node_ids) and edge_targets.issubset(node_ids)):
        return {"valid": False, "error": "All edges must connect valid nodes"}
    
    # Check for cycles (simple check - can be enhanced)
    # For now, we'll allow cycles but warn about them
    
    return {"valid": True, "error": None}
