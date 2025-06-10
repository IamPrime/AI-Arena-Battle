# 🛠️ Troubleshooting Documentation

## 🚨 Common Issues

### 1. Application Won't Start

#### Symptoms

- Docker container exits immediately
- "Port already in use" error
- Environment variable errors

#### Solutions

##### Check Environment File

```bash
# Verify .env file exists
ls -la .env

# Check file contents (be careful not to expose secrets)
head .env
```

##### Verify Docker Status

```bash
# Check if Docker is running
docker --version
docker ps

# Check port availability
netstat -tulpn | grep :8501
```

##### Fix Port Conflicts

```bash
# Use different port
docker run --env-file .env -p 8080:8501 complexflow-arena

# Or kill process using port 8501
sudo lsof -ti:8501 | xargs kill -9
```

### 2. Models Not Responding

#### Indicators

- "Failed to get response" errors
- Infinite loading spinners
- API timeout messages

#### Diagnostic Steps

##### Test API Connectivity

```bash
# Test API endpoint
curl -X POST "https://genai.rcac.purdue.edu/api/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:70b-instruct-q4_K_M",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'
```

##### Verify API Key

```python
import os
import requests

def test_api_key():
    api_key = os.getenv('API_KEY')
    if not api_key:
        print("❌ API_KEY not found in environment")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ API_KEY format appears invalid")
        return False
    
    print("✅ API_KEY format looks correct")
    return True
```

##### Check Rate Limiting

```python
# Check if models are rate limited
def check_rate_limits():
    from src.services.model_service import ModelService
    service = ModelService()
    
    models = ["llama3.1:70b-instruct-q4_K_M", "codellama:latest"]
    for model in models:
        if service._is_rate_limited(model):
            print(f"⚠️ {model} is rate limited")
        else:
            print(f"✅ {model} is available")
```

#### Resolution

##### API Key Issues

````bash
# Regenerate API key from RCAC GenAI Studio
# Update .env file
# Restart container
````
