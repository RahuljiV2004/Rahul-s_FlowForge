from typing import Dict, List, Any
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService

class WorkflowExecutor:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
    
    def find_node_by_type(self, nodes: List[Dict], node_type: str) -> Dict:
        """Find a node by its type"""
        for node in nodes:
            if node.get("type") == node_type:
                return node
        return None
    
    def find_connected_nodes(self, edges: List[Dict], source_id: str) -> List[str]:
        """Find all nodes connected from a source node"""
        connected = []
        for edge in edges:
            if edge.get("source") == source_id:
                connected.append(edge.get("target"))
        return connected
    
    def execute_workflow(self, nodes: List[Dict], edges: List[Dict], query: str, chat_history: List[Dict] = None) -> Dict:
        """Execute a workflow given nodes, edges, and a query"""
        execution_log = []
        result = None
        
        # Find User Query component (entry point)
        user_query_node = self.find_node_by_type(nodes, "userQuery")
        if not user_query_node:
            raise ValueError("Workflow must contain a User Query component")
        
        current_node = user_query_node
        current_data = {"query": query}
        
        execution_log.append({
            "step": "user_query",
            "node_id": current_node["id"],
            "data": current_data
        })
        
        # Traverse the workflow
        visited = set()
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        while current_node and iteration < max_iterations:
            iteration += 1
            node_id = current_node["id"]
            
            if node_id in visited:
                break
            visited.add(node_id)
            
            node_type = current_node.get("type")
            node_data = current_node.get("data", {})
            
            # Process based on node type
            if node_type == "userQuery":
                # Already processed, just pass data forward
                pass
            
            elif node_type == "knowledgeBase":
                # Retrieve context from knowledge base
                kb_id = node_data.get("knowledgeBaseId")
                embedding_model = node_data.get("embeddingModel", "openai")
                top_k = node_data.get("topK", 5)
                
                if kb_id and current_data.get("query"):
                    similar_docs = self.embedding_service.search_similar(
                        query=current_data["query"],
                        knowledge_base_id=kb_id,
                        top_k=top_k,
                        embedding_model=embedding_model
                    )
                    
                    # Combine context
                    context = "\n\n".join([doc["text"] for doc in similar_docs])
                    current_data["context"] = context
                    
                    execution_log.append({
                        "step": "knowledge_base",
                        "node_id": node_id,
                        "context_chunks": len(similar_docs),
                        "context_length": len(context)
                    })
            
            elif node_type == "llmEngine":
                # Generate LLM response
                llm_provider = node_data.get("llmProvider", "openai")
                custom_prompt = node_data.get("customPrompt")
                use_web_search = node_data.get("useWebSearch", False)
                web_search_provider = node_data.get("webSearchProvider")
                model = node_data.get("model", "gpt-3.5-turbo")
                
                query_text = current_data.get("query", "")
                context = current_data.get("context")
                
                # Include chat history if available
                if chat_history:
                    history_context = "\n".join([
                        f"{msg['role']}: {msg['content']}" 
                        for msg in chat_history[-5:]  # Last 5 messages
                    ])
                    if context:
                        context = f"{context}\n\nChat History:\n{history_context}"
                    else:
                        context = f"Chat History:\n{history_context}"
                
                llm_response = self.llm_service.generate_with_web_search(
                    query=query_text,
                    llm_provider=llm_provider,
                    context=context,
                    custom_prompt=custom_prompt,
                    web_search_provider=web_search_provider if use_web_search else None
                )
                
                current_data["response"] = llm_response["response"]
                result = llm_response["response"]
                
                execution_log.append({
                    "step": "llm_engine",
                    "node_id": node_id,
                    "provider": llm_provider,
                    "web_search_used": llm_response["web_context_used"],
                    "context_used": llm_response["context_used"]
                })
            
            elif node_type == "output":
                # Output component - final result
                result = current_data.get("response", current_data.get("query", ""))
                execution_log.append({
                    "step": "output",
                    "node_id": node_id,
                    "result": result[:100] + "..." if len(str(result)) > 100 else result
                })
                break
            
            # Find next connected node
            connected_node_ids = self.find_connected_nodes(edges, node_id)
            if connected_node_ids:
                next_node_id = connected_node_ids[0]  # Take first connection
                current_node = next((n for n in nodes if n["id"] == next_node_id), None)
            else:
                break
        
        if not result:
            result = "Workflow execution completed but no output was generated."
        
        return {
            "result": result,
            "execution_log": execution_log,
            "success": True
        }
