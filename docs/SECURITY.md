# 🔐 Security Documentation

## 🔑 API Key Management

### Best Practices

#### Environment Variables

- Store API keys in `.env` file only
- Never commit API keys to version control
- Use different keys for development and production
- Rotate keys regularly (monthly recommended)

#### Key Storage

```env
# ✅ Correct - Environment variable
API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ❌ Wrong - Never hardcode in source
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Don't do this!
```

#### Key Validation

```python
import os
import re

def validate_api_key():
    """Validate API key format and presence"""
    api_key = os.getenv('API_KEY')
    
    if not api_key:
        raise ValueError("API_KEY environment variable not set")
    
    if not re.match(r'^sk-[a-zA-Z0-9]{32,}$', api_key):
        raise ValueError("Invalid API key format")
    
    return api_key
```

### Key Rotation Process

1. **Generate New Key**
   - Access RCAC GenAI Studio dashboard
   - Create new API key
   - Copy key securely

2. **Update Environment**

   ```bash
   # Update .env file
   API_KEY=sk-new-key-here
   ```

3. **Restart Application**

   ```bash
   docker restart complexflow-arena
   ```

4. **Revoke Old Key**
   - Delete old key from .env file
   - Replace with new key
   - Refresh application
   - Verify application still works

## 🛡️ Database Security

### MongoDB Atlas Security

#### Connection Security

- Use MongoDB Atlas connection strings with authentication
- Enable IP whitelisting for production
- Use TLS/SSL encryption for all connections
- Implement connection pooling

#### Access Control

```python
# ✅ Secure connection with authentication
MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority"

# ✅ Additional security options
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=False,
    serverSelectionTimeoutMS=5000
)
```

#### Data Validation

```python
from pymongo import MongoClient
from datetime import datetime

def validate_vote_data(vote_data):
    """Validate vote data before database insertion"""
    required_fields = ['timestamp', 'prompt', 'model_a', 'model_b', 'vote']
    
    for field in required_fields:
        if field not in vote_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate vote options
    valid_votes = ['A', 'B', 'Tie', 'Both Bad']
    if vote_data['vote'] not in valid_votes:
        raise ValueError("Invalid vote option")
    
    # Validate timestamp
    if not isinstance(vote_data['timestamp'], datetime):
        raise ValueError("Invalid timestamp format")
    
    return True
```

### Data Privacy

#### Personal Information

- No personal data collected or stored
- Anonymous voting system
- No user authentication required
- IP addresses not logged

#### Data Retention

```python
# Implement data retention policy
from datetime import datetime, timedelta

def cleanup_old_votes(days_to_keep=90):
    """Remove votes older than specified days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    result = collection.delete_many({
        "timestamp": {"$lt": cutoff_date}
    })
    
    return result.deleted_count
```

## 🌐 Network Security

### HTTPS Configuration

#### Production Deployment

```yaml
# docker-compose.yml for production
version: '3.8'
services:
  app:
    build: .
    environment:
      - API_KEY=${API_KEY}
      - MONGO_URI=${MONGO_URI}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`your-domain.com`)"
      - "traefik.http.routers.app.tls=true"
      - "traefik.http.routers.app.tls.certresolver=letsencrypt"
```

#### Request Validation

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_secure_session():
    """Create HTTP session with security configurations"""
    session = requests.Session()
    
    # Retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Security headers
    session.headers.update({
        'User-Agent': 'ComplexFlow-Arena/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    return session
```

## 🔒 Input Validation & Sanitization

### Prompt Sanitization

```python
import re
import html

def sanitize_prompt(prompt):
    """Sanitize user input prompt"""
    if not prompt or not isinstance(prompt, str):
        raise ValueError("Invalid prompt")
    
    # Remove potentially dangerous characters
    prompt = html.escape(prompt)
    
    # Limit length
    if len(prompt) > 1000:
        raise ValueError("Prompt too long")
    
    # Remove excessive whitespace
    prompt = re.sub(r'\s+', ' ', prompt.strip())
    
    return prompt
```

### SQL Injection Prevention

```python
# ✅ Using parameterized queries with PyMongo
def safe_database_query(model_name):
    """Safe database query using parameterized approach"""
    return collection.find({
        "$or": [
            {"model_a": model_name},
            {"model_b": model_name}
        ]
    })

# ❌ Never use string concatenation
def unsafe_query(model_name):
    """DON'T DO THIS - Vulnerable to injection"""
    query = f"SELECT * FROM votes WHERE model_a = '{model_name}'"
    return execute_query(query)
```

## 🚨 Error Handling Security

### Information Disclosure Prevention

```python
import logging

def secure_error_handler(error):
    """Handle errors without exposing sensitive information"""
    
    # Log detailed error for debugging
    logging.error(f"Application error: {str(error)}", exc_info=True)
    
    # Return generic message to user
    if isinstance(error, ConnectionError):
        return "Service temporarily unavailable. Please try again."
    elif isinstance(error, ValueError):
        return "Invalid input provided."
    else:
        return "An unexpected error occurred. Please try again."
```

### Rate Limiting

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id):
        """Check if client is within rate limits"""
        now = datetime.now()
        client_requests = self.requests[client_id]
        
        # Remove old requests
        cutoff = now - timedelta(seconds=self.time_window)
        client_requests[:] = [req for req in client_requests if req > cutoff]
        
        # Check limit
        if len(client_requests) >= self.max_requests:
            return False
        
        # Add current request
        client_requests.append(now)
        return True
```

## 📋 Security Checklist

### Development

- [x] API keys stored in environment variables
- [x] No sensitive data in version control
- [x] Input validation implemented
- [x] Error handling doesn't expose internals
- [ ] Dependencies regularly updated

### Deployment

- [ ] HTTPS enabled in production
- [ ] Database connections encrypted
- [ ] Rate limiting configured
- [ ] Monitoring and logging enabled
- [ ] Regular security updates applied

### Monitoring

- [ ] Failed authentication attempts logged
- [ ] Unusual API usage patterns detected
- [ ] Database access monitored
- [ ] Error rates tracked
- [ ] Performance metrics collected
