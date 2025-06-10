from pymongo import MongoClient
from datetime import datetime, timezone
import streamlit as st
import random
import requests
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
API_KEY = os.getenv("API_KEY")

client = MongoClient(MONGO_URI)
db = client["llm_arena"]
collection = db["votes"]

def store_vote(prompt, model_a, model_b, selected_vote):
    print("Stored Model#1"+model_a)
    print("Stored Model#2"+model_b)
    document = {
        "timestamp": datetime.now(timezone.utc),
        "prompt": prompt,
        "model_a": model_a,
        "model_b": model_b,
        "vote": selected_vote
    }
    collection.insert_one(document)

# 🎨 Streamlit UI setup
st.set_page_config(page_title="ComplexFlow-Arena", page_icon="🤖", layout="wide")

# Header with navigation
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title("🤖 ComplexFlow-Arena Dashboard")
with col2:
    if st.button("📚 Documentation", key="docs_button"):
        st.switch_page("pages/Documentation.py")
with col3:
    # A clickable badge
    st.markdown(
        """
        <a href="https://github.com/PurdueRCAC" target="_blank">
            <img src="https://img.shields.io/badge/PurdueRCAC-Repository-blue" alt="PurdueRCAC Repository">
        </a>
        """,
        unsafe_allow_html=True
    )
    
st.markdown("*Compare LLM responses in anonymous battles and help shape the leaderboard*")
st.markdown("---")

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

random_models = random.sample(model_pool, 2)
model_a, model_b = random_models[0], random_models[1]


if "model_a" not in st.session_state:
    st.session_state["model_a"] = model_a
    print("Selected Model#1"+model_a)
if "model_b" not in st.session_state:
    st.session_state["model_b"] = model_b
    print("Selected Model#2"+model_b)

OLLAMA_URL = "https://genai.rcac.purdue.edu/ollama/api/chat"
OPENAI_COMPATIBLE_URL = "https://genai.rcac.purdue.edu/api/chat/completions"

def call_model(prompt, model):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    try:
        url = OLLAMA_URL
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            json_data = response.json()
            if "choices" in json_data:
                return json_data["choices"][0]["message"]["content"]
            elif "message" in json_data:
                return json_data["message"]["content"]
            else:
                return "[Error: Unexpected response format]"
        else:
            return f"[Error {response.status_code}: {response.text}]"
    except Exception as e:
        return f"[Exception: {str(e)}]"

st.subheader("⚔️ Anonymous Arena Battle")

# Add info about the current model pool
with st.expander("ℹ️ About the Arena"):
    st.markdown(f"""
    **How it works:**
    - Two models are randomly selected from our pool of {len(model_pool)} LLMs
    - Model identities remain hidden until after you vote
    - Your votes help determine which models perform better
    
    **Current Model Pool:**
    {', '.join([f'`{model}`' for model in model_pool])}
    
    **Need help?** Check out our [Documentation](pages/📚_Documentation.py) for detailed information.
    """)
    
prompt = st.text_input("Enter your prompt:", placeholder="Ask anything... e.g., 'Explain quantum computing in simple terms'", key="prompt")

if prompt:
    if "prev_prompt" not in st.session_state or st.session_state["prev_prompt"] != prompt:
        st.session_state["prev_prompt"] = prompt
        # Reset vote status when prompt changes
        st.session_state["has_voted"] = False
        st.session_state["vote_result"] = None
        with st.spinner("Calling Model A..."):
            st.session_state["response_a"] = call_model(prompt, st.session_state["model_a"])
        with st.spinner("Calling Model B..."):
            st.session_state["response_b"] = call_model(prompt, st.session_state["model_b"])

    st.write("Model A and Model B have generated their responses.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Model A response:**")
        st.success(st.session_state["response_a"])
    with col2:
        st.markdown("**Model B response:**")
        st.success(st.session_state["response_b"])

    st.subheader("🗳️ Cast your vote")
    
    # Initialize has_voted if not exists
    if "has_voted" not in st.session_state:
        st.session_state["has_voted"] = False
    if "vote_result" not in st.session_state:
        st.session_state["vote_result"] = None
    
    # Disable buttons if user has already voted
    buttons_disabled = st.session_state["has_voted"]
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        leftvote = st.button("👈 A is better", disabled=buttons_disabled)
    with col2:
        rightvote = st.button("👉 B is better", disabled=buttons_disabled)
    with col3:
        tie = st.button("🤝 Tie", disabled=buttons_disabled)
    with col4:
        bothbad = st.button("👎 Both are bad", disabled=buttons_disabled)

    # Only process votes if user hasn't voted yet
    if not st.session_state["has_voted"]:
        vote_result = None
        if leftvote:
            vote_result = "A"
            st.session_state["vote_result"] = "A"
            st.session_state["has_voted"] = True
        elif rightvote:
            vote_result = "B"
            st.session_state["vote_result"] = "B"
            st.session_state["has_voted"] = True
        elif tie:
            vote_result = "Tie"
            st.session_state["vote_result"] = "Tie"
            st.session_state["has_voted"] = True
        elif bothbad:
            vote_result = "Both Bad"
            st.session_state["vote_result"] = "Both Bad"
            st.session_state["has_voted"] = True
            
        if vote_result:
            store_vote(
                prompt,
                st.session_state["model_a"],
                st.session_state["model_b"],
                vote_result
            )
    
    # Display vote result and messages
    if st.session_state["has_voted"] and st.session_state["vote_result"]:
        if st.session_state["vote_result"] == "A":
            st.success("✅ You voted: A is better")
        elif st.session_state["vote_result"] == "B":
            st.success("✅ You voted: B is better")
        elif st.session_state["vote_result"] == "Tie":
            st.success("✅ You voted: Tie")
        elif st.session_state["vote_result"] == "Both Bad":
            st.success("❌ You voted: Both are bad")
            
        st.info("🎉 Thanks for voting! Your vote shapes the leaderboard, please vote RESPONSIBLY.")
        st.info("💡 You have already voted for this prompt. Enter a new prompt to vote again.")
        
else:
    st.info("Enter a prompt above to begin the battle.")
