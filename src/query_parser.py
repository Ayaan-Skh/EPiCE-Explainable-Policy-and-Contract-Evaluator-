import re
from typing import List,Dict,Tuple, Optional
from src.logger import logging
from src.exception import CustomException
from pydantic import BaseModel,Field,field_validator
import sys

class ParseQuery(BaseModel):
    """
        Structured representation of a parsed query.
        
        Uses Pydantic for automatic validation and type checking.
    """
    age: Optional[int] = Field(None, ge=0, le=120, description="Patient age in years")  # Optional integer age (may be None); Field enforces minimum 0, maximum 120, and documents as patient age in years
    gender: Optional[str] = Field(None, description="Patient gender (male/female)")  # Optional string for patient gender; Field description documents expected values (e.g., "male"/"female")
    procedure: Optional[str] = Field(None, description="Medical procedure requested")  # Optional string naming the medical procedure requested; Field description for documentation
    location: Optional[str] = Field(None, description="Treatment location/city")  # Optional string for treatment location or city; Field description documents intent
    policy_duration_months: Optional[int] = Field(None, ge=0, description="Policy duration in months")  # Optional integer for policy duration (months); Field enforces non-negative values with ge=0 and documents units
    is_emergency: Optional[bool] = Field(False, description="Whether this is an emergency case")  # Optional boolean indicating emergency status; defaults to False when not provided
    raw_query: str = Field(..., description="Original query text")  # Required string (ellipsis ... makes it required) that stores the original/unparsed query text
    