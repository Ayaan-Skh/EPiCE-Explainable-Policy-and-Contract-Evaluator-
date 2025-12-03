from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import sys
import os
from src.logger import logging
from src.exception import CustomException

class EmbeddingsManager:
    """
        Manages document embeddings and vector search.
        
        Key responsibilities:
        1. Generate embeddings using sentence-transformers
        2. Store embeddings in ChromaDB
        3. Perform semantic search
        4. Manage vector database persistence
    """
    def __init__(self,model_name:str="all-MiniLM-L6-v2",persist_directory:str="./models/vector_store"):
        try:    
            logging.info(f"Initializing the embeddings model")
            self.model=SentenceTransformer(model_name)
            logging.info(f"Loaded embeddings model: {model_name}")
            
            ##Loading chromadb Database
            logging.info("Initializating chromaDB")
            self.persist_directory = persist_directory
            os.makedirs(persist_directory,exist_ok=True)
            
            self.client=chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,  # Disable telemetry
                    allow_reset=True
                )
            )
            self.collection=None #Will be set when collection is created
            logging.info(f"Chromadb initialized at: {persist_directory}")
            
        except Exception as e:
            logging.error(f"Error initializing EmbeddingManager: {str(e)}")
            raise CustomException(sys,e)    
        
    def create_collection(
        self, 
        collection_name: str = "policy_documents",
        reset: bool = False
    ) -> chromadb.Collection:
        """
        Create or get existing collection.
        
        Args:
            collection_name: Name of the collection
            reset: If True, delete existing collection and create new one
        
        Returns:
            ChromaDB collection object
        """
        try:
            # Reset collection if requested
            if reset:
                try:
                    self.client.delete_collection(collection_name)
                    logging.info(f"Deleted existing collection: {collection_name}")
                except Exception:  # ← Changed: Don't capture 'e' here
                    pass  # Collection doesn't exist, that's fine
            
            # Try to get existing collection
            try:
                self.collection = self.client.get_collection(
                    name=collection_name,
                    embedding_function=None  # We'll provide embeddings manually
                )
                logging.info(f"✅ Loaded existing collection: {collection_name}")
                logging.info(f"   Collection has {self.collection.count()} documents")
                
            except Exception:  # ← Changed: Don't capture 'e' here either
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=collection_name,
                    embedding_function=None,
                    metadata={"description": "Insurance policy document chunks"}
                )
                logging.info(f"✅ Created new collection: {collection_name}")
            
            return self.collection
            
        except Exception as e:  # ← Only capture 'e' in the outer try-except
            logging.error(f"Error creating collection: {str(e)}")
            raise CustomException(sys, e)
            
    def generate_embeddings(self,text:List[str])->List[List[float]]:
        try:
            logging.info(f"Generating embeddings for text: {text}")
            # Generate embeddings
            # encode() returns numpy arrays, convert to lists for ChromaDB
            embedding=self.model.encode(
                text,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            #Convert array to List
            embeddings_list=embedding.tolist()
              
            logging.info(f"✅ Generated {len(embeddings_list)} embeddings")
            logging.info(f"   Embedding dimension: {len(embeddings_list[0])}")
            
            return embeddings_list
            
        except Exception as e:
            logging.error(f"Error generating embeddings: {str(e)}")
            raise CustomException(sys,e)                 
                
    def add_documents(self,chunks:List[Dict])->None:
        """
            Add document chunks to vector store.
            
            Args:
                chunks: List of chunk dictionaries with structure:
                    {
                        "id": "chunk_0",
                        "text": "document content...",
                        "section": "SECTION NAME",
                        "chunk_index": 0,
                        "char_start": 0,
                        "char_end": 500
                    }
            
            Process:
            1. Extract texts from chunks
            2. Generate embeddings
            3. Store in ChromaDB with metadata
        """
        try:
            if not self.collection:
                raise ValueError("Collection not initialized. Call create_collection() first")
            if not chunks:
                logging.info("No chunks to add")
                return

            logging.info(f"Adding {len(chunks)} documents to storage")

            # Extract components from each chunk (correctly reference each chunk)
            ids = [chunk.get('id', f'chunk_{i}') for i, chunk in enumerate(chunks)]
            texts = [chunk.get('text', '') for chunk in chunks]

            # Build metadata safely using .get and computed values
            metadatas = [
                {
                    "section": chunk.get('section'),
                    "chunk_index": chunk.get('chunk_index'),
                    "char_start": chunk.get('char_start'),
                    "char_end": chunk.get('char_end'),
                    "text_length": len(chunk.get('text', ''))
                }
                for chunk in chunks
            ]

            # Generate embeddings
            embeddings = self.generate_embeddings(texts)

            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            logging.info(f"✅ Successfully added {len(chunks)} documents to vector store")
            logging.info(f"   Total documents in collection: {self.collection.count()}")

        except Exception as e:
            logging.error(f"Error adding documents: {str(e)}")
            raise CustomException(sys, e)
    
    def search(self,
               query:str,
               top_k:int=3,
               filter_metadata:Optional[Dict]=None
               )->Dict:
        """
            Search for relevant chunks using semantic similarity.
            
            Args:
                query: Search query in natural language
                top_k: Number of results to return
                filter_metadata: Optional filters (e.g., {"section": "SURGICAL COVERAGE"})
            
            Returns:
                Dict containing:
                    - documents: List of retrieved text chunks
                    - metadatas: List of metadata for each chunk
                    - distances: List of similarity scores (lower = more similar)
                    - ids: List of chunk IDs
            
            How it works:
            1. Convert query to embedding
            2. Find top_k most similar embeddings in database
            3. Return corresponding documents
        """
        try:
            if not self.collection:
                raise ValueError("Collection not initialized. Call create_collection() first")
            logging.info(f"Searching for: '{query}' top_k={top_k}")
            
            #Generate Query embeddings
            query_embeddings=self.model.encode([query]).tolist()
            
            #Search in chromaDB
            results=self.collection.query(
                query_embeddings=query_embeddings,
                n_results=top_k,
                where=filter_metadata # Optional filtering
                )
            
            #Format Results
            formatted_results={
                "documents": results['documents'][0] if results['documents'] else [],
                "metadatas": results['metadatas'][0] if results['metadatas'] else [],
                "distances": results['distances'][0] if results['distances'] else [],
                "ids": results['ids'][0] if results['ids'] else []
            }  
            logging.info(f"✅ Found {len(formatted_results['documents'])} relevant documents")
            if formatted_results['documents']:
                logging.info(f"   Top result from section: {formatted_results['metadatas'][0].get('section', 'N/A')}")
                logging.info(f"   Distance score: {formatted_results['distances'][0]:.4f}")
            
            return formatted_results
            
        except Exception as e:
            logging.error(f"Error during search: {str(e)}")
            raise CustomException(sys, e)
        
        
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the vector database.
        
        Returns:
            Dict with collection statistics
        """
        try:
            if not self.collection:
                return {"error": "Collection not initialized"}
            
            count = self.collection.count()
            
            # Try to get sample to check sections
            sample = self.collection.peek(limit=min(10, count))
            sections = set()
            if sample and sample['metadatas']:
                sections = set(meta.get('section', 'Unknown') for meta in sample['metadatas'])
            
            stats = {
                "total_documents": count,
                "collection_name": self.collection.name,
                "persist_directory": self.persist_directory,
                "sample_sections": list(sections)
            }
            
            logging.info(f"Collection stats: {stats}")
            return stats
            
        except Exception as e:
            logging.error(f"Error getting stats: {str(e)}")
            return {"error": str(e)}
    
    def delete_collection(self, collection_name: str = "policy_documents") -> bool:
        """
        Delete a collection from the database.
        
        Args:
            collection_name: Name of collection to delete
            
        Returns:
            bool: True if successful
        """
        try:
            self.client.delete_collection(collection_name)
            logging.info(f"✅ Deleted collection: {collection_name}")
            self.collection = None
            return True
        except Exception as e:
            logging.error(f"Error deleting collection: {str(e)}")
            return False
        
        
                    
        
                
        
                    