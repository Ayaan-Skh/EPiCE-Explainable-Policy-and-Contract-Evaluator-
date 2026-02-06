from pydantic import BaseModel,Field
from typing import List,Dict,Optional

class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query:str=Field(...,min_length=5,description="Natural language insurance query")
    top_k:int=Field(..., ge=1,le=10,description="Number of clauses to retrive")
    
    class Config:
        json_schema_extra={
            "example":{
                "query":"46 year old male,knee surgery in Pune, 3 months policy",
                "top_k":3
            }
        }


class ParsedQueryInfo(BaseModel):
    age:Optional[int]=None
    gender:Optional[str]=None
    procedure:Optional[str]=None
    location:Optional[str]=None
    policy_duration_months:Optional[int]=None
    is_emegency:Optional[bool]=None
    
    
class DecisionInfo(BaseModel):
    """Decision Information"""
    approved:bool
    amount:Optional[int]
    reasoning:str
    relevant_clauses:List[str]
    confidence:str
    risk_factors:List[str]    

class RetrivedClause(BaseModel):
    """Retrived policy model"""
    text:str
    section:str
    similarity:float
    chunk_id:str
    
    
        
class QueryResponse(BaseModel):    
    success:bool
    query:str
    parsed_query:ParsedQueryInfo
    decision:DecisionInfo
    retrieved_clauses:List[RetrivedClause]
    processing_time_seconds:float
    timestamp:str
    
class StatusResponse(BaseModel):
    """Response model for status endpoint""" 
    
    success:bool
    is_setup:bool
    total_documents:int
    llm_provider:str
    llm_model:str
    supported_locations:int
    supported_procedures:int 
    
class ErrorResponse(BaseModel):
    """Error response model"""
    success:bool=False
    error:str
    details:Optional[str]=None


class BatchQueryRequest(BaseModel):
    """Request model for batch query endpoint"""
    queries: List[str] = Field(..., min_length=1, max_length=50)
    top_k: int = Field(3, ge=1, le=10)


class BatchQueryResponse(BaseModel):
    """Response model for batch query"""
    success: bool
    total: int
    results: List[Dict]
    total_time_seconds: float
    avg_time_seconds: float


class HistoryEntry(BaseModel):
    id: str
    query: str
    top_k: int
    timestamp: str
    processing_time_seconds: Optional[float]
    approved: Optional[bool]
    from_cache: bool = False


class AnalyticsResponse(BaseModel):
    total_queries: int
    approved_count: int
    rejected_count: int
    approval_rate: float
    avg_processing_time_seconds: float
    cache_hits: int
    cache_size: int
