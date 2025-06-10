# 🔌 API Documentation

## 🌐 API Integration

### Endpoint Configuration

```python
OLLAMA_URL = "https://genai.rcac.purdue.edu/ollama/api/chat"
OPENAI_COMPATIBLE_URL = "https://genai.rcac.purdue.edu/api/chat/completions"
```

### Authentication

All API requests require authentication via API key in headers:

```python
headers = {
  "Authorization": f"Bearer {API_KEY}",
  "Content-Type": "application/json"
}
```

## 📨 Request Format

### Chat Completion Request

```json
{
"model": "model_name",
"messages": [{"role": "user", "content": "user_prompt"}],
"stream": false
}
```

### Example Request

```python
import requests

payload = {
  "model": "llama3.1:70b-instruct-q4_K_M",
  "messages": [
      {"role": "user", "content": "Explain quantum computing"}
  ],
  "stream": False
}

response = requests.post(
  "https://genai.rcac.purdue.edu/api/chat/completions",
  headers={"Authorization": f"Bearer {API_KEY}"},
  json=payload
)
```

## 📊 Database Schema

### Vote Document Structure

```json
{
"_id": "ObjectId",
"ip_hash": "hash(user_ip)",
"timestamp": "2025-06-06T12:00:00.000Z",
"prompt": "User's input prompt",
"prompt_hash": "hash(prompt)",
"model_a": "codellama:latest",
"model_b": "llama3.1:70b-instruct-q4_K_M",
"vote": "A | B | Tie | Both are bad"
}
```

### Database Operations

#### Insert Vote

```python
from datetime import datetime, timezone

vote_document = {
  "ip_hash": hash(user_ip),
  "timestamp": datetime.now(timezone.utc),
  "prompt": prompt,
  "prompt_hash": hash(prompt),
  "model_a": model_a,
  "model_b": model_b,
  "vote": vote,
}
result = self.db.votes.insert_one(vote_document)
```

#### Query Votes

```python
# Get all votes for a specific model
votes = collection.find({
  "$or": [
      {"model_a": "llama3.1:70b"}, 
      {"model_b": "llama3.1:70b"}
  ]
})

# Get votes within date range
from datetime import datetime, timedelta
recent_votes = collection.find({
  "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
})
```

## 🔄 Rate Limiting

### Rate Limit Handling

The application implements rate limiting for API calls:

```python
from datetime import datetime, timedelta

def _is_rate_limited(self, model: str) -> bool:
  """Check if model is currently rate limited"""
  if model not in self.rate_limit_tracker:
      return False
    
  last_limit = self.rate_limit_tracker[model]
  return datetime.now() < last_limit + timedelta(minutes=1)
```

### Rate Limit Response

When rate limited, the API returns:

```json
{
"error": {
  "message": "Rate limit exceeded",
  "type": "rate_limit_error",
  "code": "rate_limit_exceeded"
}
}
```

## 📈 Response Handling

### Successful Response

```json
{
"choices": [
  {
    "message": {
      "role": "assistant",
      "content": "Model response content here..."
    },
    "finish_reason": "stop"
  }
],
"model": "llama3.1:70b-instruct-q4_K_M",
"usage": {
  "prompt_tokens": 10,
  "completion_tokens": 50,
  "total_tokens": 60
}
}
```

### Error Response

```json
{
"error": {
  "message": "Error description",
  "type": "error_type",
  "code": "error_code"
}
}
```

## 🔧 Model Configuration

### Available Models

| Model                          | Specialization        | Context Length |
|--------------------------------|-----------------------|----------------|
| `codellama:latest`             | Code generation       | 16K            |
| `deepseek-r1:14b`              | Reasoning             | 32K            |
| `gemma3:12b`                   | General purpose       | 8K             |
| `llama3.1:70b-instruct-q4_K_M` | Instruction following | 128K           |
| `llava:latest`                 | Vision-language       | 4K             |
| `mistral:latest`               | General purpose       | 32K            |
| `phi4:latest`                  | Efficient reasoning   | 16K            |
| `qwen2.5:72b`                  | Multilingual          | 32K            |

### Model Selection Logic

```python
import random

def select_random_models(available_models, exclude_rate_limited=True):
  """Select two different models randomly"""
  if exclude_rate_limited:
      available_models = [
          m for m in available_models 
          if not _is_rate_limited(m)
      ]
    
  if len(available_models) < 2:
      raise ValueError("Not enough available models")
    
  return random.sample(available_models, 2)
```

## 🔍 API Testing

### Test API Connection

```python
import requests
import os

def test_api_connection():
  """Test basic API connectivity"""
  api_key = os.getenv('API_KEY')
  if not api_key:
      raise ValueError("API_KEY environment variable not set")
    
  headers = {
      "Authorization": f"Bearer {api_key}",
      "Content-Type": "application/json"
  }
    
  payload = {
      "model": "llama3.1:70b-instruct-q4_K_M",
      "messages": [{"role": "user", "content": "Hello"}],
      "stream": False
  }
    
  try:
      response = requests.post(
          "https://genai.rcac.purdue.edu/api/chat/completions",
          headers=headers,
          json=payload,
          timeout=30
      )
      response.raise_for_status()
      return response.json()
  except requests.exceptions.RequestException as e:
      print(f"API test failed: {e}")
      return None
```

### Validate Response Format

```python
def validate_response(response_data):
  """Validate API response structure"""
  required_fields = ['choices']
    
  for field in required_fields:
      if field not in response_data:
          raise ValueError(f"Missing required field: {field}")
    
  if not response_data['choices']:
      raise ValueError("Empty choices array")
    
  choice = response_data['choices'][0]
  if 'message' not in choice or 'content' not in choice['message']:
      raise ValueError("Invalid choice structure")
    
  return True
```

## 🚀 Usage Examples

### Basic Chat Completion

```python
import requests
import os

class ComplexFlowAPI:
  def __init__(self):
      self.api_key = os.getenv('API_KEY')
      self.base_url = "https://genai.rcac.purdue.edu/api/chat/completions"
      self.headers = {
          "Authorization": f"Bearer {self.api_key}",
          "Content-Type": "application/json"
      }
    
  def chat_completion(self, model, messages, stream=False):
      """Send chat completion request"""
      payload = {
          "model": model,
          "messages": messages,
          "stream": stream
      }
        
      response = requests.post(
          self.base_url,
          headers=self.headers,
          json=payload,
          timeout=60
      )
        
      response.raise_for_status()
      return response.json()

# Usage
api = ComplexFlowAPI()
result = api.chat_completion(
  model="llama3.1:70b-instruct-q4_K_M",
  messages=[{"role": "user", "content": "Explain machine learning"}]
)
print(result['choices'][0]['message']['content'])
```

### Batch Model Comparison

```python
def compare_models(prompt, models):
  """Compare responses from multiple models"""
  api = ComplexFlowAPI()
  results = {}
    
  for model in models:
      try:
          response = api.chat_completion(
              model=model,
              messages=[{"role": "user", "content": prompt}]
          )
          results[model] = response['choices'][0]['message']['content']
      except Exception as e:
          results[model] = f"Error: {str(e)}"
    
  return results

# Usage
models = ["codellama:latest", "llama3.1:70b-instruct-q4_K_M"]
comparison = compare_models("Write a Python function to sort a list", models)
```
