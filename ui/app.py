import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title = "product Mind", page_icon="📓",layout = "wide")
st.title("Product Mind - Agentic Intelligence")
st.caption("Upload product documentation or connect to database, then ask anything.")

with st.sidebar:
    st.header("Load Knowledge Base")
    
    load_type = st.radio("Source type", ["PDF/Image File", "URL"])
    
    if load_type == "PDF/Image File":
        uploaded_file = st.file_uploader("Upload file", type=["pdf", "png", "jpg", "jpeg"])
        if st.button("Load File") and uploaded_file:
            with st.spinner("Extracting and embedding..."):
                response = requests.post(
                    f"{API_BASE}/load/file",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue())},
                    timeout=120
                )
            if response.ok:
                data = response.json()
                st.success(f"Loaded {data['chunks_stored']} chunks from {data['source']}")
            else:
                st.error(response.json().get("detail", "Failed"))
    else:
        url_input = st.text_input("Enter URL")
        if st.button("Load URL") and url_input:
            with st.spinner("Scraping and embedding..."):
                response = requests.post(
                    f"{API_BASE}/load/url",
                    json={"url": url_input}
                )
            if response.ok:
                data = response.json()
                st.success(f"Loaded {data['chunks_stored']} chunks from URL")
            else:
                st.error(response.json().get("detail", "Failed"))

st.markdown("---")
query = st.text_input("Ask a question", placeholder="e.g. What is the total number of orders?")

if st.button("Ask", type="primary") and query:
    with st.spinner("Thinking..."):
        response = requests.post(f"{API_BASE}/query", json={"query": query})
    
    if response.ok:
        result = response.json()
        
        st.markdown("### Answer")
        st.write(result.get("answer", "No answer returned."))
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Path", result.get("source", "unknown").upper())
        
        with col2:
            if result.get("source") == "rag":
                st.metric("Similarity Score", f"{result.get('score', 0):.3f}")
            elif result.get("source") == "tool":
                st.metric("Tool Used", result.get("tool", "unknown"))
    else:
        st.error(f"Query failed: {response.json().get('detail', 'Unknown error')}")