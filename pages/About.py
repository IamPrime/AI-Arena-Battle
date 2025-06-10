import streamlit as st
import os

st.set_page_config(
    page_title="ComplexFlow-Arena Documentation",
    page_icon="📚",
    layout="wide")

def load_documentation():
    """Load documentation content from markdown file"""
    docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "ABOUT.md")
    
    if os.path.exists(docs_path):
        with open(docs_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return """# 📚 Documentation

Documentation file not found. Please ensure `docs/DOCUMENTATION.md` exists in your project directory.

## Quick Start
1. Set up your `.env` file with MongoDB URI and API key
2. Run with Docker: `docker run --env-file .env -p 8501:8501 complexflow-arena`
3. Access at http://localhost:8501

For detailed setup instructions, please refer to the README.md file."""

def main():
    # Load and display documentation
    doc_content = load_documentation()
    st.markdown(doc_content)
    
    # Add a sidebar with quick navigation
    with st.sidebar:
        st.markdown("---")
        st.header("🔗 Quick Links")
        
        if st.button("🏠 Back to Main Arena", key="sidebar_home"):
            st.switch_page("Arena.py")

if __name__ == "__main__":
    main()
