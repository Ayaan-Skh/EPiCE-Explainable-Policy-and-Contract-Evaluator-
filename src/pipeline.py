import sys,time,json
from src.logger import logging
from src.document_processor import DocumentProcessor
from src.query_parser import Query_parser
from src.decision_engine import DecisionEngine
from src.embeddings import EmbeddingsManager
from src.exception import CustomException
from typing import Dict,List,Optional
from pathlib import Path

class InsuranceQAPipeline:
    """"
        End to end pipeline for insurance claimaing process and decision making.
        Flow:
        1.setup: Load documents->Chunk->Embed->Store in vector DB
        2. Query: Parse->Search->Decide->Return structured response
    Usage:
    
        pipeline=InsuranceQAPipeline()
        pipeline.setup("data/raw/insurance_policy.txt")
        result= pipeline.process_query("46 knee surgery Pune 3 months policy")
    
    """
    def __init__(self,vector_db_path:str="policy_documents"):
        """
        Initialize pipeline with all components.
        
        Args:
            vector_db_path: Path to persist vector database
        """
        try:
            logging.info("Initializing InsuranceQAPipeline...")
            
            # Initialize all components
            self.doc_processor = DocumentProcessor()
            self.embedding_manager = EmbeddingsManager(persist_directory=vector_db_path)
            self.query_parser = Query_parser()
            self.decision_engine = DecisionEngine()
            
            # State tracking
            self.is_setup = False
            self.total_documents = 0
            self.collection_name = "policy_documents"
            
            logging.info("✅ Pipeline initialized successfully")
            logging.info(f"   LLM Provider: {self.decision_engine.provider}")
            logging.info(f"   LLM Model: {self.decision_engine.model}")
            
        except Exception as e:
            logging.error(f"Error initializing pipeline: {str(e)}")
            raise CustomException(sys, e)
    
    def setup(
        self, 
        document_path: str,
        reset: bool = False,
        save_chunks: bool = True
    ) -> Dict:
        """
        One-time setup: Process documents and create vector database.
        
        Args:
            document_path: Path to policy document
            reset: If True, recreate vector database from scratch
            save_chunks: If True, save chunks to JSON file
        
        Returns:
            Dict with setup statistics
        """
        try:
            start_time = time.time()
            logging.info("="*80)
            logging.info("STARTING PIPELINE SETUP")
            logging.info("="*80)
            
            # Step 1: Load document
            logging.info("\n📄 Step 1: Loading document...")
            text = self.doc_processor.load_documents(document_path)
            logging.info(f"   ✓ Loaded {len(text)} characters")
            
            # Step 2: Chunk document
            logging.info("\n✂️  Step 2: Chunking document...")
            chunks = self.doc_processor.chunk_document(text)
            logging.info(f"   ✓ Created {len(chunks)} chunks")
            
            # Validate chunks
            is_valid = self.doc_processor.validate_chunks(chunks)
            if not is_valid:
                raise ValueError("Chunk validation failed")
            logging.info(f"   ✓ Chunks validated")
            
            # Get statistics
            stats = self.doc_processor.get_chunk_statistics(chunks)
            logging.info(f"   ✓ Avg chunk length: {stats['avg_chunk_length']:.0f} chars")
            
            # Save chunks if requested
            if save_chunks:
                chunks_path = Path("data/processed/chunks.json")
                chunks_path.parent.mkdir(parents=True, exist_ok=True)
                with open(chunks_path, 'w') as f:
                    json.dump(chunks, f, indent=2)
                logging.info(f"   ✓ Chunks saved to {chunks_path}")
            
            # Step 3: Create vector database collection FIRST
            logging.info("\n🧠 Step 3: Creating vector database collection...")
            self.embedding_manager.create_collection(
                collection_name=self.collection_name,
                reset=reset
            )
            logging.info(f"   ✓ Collection '{self.collection_name}' ready")
            
            # Step 4: Add documents to vector store
            logging.info("\n💾 Step 4: Generating embeddings and adding documents...")
            self.embedding_manager.add_documents(chunks)
            
            # Verify
            collection_stats = self.embedding_manager.get_collection_stats()
            self.total_documents = collection_stats['total_documents']
            logging.info(f"   ✓ Vector store has {self.total_documents} documents")
            
            # Mark as setup
            self.is_setup = True
            
            # Calculate total time
            elapsed_time = time.time() - start_time
            
            logging.info("\n" + "="*80)
            logging.info(f"✅ SETUP COMPLETE in {elapsed_time:.2f} seconds")
            logging.info("="*80)
            
            return {
                'success': True,
                'total_chunks': len(chunks),
                'total_documents_stored': self.total_documents,
                'setup_time_seconds': elapsed_time,
                'document_path': document_path,
                'vector_db_path': self.embedding_manager.persist_directory,
                'statistics': stats
            }
            
        except Exception as e:
            logging.error(f"Error during setup: {str(e)}")
            raise CustomException(sys, e)
            
    def process_query(
        self, 
        query: str,
        top_k: int = 3,
        verbose: bool = True
    ) -> Dict:
        """
        Process a query end-to-end.
        
        Args:
            query: Natural language query
            top_k: Number of relevant clauses to retrieve
            verbose: If True, print detailed logs
        
        Returns:
            Dict with complete results:
                - query: original query
                - parsed: parsed query information
                - retrieved_clauses: relevant policy clauses
                - decision: approval decision with reasoning
                - processing_time: time taken
        """
        try:
            # Check if setup was done
            if not self.is_setup:
                logging.warning("Pipeline not setup. Attempting to load existing vector store...")
                self.embedding_manager.create_collection(collection_name=self.collection_name)
                self.is_setup = True
            
            start_time = time.time()
            
            if verbose:
                logging.info("\n" + "="*80)
                logging.info(f"PROCESSING QUERY: {query}")
                logging.info("="*80)
            
            # Step 1: Parse query
            if verbose:
                logging.info("\n🔍 Step 1: Parsing query...")
            
            parsed = self.query_parser.parse(query)
            
            if verbose:
                logging.info(f"✓ Age: {parsed.age}")
                logging.info(f"✓ Gender: {parsed.gender}")
                logging.info(f"✓ Procedure: {parsed.procedure}")
                logging.info(f"✓ Location: {parsed.location}")
                logging.info(f"✓ Policy Duration: {parsed.policy_duration_months} months")
                logging.info(f"✓ Emergency: {parsed.is_emergency}")
            
            # Validate parsed query
            validation = self.query_parser.validate_parsed_query(parsed)
            missing_fields = self.query_parser.get_missing_fields(parsed)
            
            if verbose and missing_fields:
                logging.warning(f"⚠️  Missing fields: {', '.join(missing_fields)}")
            
            # Step 2: Semantic search
            if verbose:
                logging.info(f"\n🔎 Step 2: Searching vector database (top_k={top_k})...")
            
            search_results = self.embedding_manager.search(query, top_k=top_k)
            
            # Log the number of relevant clauses found if verbose mode is enabled
            if verbose:
                # Display count of retrieved documents from vector database search
                logging.info(f"✓Found {len(search_results['documents'])} relevant clauses")
                
                # Iterate through metadata and distance scores with enumerate to get index starting at 1
                for i, (meta, dist) in enumerate(zip(
                    search_results['metadatas'],  # Contains metadata like section name for each result
                    search_results['distances']   # Contains distance scores (lower = more similar)
                ), 1):
                    # Log each result with its section name and similarity score (1-distance converts distance to similarity percentage)
                    logging.info(f"   {i}. Section: {meta['section']} (similarity: {1-dist:.2%})")
            
            # Step 3: Make decision
            if verbose:
                logging.info("\n🤖 Step 3: Generating decision with LLM...")
                logging.info(f"{search_results['documents']}")
                
            
            decision = self.decision_engine.make_decision(
                query_info=parsed.model_dump(),
                retrieved_docs=search_results['documents'],
                retrieved_metadata=search_results['metadatas']
            )
            
            if verbose:
                logging.info(f"   ✓ Decision: {'✅ APPROVED' if decision.approved else '❌ REJECTED'}")
                logging.info(f"   ✓ Confidence: {decision.confidence}")
                if decision.amount:
                    logging.info(f"   ✓ Amount: ₹{decision.amount:,}")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            if verbose:
                logging.info(f"\n⏱️  Total processing time: {processing_time:.3f} seconds")
                logging.info("="*80 + "\n")
            
            # Compile complete result
            result = {
                'query': query,
                'parsed_query': {
                    'age': parsed.age,
                    'gender': parsed.gender,
                    'procedure': parsed.procedure,
                    'location': parsed.location,
                    'policy_duration_months': parsed.policy_duration_months,
                    'is_emergency': parsed.is_emergency,
                },
                'validation': {
                    'is_complete': validation['is_complete'],
                    'missing_fields': missing_fields
                },
                'retrieved_clauses': [
                    {
                        'text': doc,
                        'section': meta['section'],
                        'similarity': 1 - dist,
                        'chunk_id': chunk_id
                    }
                    for doc, meta, dist, chunk_id in zip(
                        search_results['documents'],
                        search_results['metadatas'],
                        search_results['distances'],
                        search_results['ids']
                    )
                ],
                'decision': {
                    'approved': decision.approved,
                    'amount': decision.amount,
                    'reasoning': decision.reasoning,
                    'relevant_clauses': decision.relevant_clauses,
                    'confidence': decision.confidence,
                    'risk_factors': decision.risk_factors
                },
                'processing_time_seconds': processing_time,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error processing query: {str(e)}")
            raise CustomException(sys,e)
            
    def batch_process(self, queries:List[str],
                      save_results:bool=True,
                      output_path:str="data/processed/batch_results.json"):
        
        """
        Process multiole queries in batch
        Arge:
            queries:List of query string
            save_results: If true save rsults to JSON
            output_path: Path to save results
            
        Returns:
            List of dictionaries    
        """
        
        try:
            logging.info(f"Processing {len(queries)} in batch...")
            results=[]
            start_time=time.time()
            
            for i , query in enumerate(queries,1):
                logging.info(f"Processing {i}/{len(queries)}: {query[:50]}...")
                
                try:
                    result=self.process_query(query,verbose=False)
                    results.append(result)
                    logging.info(f"{'APPROVED' if result['decision']['approved'] else 'REJECTED'}")
                except Exception as e:
                    logging.error(f"Error occure in batch process while processing queries: {str(e)}")
                    results.append({
                        "query":query,
                        "error":str(e),
                        "success":False
                    })
            total_time=time.time()-start_time
            avg_time=total_time/len(queries)
            
            
            logging.info(f"\n Batch processing complete")
            logging.info(f" Total Time: {total_time}")
            logging.info(f" Average Time: {avg_time}")
            logging.info(f" Throughput: {len(queries)/total_time:.2f} queries/second")
            
            if save_results:
                output_file=Path(output_path)
                output_file.parent.mkdir(parents=True,exist_ok=True)
                
                with open(output_file,'w') as f:
                    json.dump(result,f,indent=2)
                
                logging.info(f"Results saved to {output_path}")
            
            
            return results     
        except Exception as e:
            logging.error(f"Error occured in batch process: {str(e)}")
            raise CustomException(sys,e)
        
    
    
    def get_status(self)->Dict:
        """
        Get current pipeline status
        
        Returns:
            Dict with status information 
        """     
        try:
            collection_stats=self.embedding_manager.get_collection_stats()
            
            return{
                "is_setup":self.is_setup,
                "total_documents":self.total_documents,
                "LLM_provider":self.decision_engine.provider,
                "LLM_model":self.decision_engine.model,
                "Vector_storage":collection_stats,
                "supported_locations":len(self.query_parser.known_locations),
                "supported_procedures":len(self.query_parser.known_procedures)                
            }
        except Exception as e:
            logging.error(f"Error occured in getting status: {str(e)}")
            return {"error":str(e)}    
              
                    
                