import streamlit as st
import os

st.set_page_config(
    page_title="ComplexFlow-Arena API",
    page_icon="🔌",
    layout="wide")

def load_documentation():
    """Load documentation content from markdown file"""
    docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "API.md")
    
    if os.path.exists(docs_path):
        with open(docs_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return """# 🔌 API Documentation

API file not found. Please ensure `docs/API.md` exists in your project directory."""

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
        if st.button("📚 Back to Documentation", key="sidebar_documentation"):
            st.switch_page("pages/About.py")

if __name__ == "__main__":
    main()