import re
from typing import List,Dict,Tuple, Optional
from src.logger import logging
from src.exception import CustomException
from pydantic import BaseModel,Field,field_validator
import sys
# import pattern

class ParseQuery(BaseModel):
    """
        Structured representation of a parsed_query query.
        
        Uses Pydantic for automatic validation and type checking.
    """
    age: Optional[int] = Field(None, ge=0, le=120, description="Patient age in years")  # Optional integer age (may be None); Field enforces minimum 0, maximum 120, and documents as patient age in years
    gender: Optional[str] = Field(None, description="Patient gender (male/female)")  # Optional string for patient gender; Field description documents expected values (e.g., "male"/"female")
    procedure: Optional[str] = Field(None, description="Medical procedure requested")  # Optional string naming the medical procedure requested; Field description for documentation
    location: Optional[str] = Field(None, description="Treatment location/city")  # Optional string for treatment location or city; Field description documents intent
    policy_duration_months: Optional[int] = Field(None, ge=0, description="Policy duration in months")  # Optional integer for policy duration (months); Field enforces non-negative values with ge=0 and documents units
    is_emergency: Optional[bool] = Field(False, description="Whether this is an emergency case")  # Optional boolean indicating emergency status; defaults to False when not provided
    raw_query: str = Field(..., description="Original query text")  # Required string (ellipsis ... makes it required) that stores the original/unparsed query text
    
    @field_validator('gender')
    def normalize_gender(cls,v):
        if v:
            return v.lower()
        return v
    
    @field_validator("location")
    def noramlize_location(cls,v):
        if v:
            return v.title()
    
    @field_validator("procedure")
    def noramlize_procedure(cls,v):
        if v:
            return v.lower()
    
    class Config:
        """Pydamtic Configuration"""
        json_schema_extra={
            "example":{
                "age":46,
                "gender":"male",
                "procedure":"knee surgery",
                "location":"Pune",
                "policy_duration_months":3,
                "is_emergency":False,
                "raw_query":"46 year old male knee surgery Pune"
            }
        }
        
        
class Query_parser:
    """To parse the Natural language query to structured data"""
    """
        Handles various query formats:
        - "46M knee surgery Pune 3 month policy"
        - "46 year old male, knee surgery in Pune, 3-month-old insurance policy"
        - "male 46 years, knee replacement, Mumbai, policy 6 months old"
    """
    
    def __init__(self):
        """Initialize parser with valuse and key words"""
        self.age_patterns=[
             r'(\d{1,3})\s*(?:year|yr|y|yo)(?:s)?(?:\s+old)?',  # "46 years old", "46 yr", "46y"
            r'(\d{1,3})\s*(?:M|F|male|female)',  # "46M", "46F", "46 male"
            r'(?:age|aged)\s*(\d{1,3})',  # "age 46", "aged 46"
            r'(\d{1,3})\s*-\s*(?:year|yr)',  # "46-year-old"
        ]
        
        self.gender_patterns = [
            # Matches: "male", "man", "28M", "28m", standalone "M"
            (r'\b(male|man|gentleman)\b|(?<=\d)[mM]\b|\b[mM]\b', 'male'),
            
            # Matches: "female", "woman", "lady", "25F", "25f", standalone "F"
            (r'\b(female|woman|lady)\b|(?<=\d)[fF]\b|\b[fF]\b', 'female'),
        ]
        
        self.known_locations=[
            'mumbai', 'delhi', 'bangalore', 'pune', 'hyderabad', 'chennai',
            'kolkata', 'ahmedabad', 'surat', 'jaipur', 'lucknow', 'kanpur',
            'nagpur', 'indore', 'thane', 'bhopal', 'visakhapatnam', 'pimpri',
            'patna', 'vadodara', 'ghaziabad', 'ludhiana', 'agra', 'nashik'
        ]
        
        self.known_procedures= {
            'knee surgery': ['knee surgery', 'knee operation', 'knee replacement', 'knee arthroscopy'],
            'hip replacement': ['hip replacement', 'hip surgery', 'hip operation'],
            'cardiac': ['cardiac', 'heart surgery', 'bypass', 'angioplasty', 'heart operation'],
            'cataract': ['cataract', 'cataract surgery', 'eye surgery'],
            'spinal': ['spinal surgery', 'spine surgery', 'back surgery'],
            'emergency': ['emergency', 'urgent', 'accident'],
        }
        
        self.duration_patterns=[
             r'(\d+)\s*(?:month|mon|mo|m)(?:s)?(?:\s+old)?(?:\s+policy)?',  # "3 months old policy"
            r'policy\s*(?:of|for)?\s*(\d+)\s*(?:month|mon|mo)',  # "policy of 3 months"
            r'(\d+)\s*(?:month|mon|mo)(?:s)?\s+(?:old\s+)?(?:insurance|policy)',  # "3 month old insurance"
        ]
        self.emergency_keywords=['emergency','critical','accident','urgent','immediate']
        logging.info("Query parser initialized suuccessfully")
        
    def parse(self, query:str)->ParseQuery:
        """Parse the natural language query into structured data"""
        """
            Main parsing function - extracts all entities from query.
            
            Args:
                query: Natural language query string
                
            Returns:
                ParsedQuery: Structured query object
                
            Example:
                >>> parser.parse("46M knee surgery Pune 3 month policy")
                ParsedQuery(age=46, gender='male', procedure='knee surgery', 
                        location='Pune', policy_duration_months=3, ...)
        """
        
        try:
            logging.info(f"parsing query{query}")
            query_lower=query.lower()
            age=self._extract_age(query)
            gender=self._extract_gender(query_lower)
            policy_duration=self._extract_policy_duration(query_lower)
            location=self._extract_location(query_lower)
            procedure=self._extract_procedure(query_lower)
            is_emergency=self._extract_check_emergency(query_lower)
            
            parsed_query=ParseQuery(
                age=age,
                gender=gender,
                procedure=procedure,
                location=location,
                policy_duration_months=policy_duration,
                is_emergency=is_emergency,
                raw_query=query
            )
            logging.info(f"Parsed results: age={age}, gender={gender}, procedure={procedure}, "
                        f"location={location}, duration={policy_duration}, emergency={is_emergency}")
            logging.info(f"Parsed query successfullly{parsed_query.json()}")
            
            return parsed_query
            
        except Exception as e:
            logging.info(f"Error occured while parsing the query:{str(e)}")
            
            return ParseQuery(raw_query=query)
    
    def _extract_age(self,query:str)->Optional[int]:
        """
            Extarct age from query using different patterns
            Try patterns in order and return the match
        """    
        
        try:
            for pattern in self.age_patterns:
                match=re.search(pattern,query,re.IGNORECASE)
                if match:
                    age=int(match.group(1))
                    #Validate age range
                    if 0<= age<=120 :
                        logging.info(f"Extracted age:{age}")
                        return age        
                    else:
                        logging.info(f"Age is out of valid bounds:{age}")
            return None            
        except Exception as e:
            logging.info(f"Error in extracting age: {str(e)}")
            return None
        
    def _extract_gender(self,query_lower:str)->Optional[str]:
        """
            Extract the gender from the query
        """
        try:
            for pattern, gender in self.gender_patterns:
                match=re.search(pattern, query_lower,re.IGNORECASE)
                if match:
                    logging.info(f'Extracted Gender:{gender}')
                    return gender
            return None
        except Exception as e:
            logging.info(f"Error in extracting Gender:{str(e)}")
            return None    
        
    def _extract_location(self,query:str)->Optional[str]:
        """
            Extract the location from the query
        """ 
        try:
            for patterns in self.known_locations:
                location=re.search(patterns,query,re.IGNORECASE)
                if location:
                    logging.info(f"Extracted location is:{location}")
                    return location.group(0).title()
        except Exception as e:
            logging.info(f'Error in extracting location:{str(e)}')
            
    def _extract_procedure(self,query_lower:str)->Optional[str]:
        """
        Extract medical procedure from query.
        
        Uses keyword matching against known procedures.
        Supports various ways of saying the same procedure.
        """
        try:
            
            for canonical_name, variants in self.known_procedures.items():
                for variant in variants:
                    if variant in query_lower:
                        logging.debug(f"Extracted procedure: {canonical_name}")
                        return canonical_name
            
            # If no known procedure found, try to extract any surgery-related term
            surgery_pattern = r'(\w+\s+(?:surgery|operation|procedure|replacement))'
            match = re.search(surgery_pattern, query_lower)
            if match:
                procedure = match.group(1).strip()
                logging.debug(f"Extracted unknown procedure: {procedure}")
                return procedure
                
            return None
        except Exception as e:
            logging.error(f"Error extracting procedure: {str(e)}")
            return None
    def _extract_policy_duration(self,query_lower:str)->Optional[int]:
        """
            Extract policy duration in months from query using different patterns
        """
        try:
            for pattern in self.duration_patterns:
                match=re.search(pattern,query_lower,re.IGNORECASE)
                if match:
                    duration = int(match.group(1))
                    if 0 <= duration <= 120:
                            logging.debug(f"Extracted policy duration: {duration} months")
                            return duration
                    else:
                        logging.warning(f"Policy duration {duration} seems invalid")
                return None
        except Exception as e:
            logging.info(f"Error in extracting duration")
            return None    
                    
                    
    def _extract_check_emergency(self,query_lower:str)->Optional[bool]:
        try:
            for keyword in self.emergency_keywords:
                if keyword in query_lower:
                    logging.info(f"Emergency keyword found:{keyword}")
                    return True
            return False    
        except Exception as e:
            logging.info("No emergency keywords found")
            return False                          
        
    def validate_parsed_query(self,parsed_query:ParseQuery)->Dict[str,bool]:
        """
            Validates the valuse present in query
            
            Returns:
                Dictionary of validation of each field
        """    
        try:
            validations = {
                'has_age': parsed_query.age is not None,
                'has_procedure': parsed_query.procedure is not None,
                'has_location': parsed_query.location is not None,
                'has_policy_duration': parsed_query.policy_duration_months is not None,
                'age_in_range': parsed_query.age is not None and 0 <= parsed_query.age <= 120,
            }
            
            validations['is_complete'] = all([
                validations['has_age'],
                validations['has_procedure'],
                validations['has_location'],
                validations['has_policy_duration']
            ])
            
            logging.info(f"Validation results: {validations}")
            return validations
        except Exception as e:
            logging.info(F"Error validating parsed query: {str(e)}")
            return CustomException(sys,e)
        
        
    def get_missing_fields(self,parsed_query:ParseQuery)->List[str]:
        """
            Get list of fields taht couldn't be extracted
            Useful for feedback or fallback logic
        """
        missing=[]
        if parsed_query.age is None:
            missing.append('age')
        if parsed_query.procedure is None:
            missing.append('procedure')
        if parsed_query.location is None:
            missing.append('location')
        if parsed_query.policy_duration_months is None:
            missing.append('policy_duration')
        
        return missing
            