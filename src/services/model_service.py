import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta

class ModelServiceError(Exception):
    """Custom exception for model service errors"""
    pass

class ErrorType(Enum):
    NETWORK_ERROR = "network_error"
    API_ERROR = "api_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    VALIDATION_ERROR = "validation_error"

@dataclass
class ModelResponse:
    success: bool
    content: Optional[str] = None
    error_type: Optional[ErrorType] = None
    error_message: Optional[str] = None
    response_time: Optional[float] = None
    model_name: Optional[str] = None

class ModelService:
    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.rate_limit_tracker = {}
        
    async def get_model_response(
        self, 
        model: str, 
        prompt: str, 
        max_retries: int = 3
    ) -> ModelResponse:
        """Get response from model with comprehensive error handling"""
        
        start_time = datetime.now()
        
        # Check rate limiting
        if self._is_rate_limited(model):
            return ModelResponse(
                success=False,
                error_type=ErrorType.RATE_LIMIT_ERROR,
                error_message=f"Rate limit exceeded for model {model}",
                model_name=model
            )
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as session:
                    
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "max_tokens": 2000,  # Prevent excessive responses
                        "temperature": 0.7
                    }
                    
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "ComplexFlow-Arena/1.0"
                    }
                    
                    async with session.post(
                        self.base_url,
                        json=payload,
                        headers=headers
                    ) as response:
                        
                        response_time = (datetime.now() - start_time).total_seconds()
                        
                        if response.status == 200:
                            data = await response.json()
                            content = self._extract_content(data)
                            
                            if content:
                                return ModelResponse(
                                    success=True,
                                    content=content,
                                    response_time=response_time,
                                    model_name=model
                                )
                            else:
                                raise ModelServiceError("Empty response content")
                        
                        elif response.status == 429:  # Rate limited
                            self._update_rate_limit(model)
                            return ModelResponse(
                                success=False,
                                error_type=ErrorType.RATE_LIMIT_ERROR,
                                error_message="API rate limit exceeded",
                                model_name=model
                            )
                        
                        elif response.status >= 500:  # Server error, retry
                            if attempt < max_retries - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            
                        # Client error or final server error
                        error_text = await response.text()
                        return ModelResponse(
                            success=False,
                            error_type=ErrorType.API_ERROR,
                            error_message=f"API error {response.status}: {error_text}",
                            model_name=model
                        )
                        
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                return ModelResponse(
                    success=False,
                    error_type=ErrorType.TIMEOUT_ERROR,
                    error_message=f"Request timeout after {self.timeout}s",
                    model_name=model
                )
                
            except aiohttp.ClientError as e:
                self.logger.error(f"Network error for model {model}: {e}")
                return ModelResponse(
                    success=False,
                    error_type=ErrorType.NETWORK_ERROR,
                    error_message=f"Network error: {str(e)}",
                    model_name=model
                )
                
            except Exception as e:
                self.logger.error(f"Unexpected error for model {model}: {e}")
                return ModelResponse(
                    success=False,
                    error_type=ErrorType.API_ERROR,
                    error_message=f"Unexpected error: {str(e)}",
                    model_name=model
                )
        
        return ModelResponse(
            success=False,
            error_type=ErrorType.API_ERROR,
            error_message="Max retries exceeded",
            model_name=model
        )
    
    def _extract_content(self, response_data: Dict) -> Optional[str]:
        """Safely extract content from API response"""
        try:
            choices = response_data.get("choices", [])
            if not choices:
                return None
            
            message = choices[0].get("message", {})
            content = message.get("content", "").strip()
            
            return content if content else None
            
        except (KeyError, IndexError, AttributeError):
            return None
    
    def _is_rate_limited(self, model: str) -> bool:
        """Check if model is currently rate limited"""
        if model not in self.rate_limit_tracker:
            return False
        
        last_limit = self.rate_limit_tracker[model]
        return datetime.now() < last_limit + timedelta(minutes=1)
    
    def _update_rate_limit(self, model: str):
        """Update rate limit tracker for model"""
        self.rate_limit_tracker[model] = datetime.now()