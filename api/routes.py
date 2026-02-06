from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pathlib import Path
from api.models import (
    QueryRequest, QueryResponse, StatusResponse, ErrorResponse,
    ParsedQueryInfo, DecisionInfo, RetrivedClause,
    BatchQueryRequest, BatchQueryResponse,
    HistoryEntry, AnalyticsResponse,
)
import shutil
import time
import io
from src.pipeline import InsuranceQAPipeline
from src.logger import logging
from api.history_cache import (
    get_cached_response,
    set_cached_response,
    append_to_history,
    get_history,
    get_analytics,
)
from api.pdf_export import build_pdf_bytes

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
            llm_provider=status.get("llm_provider") or status.get("LLM_provider", "unknown"),
            llm_model=status.get("llm_model") or status.get("LLM_model", "unknown"),
            supported_locations=status.get("supported_locations", 0),
            supported_procedures=status.get("supported_procedures", 0),
        )
    except Exception as e:
        logging.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-file")
async def upload_policy_file(file:UploadFile=File(...)):
    """
    Upload policy document (PDF, DOCX, TXT)
    
    :param file: Description
    :type file: UploadFile
    """
    try:
        file_ext=Path(file.filename).suffix.lower()
        allowed_ext=['.pdf','.doc','.docx','.txt']
        
        if file_ext not in allowed_ext:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format. Allower formats are:{",".join(allowed_ext)}"
            )
        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to start
        
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size should be less than 10 MB"
            )
        
        # Save file
        upload_dir=Path("data/raw/uploads")    
        upload_dir.mkdir(exist_ok=True, parents=True)
        
        file_path=upload_dir/file.filename
        
        with open(file_path,"wb") as buffer:
            shutil.copyfileobj(file.file,buffer)
            
        logging.info(f"file uploaded: {file.filename} ({file_size/1024}KB)")
        
        # Process document
        pipeline=get_pipeline()    
        logging.info("Processing uploaded document")
        setup_result=pipeline.setup(
            document_path=file_path,
            reset=True,
            save_chunks=True
        )
        
        return {
            "success": True,
                "message": "Document uploaded and processed successfully",
                "filename": file.filename,
                "file_size_kb": round(file_size / 1024, 2),
                "file_type": file_ext,
                "total_chunks": setup_result['total_chunks'],
                "total_documents_stored": setup_result['total_documents_stored'],
                "setup_time_seconds": setup_result['setup_time_seconds'],
                "statistics": setup_result['statistics']
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error uploading file: {str(e)}")    
        raise HTTPException(status_code=500, detail=f"Error uploading file:{str(e)}")


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process insurance claim query (with caching and history).
    Core pipeline logic unchanged; cache and history are additive.
    """
    try:
        # Check cache first (performance optimization)
        cached = get_cached_response(request.query, request.top_k)
        if cached is not None:
            response = QueryResponse(
                success=True,
                query=cached['query'],
                parsed_query=ParsedQueryInfo(**cached['parsed_query']),
                decision=DecisionInfo(**cached['decision']),
                retrieved_clauses=[RetrivedClause(**c) for c in cached['retrieved_clauses']],
                processing_time_seconds=cached['processing_time_seconds'],
                timestamp=cached['timestamp'],
            )
            append_to_history(request.query, request.top_k, cached, from_cache=True)
            logging.info(f"✅ Query served from cache: {request.query[:50]}...")
            return response

        pipeline = get_pipeline()

        if not pipeline.is_setup:
            raise HTTPException(
                status_code=503,
                detail="System not setup. Please upload a policy document first."
            )

        logging.info(f"Processing query: {request.query}")

        result = pipeline.process_query(
            query=request.query,
            top_k=request.top_k,
            verbose=True,
        )

        # Build response dict for cache and history
        response_dict = {
            "query": result["query"],
            "parsed_query": result["parsed_query"],
            "decision": result["decision"],
            "retrieved_clauses": result["retrieved_clauses"],
            "processing_time_seconds": result["processing_time_seconds"],
            "timestamp": result["timestamp"],
        }
        set_cached_response(request.query, request.top_k, response_dict)
        append_to_history(request.query, request.top_k, response_dict, from_cache=False)

        response = QueryResponse(
            success=True,
            query=result["query"],
            parsed_query=ParsedQueryInfo(**result["parsed_query"]),
            decision=DecisionInfo(**result["decision"]),
            retrieved_clauses=[RetrivedClause(**c) for c in result["retrieved_clauses"]],
            processing_time_seconds=result["processing_time_seconds"],
            timestamp=result["timestamp"],
        )

        logging.info(f"✅ Query processed: {'APPROVED' if response.decision.approved else 'REJECTED'}")
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


@router.post("/batch-query", response_model=BatchQueryResponse)
async def batch_process_queries(request: BatchQueryRequest):
    """Process multiple queries in batch. Uses existing pipeline batch_process."""
    try:
        pipeline = get_pipeline()
        if not pipeline.is_setup:
            raise HTTPException(
                status_code=503,
                detail="System not setup. Please upload a policy document first.",
            )
        start = time.time()
        results = pipeline.batch_process(
            queries=request.queries,
            save_results=False,
        )
        total_time = time.time() - start
        return BatchQueryResponse(
            success=True,
            total=len(results),
            results=results,
            total_time_seconds=round(total_time, 3),
            avg_time_seconds=round(total_time / len(results), 3) if results else 0,
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in batch query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[HistoryEntry])
async def get_query_history(limit: int = 50, offset: int = 0):
    """Return recent query history (newest first)."""
    try:
        entries = get_history(limit=min(limit, 100), offset=offset)
        return [HistoryEntry(**e) for e in entries]
    except Exception as e:
        logging.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics_dashboard():
    """Return analytics computed from query history."""
    try:
        stats = get_analytics()
        return AnalyticsResponse(**stats)
    except Exception as e:
        logging.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export-pdf")
async def export_result_to_pdf(result: QueryResponse):
    """Generate and return a PDF for the given query result."""
    try:
        result_dict = result.model_dump()
        pdf_bytes = build_pdf_bytes(result_dict)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=epice-query-result.pdf"},
        )
    except ImportError as e:
        raise HTTPException(
            status_code=501,
            detail="PDF export requires reportlab. Install with: pip install reportlab",
        )
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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