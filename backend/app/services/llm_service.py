"""
LLM Service - LangChain wrapper for Google Gemini
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from typing import Dict, Any, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Wrapper for LangChain LLM operations"""
    
    def __init__(self):
        """Initialize LLM with Google Gemini"""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
        self.str_parser = StrOutputParser()
        self.json_parser = JsonOutputParser()
    
    async def generate_text(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text response from LLM"""
        try:
            if context:
                full_prompt = f"{context}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            # Use LangChain for generation
            chain = self.llm | self.str_parser
            response = await chain.ainvoke(full_prompt)
            
            return response
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise
    
    async def generate_with_template(
        self,
        template: str,
        variables: Dict[str, Any]
    ) -> str:
        """Generate text using a prompt template"""
        try:
            prompt = PromptTemplate(
                template=template,
                input_variables=list(variables.keys())
            )
            
            chain = prompt | self.llm | self.str_parser
            response = await chain.ainvoke(variables)
            
            return response
        except Exception as e:
            logger.error(f"Error with template: {str(e)}")
            raise
    
    async def generate_json(
        self,
        prompt: str,
        schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON output"""
        import json
        import re

        try:
            if schema:
                json_prompt = f"{prompt}\n\nRespond with JSON following this schema: {schema}"
            else:
                json_prompt = f"{prompt}\n\nRespond with valid JSON."

            chain = self.llm | self.json_parser
            response = await chain.ainvoke(json_prompt)

            # If response is a string, try to parse and sanitize it
            if isinstance(response, str):
                # Remove control characters except \n, \r, \t
                cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', response)
                try:
                    response = json.loads(cleaned)
                except json.JSONDecodeError:
                    # If still fails, wrap in a result object
                    logger.warning(f"Failed to parse JSON response, wrapping in result object")
                    response = {"result": cleaned}

            # Recursively clean the response dict
            response = self._sanitize_json_object(response)

            return response
        except Exception as e:
            logger.error(f"Error generating JSON: {str(e)}")
            raise

    def _sanitize_json_object(self, obj):
        """Recursively sanitize JSON object by removing control characters"""
        import re

        if isinstance(obj, dict):
            return {k: self._sanitize_json_object(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_json_object(item) for item in obj]
        elif isinstance(obj, str):
            # Remove control characters except \n, \r, \t
            return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', obj)
        else:
            return obj
    
    async def analyze_text(
        self,
        text: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """Analyze text with structured output"""
        prompts = {
            "general": "Analyze the following text and provide key insights:",
            "sentiment": "Analyze the sentiment of the following text:",
            "summary": "Provide a concise summary of the following text:",
            "style": "Analyze the writing style and tone of the following text:"
        }
        
        prompt = f"{prompts.get(analysis_type, prompts['general'])}\n\n{text}"
        
        return await self.generate_json(
            prompt,
            schema={
                "analysis": "string",
                "key_points": ["string"],
                "confidence": "number"
            }
        )


# Global instance
llm_service = LLMService()