import fitz  # PyMuPDF
import os
from typing import List, Dict
from app.services.embedding_service import EmbeddingService

class DocumentProcessor:
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """Split text into chunks with overlap"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "text": chunk_text,
                "index": len(chunks)
            })
        
        return chunks
    
    def process_document(self, file_path: str, knowledge_base_id: str, embedding_model: str = "openai",model_name=None) -> Dict:
        """Process document: extract text, chunk, and create embeddings"""
        # Extract text
        text = self.extract_text_from_pdf(file_path)
        
        # Chunk text
        chunks = self.chunk_text(text)
        
        # Create embeddings and store in vector DB
        embedding_ids = []
        for chunk in chunks:
            embedding_id = self.embedding_service.create_embedding(
                text=chunk["text"],
                knowledge_base_id=knowledge_base_id,
                metadata={"chunk_index": chunk["index"], "file_path": file_path},
                embedding_model=embedding_model,
                model_name=model_name
            )
            embedding_ids.append(embedding_id)
        
        return {
            "text": text,
            "chunks": chunks,
            "embedding_ids": embedding_ids,
            "total_chunks": len(chunks)
        }
