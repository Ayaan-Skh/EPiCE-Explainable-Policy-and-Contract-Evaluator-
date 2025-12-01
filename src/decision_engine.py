import json, os,sys
from typing import List,Dict,Tuple,Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.logger import logging
from src.exception import CustomException

load_dotenv()
LLM_PROVIDER=os.getenv("LLM_PROVIDER","groq")

if LLM_PROVIDER=="groq":
    from groq import Groq
elif LLM_PROVIDER == "ollama":
    import ollama
elif LLM_PROVIDER == "openai":
    from openai import OpenAI    
else :
    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


class Decision(BaseModel):
    """
        Structured decision output model.
        Uses Pydantic for data validation and type safety.
    """
    approved: bool = Field(..., description="Whether claim is approved")
    amount: Optional[int] = Field(None, ge=0, description="Approved claim amount in rupees")
    reasoning: str = Field(..., min_length=10, description="Explanation for decision")
    relevant_clauses: List[str] = Field(default_factory=list, description="Policy sections used")
    confidence: str = Field(..., description="Confidence level: high, medium, or low")
    risk_factors: List[str] = Field(default_factory=list, description="Potential issues or concerns")
    
    class Config:
        json_schema_extra = {
            "example": {
                "approved": True,
                "amount": 150000,
                "reasoning": "Claim approved based on age eligibility, sufficient policy duration, and covered procedure.",
                "relevant_clauses": ["SECTION 2: SURGICAL COVERAGE", "SECTION 4: AGE ELIGIBILITY"],
                "confidence": "high",
                "risk_factors": []
            }
        }



class DecisionEngine:
    """
        LLM Powered decision engine for insurance claims.
    """
    
    def __init__(self,provider:Optional[str]=None,model:Optional[str]=None):
        """
            Initialize decision engine with LLM provider.
        
            Args:
                provider: LLM provider (groq/ollama/openai). Defaults to env variable.
                model: Model name. Defaults to env variable.
        """
        
        try:
            self.provider=provider or os.getenv("LLM_PROVIDER",'groq')
            default_models = {
                "groq": "llama-3.1-8b-instant",
                "ollama": "llama3.1",
                "openai": "gpt-3.5-turbo"
            }
            
            # Set model name from parameter, environment variable, or default mapping
            self.model = model or os.getenv("LLM_MODEL", default_models.get(self.provider))
            # Log initialization details for infoging and monitoring
            logging.info(f"Initializing DecisionEngine with provider: {self.provider}, model: {self.model}")
            
            # Check if Groq is the selected LLM provider
            if self.provider=='groq':
                # Retrieve Groq API key from environment variables
                api_key=os.getenv("GROQ_API_KEY")
                # Validate that API key exists, raise error if missing
                if not api_key:
                    logging.error("Groq api_key not found")
                    raise ValueError("Groq api_key not found")
                # Initialize Groq client with the API key
                self.client=Groq(api_key=api_key,timeout=500)
            elif self.provider == "ollama":
                # Ollama doesn't need API key
                self.client = ollama
                
            elif self.provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment variables")
                self.client = OpenAI(api_key=api_key)
            
            logging.info(f"✅ DecisionEngine initialized with {self.provider} ({self.model})")
            
        except Exception as e:
            logging.error(f"Error initializing DecisionEngine: {str(e)}")
            raise CustomException(sys, e)
        
        
        
    def make_decision(self,query_info:Dict,retrived_docs:List[str],retrived_metadata:Optional[List[Dict]])->Decision:
        """
            Make insurance claim decision using LLM.
            
            Args:
                query_info: Parsed query information (age, procedure, etc.)
                retrieved_docs: Relevant policy clauses from vector search
                retrieved_metadata: Metadata for retrieved documents (sections, etc.)
            
            Returns:
                Decision object with approval status, reasoning, etc.
        """    
        try:
            logging.info("Making decision using LLM")
            prompt=self._build_prompt(query_info,retrived_docs,retrived_metadata)
            logging.info(f"Prompt built for LLM:{prompt[:500]}")

            response_text=self._call_llm(prompt)
            logging.info(f"Response of LLM:{response_text}")

            decision=self._parse_llm_response(response_text)
            
            logging.info(f"Decision made: {"🟢APPROVED" if decision.approved else "🔴REJECTED"}")
            logging.info(f"Confidence: {decision.confidence}")
            
            return decision
        except Exception as e:
            logging.error(f"Error making decision {str(e)}")
            return Decision(
                approved=False,
                reasoning=f"Error processing claim: {str(e)}",
                relevant_clauses=[],
                confidence="low",
                risk_factors=["System error occurred"]
            )
    def _build_prompt(self, 
        query_info: Dict, 
        docs: List[str],
        metadata: Optional[List[Dict]] = None)->str:
        """
            Build comprehensive prompts for LLM
            
            It Includes:
            - System instructions
            - Claim details
            - Policy Details
            - Decision criteria
            - Output format instructions
        """        
        
        # Extract query information
        age = query_info.get('age', 'Not specified')
        gender = query_info.get('gender', 'Not specified')
        procedure = query_info.get('procedure', 'Not specified')
        location = query_info.get('location', 'Not specified')
        policy_duration = query_info.get('policy_duration_months', 'Not specified')
        is_emergency = query_info.get('is_emergency', False)
        
        formatted_clauses=[]
        for i, doc in enumerate(docs):
            section = "unknown Section"
            if metadata and i < len(metadata):
                section = metadata[i].get("section","Unknown Section")
            formatted_clauses.append(f"[{section}] \n {doc}")
        clauses_text="\n\n".join(formatted_clauses)
        
        prompt=f"""You are an expert insurance claim analyst. Analyze the following claim and determine if it should be approved based on the policy clauses provided.

            CLAIM DETAILS:
            - Patient Age: {age}
            - Gender: {gender}
            - Medical Procedure: {procedure}
            - Treatment Location: {location}
            - Policy Duration: {policy_duration} months
            - Emergency Case: {'Yes' if is_emergency else 'No'}

            RELEVANT POLICY CLAUSES:
            {clauses_text}

            ANALYSIS INSTRUCTIONS:
            1. Check age eligibility (typically 18-50 for standard coverage)
            2. Verify policy duration requirements:
            - Emergency procedures: Immediate coverage
            - Elective surgeries: Typically require 2+ months
            - Specific procedures may have longer waiting periods
            3. Confirm procedure is covered
            4. Assess location coverage (Tier 1 cities usually 100%, others 70-80%)
            5. Identify any exclusions or special conditions

            DECISION CRITERIA:
            - If ALL requirements are met → APPROVE
            - If ANY critical requirement fails → REJECT
            - If information is insufficient → REJECT with explanation

            OUTPUT FORMAT (Must be valid JSON):
            {{
                "approved": true or false,
                "amount": estimated_claim_amount_in_rupees or null,
                "reasoning": "Clear, concise explanation referencing specific policy sections",
                "relevant_clauses": ["List of policy section names used in decision"],
                "confidence": "high" or "medium" or "low",
                "risk_factors": ["List any concerns, missing info, or edge cases"]
            }}

            IMPORTANT RULES:
            - Be strict in applying policy requirements
            - Always reference specific policy sections in reasoning
            - If age is outside 18-50, note this as a risk factor
            - If policy duration is insufficient, reject the claim
            - If procedure is not explicitly covered, reject
            - For emergency cases, waive waiting period requirements
            - Estimate claim amounts based on typical costs mentioned in policy
            - Use "high" confidence only when all information is clear
            - Use "low" confidence if critical information is missing

            Provide your analysis as a valid JSON object: """    
                
        return prompt
    
    def _call_llm(self,prompt:str)->str:
        
        """
        Call LLM based on configured provider.
        """
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert insurance claim analyst. Always respond with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,  # Low temperature for consistent outputs
                    max_tokens=1000,
                )
                return response.choices[0].message.content
                
            elif self.provider == "ollama":
                response = self.client.chat(
                    model=self.model,
                    messages=[
                        {
                            'role': 'system',
                            'content': 'You are an expert insurance claim analyst. Always respond with valid JSON.'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    options={
                        'temperature': 0.1,
                        'num_predict': 1000,
                    }
                )
                return response['message']['content']
                
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert insurance claim analyst. Always respond with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,
                    max_tokens=1000,
                )
                return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error calling LLM: {str(e)}")
            raise CustomException(sys, e)
        
    def _parse_llm_response(self, response: str) -> Decision:
        """
        Parse LLM response into Decision object.
        
        Handles:
        - JSON extraction from response
        - Validation via Pydantic
        - Fallback for malformed responses
        """
        try:
            # Extract JSON from response (LLM might add text before/after)
            # Find first { and last }
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Validate and create Decision object
            decision = Decision(**data)
            
            logging.info(f"Successfully parsed decision: {decision.approved}")
            return decision
            
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing error: {str(e)}")
            logging.error(f"Response was: {response[:500]}")
            
            # Fallback: Try to extract key information manually
            return self._fallback_parse(response)
            
        except Exception as e:
            logging.error(f"Error parsing LLM response: {str(e)}")
            
            # Return conservative fallback
            return Decision(
                approved=False,
                reasoning="Unable to parse LLM response. Manual review required.",
                relevant_clauses=[],
                confidence="low",
                risk_factors=["Response parsing failed"]
            )
    
    def _fallback_parse(self, response: str) -> Decision:
        """
        Fallback parser for when JSON extraction fails.
        
        Uses regex to extract key information.
        """
        import re
        
        try:
            # Try to determine if approved
            approved = False
            if re.search(r'"approved"\s*:\s*true', response, re.IGNORECASE):
                approved = True
            
            # Try to extract reasoning
            reasoning_match = re.search(r'"reasoning"\s*:\s*"([^"]*)"', response)
            reasoning = reasoning_match.group(1) if reasoning_match else "Unable to extract reasoning from response"
            
            return Decision(
                approved=approved,
                reasoning=reasoning,
                relevant_clauses=[],
                confidence="low",
                risk_factors=["Fallback parsing used"]
            )
            
        except Exception as e:
            logging.error(f"Fallback parsing also failed: {str(e)}")
            return Decision(
                approved=False,
                reasoning="Complete parsing failure. Manual review required.",
                relevant_clauses=[],
                confidence="low",
                risk_factors=["Complete parsing failure"]
            )
    
    def test_connection(self) -> bool:
        """
        Test if LLM connection is working.
        
        Returns:
            bool: True if connection successful
        """
        try:
            logging.info(f"Testing {self.provider} connection...")
            
            test_prompt = "Say 'Hello, I am working!' in exactly those words."
            response = self._call_llm(test_prompt)
            
            logging.info(f"Test response: {response[:100]}")
            logging.info("✅ LLM connection test successful")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ LLM connection test failed: {str(e)}")
            return False
    