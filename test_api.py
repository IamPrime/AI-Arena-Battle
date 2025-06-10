import asyncio
import aiohttp
from src.config import Config

async def test_api_connection():
    config = Config()
    
    # Test different endpoints
    endpoints_to_test = [
        "https://genai.rcac.purdue.edu/ollama/api/chat",
        "https://genai.rcac.purdue.edu/api/chat/completions"
    ]
    
    # Test payloads for different endpoint types
    ollama_payload = {
        "model": "mistral:latest",
        "prompt": "Hello, can you respond with a simple greeting?",
        "stream": False
    }
    
    openai_payload = {
        "model": "mistral:latest",
        "messages": [
            {
                "role": "user", 
                "content": "Hello, can you respond with a simple greeting?"
            }
        ],
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    
    for endpoint in endpoints_to_test:
        print(f"\n{'='*50}")
        print(f"Testing endpoint: {endpoint}")
        
        # Choose payload based on endpoint
        if "chat/completions" in endpoint:
            payload = openai_payload
        else:
            payload = ollama_payload
            
        print(f"Payload: {payload}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    print(f"Status Code: {response.status}")
                    
                    response_text = await response.text()
                    print(f"Raw Response: {response_text[:500]}...")  # Truncate long responses
                    
                    if response.status == 200:
                        try:
                            response_json = await response.json()
                            print("✅ SUCCESS! This endpoint works.")
                            
                            # Try to extract the actual response content
                            if "response" in response_json:
                                print(f"Response content: {response_json['response']}")
                            elif "choices" in response_json:
                                print(f"Response content: {response_json['choices'][0]['message']['content']}")
                            
                            return endpoint, payload  # Return working endpoint
                            
                        except Exception as e:
                            print(f"Failed to parse JSON: {e}")
                    else:
                        print(f"❌ HTTP Error: {response.status}")
                        
        except Exception as e:
            print(f"❌ Connection Error: {e}")
    
    print(f"\n{'='*50}")
    print("❌ None of the endpoints worked. Check:")
    print("1. Network connectivity")
    print("2. API key validity") 
    print("3. Server availability")
    print("4. Correct base URL")

if __name__ == "__main__":
    result = asyncio.run(test_api_connection())
    if result:
        endpoint, payload = result
        print(f"\n🎉 Use this endpoint: {endpoint}")
        print(f"🎉 Use this payload format: {payload}")
