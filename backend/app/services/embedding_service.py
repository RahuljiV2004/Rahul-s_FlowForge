
import chromadb
import os
from typing import List, Dict, Optional
from openai import OpenAI
import google.generativeai as genai
import cohere
from dotenv import load_dotenv
import uuid

load_dotenv()

class EmbeddingService:
    def __init__(self, chroma_db_path: str = "./chroma_db"):
        """
        Initialize the EmbeddingService with support for multiple embedding providers.
        
        Args:
            chroma_db_path: Path to store ChromaDB data
        """
        # Initialize ChromaDB with new API
        self.chroma_client = chromadb.PersistentClient(path=chroma_db_path)
        
        # Initialize OpenAI only if API key is provided
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
        else:
            self.openai_client = None
        
        # Initialize Google Gemini only if API key is provided
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            genai.configure(api_key=google_key)
        self.google_key = google_key
        
        # Initialize Cohere only if API key is provided
        cohere_key = os.getenv("COHERE_API_KEY")
        if cohere_key:
            self.cohere_client = cohere.Client(api_key=cohere_key)
        else:
            self.cohere_client = None
    
    def get_or_create_collection(self, knowledge_base_id: str):
        """Get or create a ChromaDB collection"""
        try:
            collection = self.chroma_client.get_collection(name=knowledge_base_id)
        except:
            collection = self.chroma_client.create_collection(name=knowledge_base_id)
        return collection
    
    def create_embedding_openai(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """
        Create embedding using OpenAI.
        
        Args:
            text: Text to embed
            model: OpenAI embedding model to use
                  - text-embedding-3-small (default, 1536 dimensions)
                  - text-embedding-3-large (3072 dimensions)
                  - text-embedding-ada-002 (1536 dimensions, legacy)
        
        Returns:
            List of float values representing the embedding
        """
        if not self.openai_client:
            raise ValueError("OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable.")
        
        response = self.openai_client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    
    def create_embedding_gemini(self, text: str, model: str = "models/embedding-001") -> List[float]:
        """
        Create embedding using Google Gemini.
        
        Args:
            text: Text to embed
            model: Gemini embedding model to use
        
        Returns:
            List of float values representing the embedding
        """
        if not self.google_key:
            raise ValueError("Google API key is not configured. Please set GOOGLE_API_KEY environment variable.")
        
        try:
            # Use the embedding model
            result = genai.embed_content(
                model=model,
                content=text,
                task_type="retrieval_document"
            )
            # Adjust based on actual response structure
            if isinstance(result, dict) and 'embedding' in result:
                return result['embedding']
            elif hasattr(result, 'embedding'):
                return result['embedding']
            else:
                raise ValueError("Unexpected response format from Gemini embedding API")
        except Exception as e:
            # Re-raise with clearer error message
            raise Exception(f"Gemini embedding error: {str(e)}")
    
    def create_embedding_cohere(self, text: str, model: str = "embed-english-v3.0", input_type: str = "search_document") -> List[float]:
        """
        Create embedding using Cohere.
        
        Args:
            text: Text to embed
            model: Cohere embedding model to use
                  - embed-english-v3.0 (default, 1024 dimensions)
                  - embed-multilingual-v3.0 (1024 dimensions)
                  - embed-english-light-v3.0 (384 dimensions)
                  - embed-multilingual-light-v3.0 (384 dimensions)
            input_type: Type of input for embedding
                       - "search_document" (default, for storing documents)
                       - "search_query" (for search queries)
                       - "classification" (for classification tasks)
                       - "clustering" (for clustering tasks)
        
        Returns:
            List of float values representing the embedding
        """
        if not self.cohere_client:
            raise ValueError("Cohere API key is not configured. Please set COHERE_API_KEY environment variable.")
        
        try:
            response = self.cohere_client.embed(
                texts=[text],
                model=model,
                input_type=input_type
            )
            return response.embeddings[0]
        except Exception as e:
            raise Exception(f"Cohere embedding error: {str(e)}")
    
    def create_embedding(self, text: str, knowledge_base_id: str, metadata: Dict, 
                        embedding_model: str = "openai", model_name: Optional[str] = None) -> str:
        """
        Create embedding and store in ChromaDB.
        
        Args:
            text: Text to embed and store
            knowledge_base_id: ID of the knowledge base collection
            metadata: Metadata to store with the embedding
            embedding_model: Provider to use ("openai", "gemini", or "cohere")
            model_name: Specific model name (optional, uses defaults if not provided)
        
        Returns:
            Unique ID of the created embedding
        """
        # Generate embedding
        if embedding_model == "openai":
            if model_name:
                embedding = self.create_embedding_openai(text, model=model_name)
            else:
                embedding = self.create_embedding_openai(text)
        elif embedding_model == "gemini":
            if model_name:
                embedding = self.create_embedding_gemini(text, model=model_name)
            else:
                embedding = self.create_embedding_gemini(text)
        elif embedding_model == "cohere":
            if model_name:
                embedding = self.create_embedding_cohere(text, model=model_name)
            else:
                embedding = self.create_embedding_cohere(text)
        else:
            raise ValueError(f"Unsupported embedding model: {embedding_model}. Supported: openai, gemini, cohere")
        
        # Get or create collection
        collection = self.get_or_create_collection(knowledge_base_id)
        
        # Generate unique ID
        embedding_id = str(uuid.uuid4())
        
        # Add embedding model info to metadata
        metadata_with_model = metadata.copy()
        metadata_with_model['embedding_model'] = embedding_model
        if model_name:
            metadata_with_model['model_name'] = model_name
        
        # Add to collection
        collection.add(
            ids=[embedding_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata_with_model]
        )
        
        return embedding_id
    
    def search_similar(self, query: str, knowledge_base_id: str, top_k: int = 5, 
                      embedding_model: str = "openai", model_name: Optional[str] = None,
                      filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar documents in the knowledge base.
        
        Args:
            query: Search query text
            knowledge_base_id: ID of the knowledge base collection
            top_k: Number of results to return
            embedding_model: Provider to use for query embedding ("openai", "gemini", or "cohere")
            model_name: Specific model name (optional)
            filter_metadata: Optional metadata filter for results
        
        Returns:
            List of dictionaries containing search results
        """
        # Generate query embedding with appropriate input type for Cohere
        if embedding_model == "openai":
            if model_name:
                query_embedding = self.create_embedding_openai(query, model=model_name)
            else:
                query_embedding = self.create_embedding_openai(query)
        elif embedding_model == "gemini":
            if model_name:
                query_embedding = self.create_embedding_gemini(query, model=model_name)
            else:
                query_embedding = self.create_embedding_gemini(query)
        elif embedding_model == "cohere":
            # Use "search_query" input type for search queries
            if model_name:
                query_embedding = self.create_embedding_cohere(query, model=model_name, input_type="search_query")
            else:
                query_embedding = self.create_embedding_cohere(query, input_type="search_query")
        else:
            raise ValueError(f"Unsupported embedding model: {embedding_model}. Supported: openai, gemini, cohere")
        
        # Get collection
        try:
            collection = self.get_or_create_collection(knowledge_base_id)
        except:
            return []
        
        # Build query parameters
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": top_k
        }
        
        # Add metadata filter if provided
        if filter_metadata:
            query_params["where"] = filter_metadata
        
        # Search
        results = collection.query(**query_params)
        
        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def batch_create_embeddings(self, texts: List[str], knowledge_base_id: str, 
                               metadatas: List[Dict], embedding_model: str = "openai",
                               model_name: Optional[str] = None) -> List[str]:
        """
        Create multiple embeddings in batch.
        
        Args:
            texts: List of texts to embed
            knowledge_base_id: ID of the knowledge base collection
            metadatas: List of metadata dictionaries (one per text)
            embedding_model: Provider to use ("openai", "gemini", or "cohere")
            model_name: Specific model name (optional)
        
        Returns:
            List of unique IDs for created embeddings
        """
        if len(texts) != len(metadatas):
            raise ValueError("Number of texts must match number of metadata entries")
        
        # Generate all embeddings
        embeddings = []
        for text in texts:
            if embedding_model == "openai":
                if model_name:
                    embedding = self.create_embedding_openai(text, model=model_name)
                else:
                    embedding = self.create_embedding_openai(text)
            elif embedding_model == "gemini":
                if model_name:
                    embedding = self.create_embedding_gemini(text, model=model_name)
                else:
                    embedding = self.create_embedding_gemini(text)
            elif embedding_model == "cohere":
                if model_name:
                    embedding = self.create_embedding_cohere(text, model=model_name)
                else:
                    embedding = self.create_embedding_cohere(text)
            else:
                raise ValueError(f"Unsupported embedding model: {embedding_model}")
            embeddings.append(embedding)
        
        # Get or create collection
        collection = self.get_or_create_collection(knowledge_base_id)
        
        # Generate unique IDs
        embedding_ids = [str(uuid.uuid4()) for _ in texts]
        
        # Add embedding model info to all metadata
        metadatas_with_model = []
        for metadata in metadatas:
            metadata_copy = metadata.copy()
            metadata_copy['embedding_model'] = embedding_model
            if model_name:
                metadata_copy['model_name'] = model_name
            metadatas_with_model.append(metadata_copy)
        
        # Add all to collection
        collection.add(
            ids=embedding_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas_with_model
        )
        
        return embedding_ids
    
    def delete_embedding(self, knowledge_base_id: str, embedding_id: str) -> bool:
        """
        Delete an embedding from the knowledge base.
        
        Args:
            knowledge_base_id: ID of the knowledge base collection
            embedding_id: ID of the embedding to delete
        
        Returns:
            True if successful
        """
        try:
            collection = self.get_or_create_collection(knowledge_base_id)
            collection.delete(ids=[embedding_id])
            return True
        except Exception as e:
            print(f"Error deleting embedding: {str(e)}")
            return False
    
    def delete_collection(self, knowledge_base_id: str) -> bool:
        """
        Delete an entire knowledge base collection.
        
        Args:
            knowledge_base_id: ID of the knowledge base collection to delete
        
        Returns:
            True if successful
        """
        try:
            self.chroma_client.delete_collection(name=knowledge_base_id)
            return True
        except Exception as e:
            print(f"Error deleting collection: {str(e)}")
            return False
    
    def get_collection_count(self, knowledge_base_id: str) -> int:
        """
        Get the number of embeddings in a collection.
        
        Args:
            knowledge_base_id: ID of the knowledge base collection
        
        Returns:
            Number of embeddings in the collection
        """
        try:
            collection = self.get_or_create_collection(knowledge_base_id)
            return collection.count()
        except:
            return 0
    
    def get_available_embedding_providers(self) -> List[str]:
        """
        Get list of available embedding providers based on configured API keys.
        
        Returns:
            List of available provider names
        """
        providers = []
        if self.openai_client:
            providers.append("openai")
        if self.google_key:
            providers.append("gemini")
        if self.cohere_client:
            providers.append("cohere")
        return providers
    
    def is_provider_available(self, provider: str) -> bool:
        """
        Check if a specific embedding provider is available.
        
        Args:
            provider: Provider name to check
        
        Returns:
            True if provider is available
        """
        return provider in self.get_available_embedding_providers()