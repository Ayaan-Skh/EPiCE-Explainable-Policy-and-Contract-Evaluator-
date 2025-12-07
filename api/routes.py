from fastapi import APIRouter, HTTPException
from api.models import (
    QueryRequest, QueryResponse, StatusResponse, ErrorResponse,
    ParsedQueryInfo, DecisionInfo, RetrivedClause
)
from src.pipeline import InsuranceQAPipeline
from src.logger import logging
import time

router = APIRouter()

# Initialize pipeline (singleton)
pipeline = None

def get_pipeline():
    """Get or initialize pipeline instance"""
    global pipeline
    if pipeline is None:
        try:
            logging.info("Initializing pipeline...")
            pipeline = InsuranceQAPipeline()
            
            # Try to load existing vector store
            try:
                pipeline.embedding_manager.create_collection(
                    collection_name="policy_documents"
                )
                pipeline.is_setup = True
                logging.info("✅ Loaded existing vector store")
            except Exception as e:
                logging.warning(f"No existing vector store found: {str(e)}")
                pipeline.is_setup = False
            
        except Exception as e:
            logging.error(f"Failed to initialize pipeline: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to initialize system")
    
    return pipeline


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "status": "healthy",
        "message": "Insurance Q&A API is running"
    }


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get system status"""
    try:
        pipeline = get_pipeline()
        status = pipeline.get_status()
        
        return StatusResponse(
            success=True,
            is_setup=status.get("is_setup", False),
            total_documents=status.get("total_documents", 0),
            llm_provider=status.get("llm_provider", "unknown"),
            llm_model=status.get("llm_model", "unknown"),
            supported_locations=status.get("supported_locations", 0),
            supported_procedures=status.get("supported_procedures", 0),
        )
    except Exception as e:
        logging.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process insurance claim query
    
    Args:
        request: QueryRequest with query text and top_k
    
    Returns:
        QueryResponse with decision and retrieved clauses
    """
    try:
        pipeline = get_pipeline()
        
        # Check if system is setup
        if not pipeline.is_setup:
            raise HTTPException(
                status_code=503,
                detail="System not setup. Please upload a policy document first."
            )
        
        logging.info(f"Processing query: {request.query}")
        
        # Process query through pipeline
        result = pipeline.process_query(
            query=request.query,
            top_k=request.top_k,
            verbose=True
        )
        
        # Convert to API response format
        response = QueryResponse(
            success=True,
            query=result['query'],
            parsed_query=ParsedQueryInfo(**result['parsed_query']),
            decision=DecisionInfo(**result['decision']),
            retrieved_clauses=[
                RetrivedClause(**clause)
                for clause in result['retrieved_clauses']
            ],
            processing_time_seconds=result['processing_time_seconds'],
            timestamp=result['timestamp']
        )
        
        logging.info(f"✅ Query processed successfully: {'APPROVED' if response.decision.approved else 'REJECTED'}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/upload")
async def upload_document():
    """
    Upload and process policy document
    
    Note: This is a placeholder. Real implementation would handle file upload.
    For now, it triggers setup with the existing document.
    """
    try:
        pipeline = get_pipeline()
        
        # Use existing document for demo
        # In production, you'd save the uploaded file and process it
        document_path = "data/raw/insurance_policy.txt"
        
        logging.info("Starting document upload and processing...")
        
        setup_result = pipeline.setup(
            document_path=document_path,
            reset=True,
            save_chunks=True
        )
        
        return {
            "success": True,
            "message": "Document uploaded and processed successfully",
            "total_chunks": setup_result['total_chunks'],
            "total_documents_stored": setup_result['total_documents_stored'],
            "setup_time_seconds": setup_result['setup_time_seconds']
        }
        
    except Exception as e:
        logging.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/test-llm")
async def test_llm():
    """Test LLM connection"""
    try:
        pipeline = get_pipeline()
        is_working = pipeline.decision_engine.test_connection()
        
        return {
            "success": True,
            "llm_working": is_working,
            "provider": pipeline.decision_engine.provider,
            "model": pipeline.decision_engine.model
        }
    except Exception as e:
        logging.error(f"Error testing LLM: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))