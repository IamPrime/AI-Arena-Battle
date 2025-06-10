import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time

@dataclass
class APIResponse:
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    status_code: Optional[int] = None

class ModelAPIClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def get_response(self, model: str, prompt: str, retries: int = 3) -> APIResponse:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        
        for attempt in range(retries):
            try:
                response = self.session.post(
                    self.base_url,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return APIResponse(success=True, content=content)
                else:
                    return APIResponse(
                        success=False,
                        error=f"API returned status {response.status_code}",
                        status_code=response.status_code
                    )
                    
            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return APIResponse(success=False, error="Request timeout")
            
            except requests.exceptions.RequestException as e:
                return APIResponse(success=False, error=f"Request failed: {str(e)}")
        
        return APIResponse(success=False, error="Max retries exceeded")