import streamlit as st

# MUST be the very first Streamlit command
st.set_page_config(page_title="ComplexFlow-Arena", page_icon="🤖", layout="wide")

import asyncio
import random
import aiohttp
from src.config import Config
from src.database.repository import DatabaseRepository
from src.security.input_sanitizer import SecurityValidator
from src.utils.logger import setup_logger
from datetime import datetime, timezone

# Initialize configuration
config = Config()
logger = setup_logger(__name__)

# Environment-based debug toggle
SHOW_DEBUG = config.show_debug

# API endpoints
OLLAMA_URL = "https://genai.rcac.purdue.edu/ollama/api/generate"
OPENAI_COMPATIBLE_URL = "https://genai.rcac.purdue.edu/api/chat/completions"
# OPENAI_COMPATIBLE_URL = "https://genai.rcac.purdue.edu/ollama/api/generate"

# Model calling function
async def call_model(prompt, model):
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }
    
    # OpenAI-compatible format
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    # Try primary endpoint first
    urls_to_try = [OPENAI_COMPATIBLE_URL, OLLAMA_URL]
    
    for url in urls_to_try:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    headers=headers, 
                    json=body,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        json_data = await response.json()
                        
                        # Extract content from response
                        if "choices" in json_data:
                            content = json_data["choices"][0]["message"]["content"]
                            logger.info(f"✅ {model} responded via {url}")
                            return {"success": True, "content": content}
                        elif "message" in json_data:
                            content = json_data["message"]["content"]
                            logger.info(f"✅ {model} responded via {url}")
                            return {"success": True, "content": content}
                        else:
                            logger.warning(f"⚠️ Unexpected response format from {url}: {json_data}")
                            continue
                    else:
                        logger.warning(f"❌ HTTP {response.status} from {url}: {await response.text()}")
                        continue
                        
        except Exception as e:
            logger.error(f"❌ Error calling {url} for {model}: {str(e)}")
            continue
    
    # If all endpoints failed
    return {"success": False, "error_message": f"All endpoints failed for model {model}"}

# Initialize database
@st.cache_resource
def init_database():
    try:
        db_repo = DatabaseRepository(config.mongo_uri)
        # Test the connection
        if db_repo.test_connection():
            logger.info("✅ Database connection successful")
            return db_repo
        else:
            raise Exception("Connection test failed")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        st.error(f"❌ Database connection failed: {str(e)}")
        return None

db_repo = init_database()

# Initialize session ID for tracking
if "session_id" not in st.session_state:
    st.session_state["session_id"] = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"

# Header
st.title("🤖 ComplexFlow-Arena Dashboard")
st.markdown("*Compare LLM responses with enterprise-grade security and performance*")
st.markdown("---")

# Model pool
model_pool = [
    "codellama:latest",
    "deepseek-r1:14b", 
    "gemma3:12b",
    "llama3.1:70b-instruct-q4_K_M",
    "llava:latest",
    "mistral:latest",
    "phi4:latest",
    "qwen2.5:72b"
]

# Function to save vote
def save_vote(prompt, model_a, model_b, vote):
    """Save vote to database with comprehensive error handling"""
    if not db_repo:
        logger.error("Database repository not initialized")
        return False, "Database not available"
    
    try:
        # Use the repository's store_vote method instead of direct database access
        success = db_repo.store_vote(
            prompt=prompt,
            model_a=model_a,
            model_b=model_b,
            vote=vote,
            user_ip=st.session_state.get("session_id", "unknown")  # Use session_id as user identifier
        )
        
        if success:
            logger.info(f"✅ Vote saved successfully: {vote} for {model_a} vs {model_b}")
            return True, "Vote saved successfully"
        else:
            logger.error("❌ Vote storage failed")
            return False, "Vote storage failed"
            
    except Exception as e:
        logger.error(f"❌ Error saving vote: {str(e)}")
        return False, f"Database error: {str(e)}"

# Always randomize
if "model_a" not in st.session_state or "model_b" not in st.session_state:
    # First time initialization
    random_models = random.sample(model_pool, 2)
    st.session_state["model_a"] = random_models[0]
    st.session_state["model_b"] = random_models[1]
    logger.info(f"Initial Model Selection - A: {st.session_state['model_a']}, B: {st.session_state['model_b']}")


# Debug info
if SHOW_DEBUG:
    with st.sidebar:
        st.header("🔧 Debug Info")
        st.write(f"Model A: {st.session_state.get('model_a', 'Not set')}")
        st.write(f"Model B: {st.session_state.get('model_b', 'Not set')}")
        st.write(f"API Key: {'✅ Set' if config.api_key else '❌ Not set'}")

        st.markdown("**Endpoints:**")
        st.code(f"Primary: {OPENAI_COMPATIBLE_URL}")
        st.code(f"Fallback: {OLLAMA_URL}")
    
        # Refresh Models button
        if st.button("🔄 Refresh Models"):
            random_models = random.sample(model_pool, 2)
            st.session_state["model_a"] = random_models[0]
            st.session_state["model_b"] = random_models[1]
            # Clear previous responses and voting state
            if "prev_prompt" in st.session_state:
                del st.session_state["prev_prompt"]
            if "response_a" in st.session_state:
                del st.session_state["response_a"]
            if "response_b" in st.session_state:
                del st.session_state["response_b"]
            if "has_voted" in st.session_state:
                del st.session_state["has_voted"]
            if "vote_result" in st.session_state:
                del st.session_state["vote_result"]
            logger.info(f"Manual Model Refresh - A: {st.session_state['model_a']}, B: {st.session_state['model_b']}")
            st.rerun()
    
        # Test API button
        if st.button("🧪 Test API Connection"):
            with st.spinner("Testing API..."):
                try:
                    test_response = asyncio.run(call_model("Say hello", "mistral:latest"))
                    if test_response["success"]:
                        st.success("✅ API Connection Working")
                        st.write(f"Response: {test_response['content'][:100]}...")
                    else:
                        st.error(f"❌ API Error: {test_response['error_message']}")
                except Exception as e:
                    st.error(f"❌ Connection Error: {str(e)}")

        # Test Database button
        if st.button("🧪 Test Database Connection"):
            if db_repo:
                try:
                    # Test database connection
                    if db_repo.test_connection():
                        st.success("✅ Database Connection Working")

                        # Test vote collection
                        vote_count = db_repo.get_vote_count()
                        st.write(f"Total votes in database: {vote_count}")
                    else:
                        st.error("❌ Database connection test failed")
                except Exception as e:
                    st.error(f"❌ Database Error: {str(e)}")
            else:
                st.error("❌ Database not initialized")
    
        # Clean Database button
        if st.button("🧹 Clean Database"):
            if db_repo:
                try:
                    success = db_repo.cleanup_model_stats()
                    if success:
                        st.success("✅ Database cleaned successfully")
                    else:
                        st.error("❌ Database cleanup failed")
                except Exception as e:
                    st.error(f"❌ Cleanup error: {e}")

# About section
with st.expander("ℹ️ About the Arena"):
    st.markdown(f"""
    **How it works:**
    - Two models are randomly selected from our pool of {len(model_pool)} LLMs
    - Model identities remain hidden until after you vote
    - Your votes help determine which models perform better
    
    **Current Model Pool:**
    {', '.join([f'`{model}`' for model in model_pool])}
    
    **API Endpoints:**
    - Primary: `{OPENAI_COMPATIBLE_URL}`
    - Fallback: `{OLLAMA_URL}`
    """)

# Show database status warning if needed
if not db_repo:
    st.warning("⚠️ Database connection unavailable. Voting will be disabled.")

# Prompt input with validation
prompt = st.text_input(
    "Enter your prompt:", 
    placeholder="Ask anything... e.g., 'Explain quantum computing in simple terms'",
    key="prompt"
)

if prompt:
    # Validate input
    try:
        is_valid, error_msg = SecurityValidator.validate_user_input(prompt)
        if not is_valid:
            st.error(f"❌ {error_msg}")
            st.stop()
        
        # Sanitize input
        sanitized_prompt = SecurityValidator.sanitize_input(prompt)
        
    except Exception as e:
        st.error(f"❌ Input validation error: {str(e)}")
        logger.error(f"Input validation error: {str(e)}")
        st.stop()
    
    # Get model responses
    if "prev_prompt" not in st.session_state or st.session_state["prev_prompt"] != prompt:
        # New prompt detected - randomize models for fair comparison
        random_models = random.sample(model_pool, 2)
        st.session_state["model_a"] = random_models[0]
        st.session_state["model_b"] = random_models[1]

        st.session_state["prev_prompt"] = prompt
        st.session_state["has_voted"] = False

        # Clear previous responses
        if "response_a" in st.session_state:
            del st.session_state["response_a"]
        if "response_b" in st.session_state:
            del st.session_state["response_b"]
        if "vote_result" in st.session_state:
            del st.session_state["vote_result"]

        logger.info(f"New Prompt - Model Selection - A: {st.session_state['model_a']}, B: {st.session_state['model_b']}")
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Call models
        async def get_responses():
            try:
                status_text.text(f"🤖 Calling Model A: {st.session_state['model_a']}...")
                progress_bar.progress(25)
                
                response_a = await call_model(sanitized_prompt, st.session_state["model_a"])
                
                progress_bar.progress(50)
                status_text.text(f"🤖 Calling Model B: {st.session_state['model_b']}...")
                
                response_b = await call_model(sanitized_prompt, st.session_state["model_b"])
                
                progress_bar.progress(100)
                status_text.text("✅ Both models responded!")
                
                return response_a, response_b
                
            except Exception as e:
                logger.error(f"Error in get_responses: {str(e)}")
                progress_bar.progress(100)
                status_text.text(f"❌ Error: {str(e)}")
                return None, None
        
        responses = asyncio.run(get_responses())
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if responses[0] is not None and responses[1] is not None:
            st.session_state["response_a"] = responses[0]
            st.session_state["response_b"] = responses[1]
        else:
            st.error("❌ Failed to get responses from models")
            st.stop()
    
    # Display responses
    st.subheader("⚔️ Model Battle Results")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**🤖 {st.session_state['model_a']}:**")
        response_a = st.session_state.get("response_a")
        
        if response_a and response_a.get("success"):
            if response_a.get("content") and response_a["content"].strip():
                st.success(response_a["content"])
            else:
                st.warning("⚠️ Model returned empty response")
        else:
            error_msg = response_a.get("error_message", "Unknown error") if response_a else "No response"
            st.error(f"❌ Error: {error_msg}")
    
    with col2:
        st.markdown(f"**🤖 {st.session_state['model_b']}:**")
        response_b = st.session_state.get("response_b")
        
        if response_b and response_b.get("success"):
            if response_b.get("content") and response_b["content"].strip():
                st.success(response_b["content"])
            else:
                st.warning("⚠️ Model returned empty response")
        else:
            error_msg = response_b.get("error_message", "Unknown error") if response_b else "No response"
            st.error(f"❌ Error: {error_msg}")
    
    # Check if both responses are valid for voting
    both_successful = (
        st.session_state.get("response_a") and 
        st.session_state["response_a"].get("success") and 
        st.session_state["response_a"].get("content") and
        st.session_state.get("response_b") and 
        st.session_state["response_b"].get("success") and 
        st.session_state["response_b"].get("content")
    )

# Voting section
    if both_successful and not st.session_state.get("has_voted", False):
        if not db_repo:
            st.warning("⚠️ Voting disabled: Database not available")
        else:
            st.subheader("🗳️ Cast your vote")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("👈 A is better"):
                    success, message = save_vote(
                        sanitized_prompt,
                        st.session_state["model_a"],
                        st.session_state["model_b"],
                        "A"
                    )
                    if success:
                        st.session_state["has_voted"] = True
                        st.session_state["vote_result"] = "A"
                        st.success("✅ Vote recorded: A is better!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to record vote: {message}")
            
            with col2:
                if st.button("👉 B is better"):
                    success, message = save_vote(
                        sanitized_prompt,
                        st.session_state["model_a"],
                        st.session_state["model_b"],
                        "B"
                    )
                    if success:
                        st.session_state["has_voted"] = True
                        st.session_state["vote_result"] = "B"
                        st.success("✅ Vote recorded: B is better!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to record vote: {message}")
            
            with col3:
                if st.button("🤝 Tie"):
                    success, message = save_vote(
                        sanitized_prompt,
                        st.session_state["model_a"],
                        st.session_state["model_b"],
                        "Tie"
                    )
                    if success:
                        st.session_state["has_voted"] = True
                        st.session_state["vote_result"] = "Tie"
                        st.success("✅ Vote recorded: It's a tie!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to record vote: {message}")
            
            with col4:
                if st.button("👎 Both are bad"):
                    success, message = save_vote(
                        sanitized_prompt,
                        st.session_state["model_a"],
                        st.session_state["model_b"],
                        "Both Bad"
                    )
                    if success:
                        st.session_state["has_voted"] = True
                        st.session_state["vote_result"] = "Both Bad"
                        st.success("✅ Vote recorded: Both are bad!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to record vote: {message}")
    
    elif both_successful:
        # Show vote result after voting
        if st.session_state.get("vote_result"):
            st.success(f"✅ You voted: {st.session_state['vote_result']}")
            st.info("🎉 Thanks for voting! Your vote shapes the leaderboard.")
            st.info("💡 Enter a new prompt above to vote again.")

# Replace the leaderboard section in main.py with this corrected version:

# Display leaderboard
with st.expander("🏆 Model Leaderboard"):
    if not db_repo:
        st.warning("⚠️ Leaderboard unavailable: Database not connected")
    else:
        try:
            leaderboard = db_repo.get_model_leaderboard()
            if leaderboard:
                st.markdown("### 📊 Current Rankings")
                for i, model_stats in enumerate(leaderboard, 1):
                    # Handle None/missing model names
                    model_name = model_stats.get('model', 'Unknown Model')
                    if model_name is None:
                        model_name = 'Unknown Model'
                    
                    # Handle None/missing statistics
                    win_rate = model_stats.get('win_rate', 0) or 0
                    total_votes = model_stats.get('total_votes', 0) or 0
                    
                    rank_col, model_col, stats_col = st.columns([1, 3, 2])
                    
                    with rank_col:
                        if i == 1:
                            st.markdown("🥇")
                        elif i == 2:
                            st.markdown("🥈")
                        elif i == 3:
                            st.markdown("🥉")
                        else:
                            st.markdown(f"**{i}.**")
                    
                    with model_col:
                        st.markdown(f"**{model_name}**")
                    
                    with stats_col:
                        st.markdown(f"Win Rate: **{win_rate:.1%}**")
                        st.caption(f"({total_votes} votes)")
                    
                    st.divider()
            else:
                st.info("📈 No voting data available yet. Be the first to vote and help build the leaderboard!")
                st.markdown("*Vote on model responses above to see rankings here.*")
        
        except Exception as e:
            st.error(f"❌ Unable to load leaderboard data: {str(e)}")
            logger.error(f"Leaderboard error: {str(e)}")
            st.caption("Please try refreshing the page or contact support if the issue persists.")
            
            # Add debug info to help troubleshoot
            if st.checkbox("Show debug info"):
                st.code(f"Error type: {type(e).__name__}")
                st.code(f"Error details: {str(e)}")
                try:
                    raw_data = db_repo.get_model_leaderboard()
                    st.json(raw_data)
                except:
                    st.write("Could not retrieve raw data")
                
# Footer with database status
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if db_repo:
        try:
            vote_count = db_repo.get_vote_count()
            st.metric("Total Votes", vote_count)
        except:
            st.metric("Total Votes", "Error")
    else:
        st.metric("Total Votes", "N/A")

with col2:
    st.metric("Active Models", len(model_pool))

with col3:
    db_status = "🟢 Connected" if db_repo else "🔴 Disconnected"
    st.metric("Database Status", db_status)