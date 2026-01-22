"""
RAG-based chat engine for follow-up questions about scraped content
Uses ChromaDB for vector storage and retrieval
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict
from backend.ai.ai_provider import ai_provider
import hashlib

class ChatEngine:
    """RAG-based chat system for scraped content"""
    
    def __init__(self):
        # Initialize ChromaDB
        self.client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # Store collections per project
        self.collections = {}
    
    def _get_collection_name(self, project_id: int) -> str:
        """Generate collection name for a project"""
        return f"project_{project_id}"
    
    def _get_or_create_collection(self, project_id: int):
        """Get or create a collection for a project"""
        collection_name = self._get_collection_name(project_id)
        
        if collection_name not in self.collections:
            try:
                self.collections[collection_name] = self.client.get_or_create_collection(
                    name=collection_name
                )
            except Exception as e:
                print(f"Error creating collection: {e}")
                # Try to delete and recreate
                try:
                    self.client.delete_collection(collection_name)
                except:
                    pass
                self.collections[collection_name] = self.client.create_collection(
                    name=collection_name
                )
        
        return self.collections[collection_name]
    
    def add_content(self, project_id: int, content: str, metadata: Dict = None):
        """Add scraped content to the vector database"""
        
        collection = self._get_or_create_collection(project_id)
        
        # Split content into chunks (simple chunking by paragraphs)
        chunks = self._chunk_text(content)
        
        # Add chunks to collection
        for i, chunk in enumerate(chunks):
            # Create unique ID
            chunk_id = hashlib.md5(f"{project_id}_{i}_{chunk[:50]}".encode()).hexdigest()
            
            try:
                collection.add(
                    documents=[chunk],
                    ids=[chunk_id],
                    metadatas=[metadata or {}]
                )
            except Exception as e:
                print(f"Error adding chunk {i}: {e}")
    
    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks"""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text[:chunk_size]]
    
    def chat(
        self, 
        project_id: int, 
        question: str, 
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Answer a question about the scraped content
        Uses RAG to retrieve relevant context
        """
        
        collection = self._get_or_create_collection(project_id)
        
        try:
            # Retrieve relevant chunks
            results = collection.query(
                query_texts=[question],
                n_results=3
            )
            
            # Extract relevant context
            if results['documents'] and results['documents'][0]:
                context = "\n\n".join(results['documents'][0])
            else:
                context = "No relevant content found."
            
        except Exception as e:
            print(f"Error querying collection: {e}")
            context = "Error retrieving content."
        
        # Build conversation context
        conversation_context = ""
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                conversation_context += f"{role}: {content}\n"
        
        # Create prompt
        system_prompt = """You are a helpful assistant that answers questions about scraped web content.
Use the provided context to answer questions accurately. If the answer is not in the context, say so.
Be concise but informative."""
        
        user_prompt = f"""Context from scraped content:
{context}

Previous conversation:
{conversation_context}

User question: {question}

Answer:"""
        
        try:
            # Generate response
            response = ai_provider.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
                temperature=0.5
            )
            
            return response.strip()
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def clear_project_data(self, project_id: int):
        """Clear all data for a project"""
        collection_name = self._get_collection_name(project_id)
        try:
            self.client.delete_collection(collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
        except Exception as e:
            print(f"Error clearing project data: {e}")

# Global instance
chat_engine = ChatEngine()
