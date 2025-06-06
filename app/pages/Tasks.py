import streamlit as st
import pandas as pd

custom_css = """
<style>
body {
    color: white;
    font-size: 18px;
}
h1 {
    color: white !important;
}
h2, h3 {
    color: #FFD700 !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.title("Project Overview")

st.header("1. Domain Area")
st.markdown("""
The project belongs to the domain of **intelligent text information analysis**, combining:  
- Large Language Models (LLMs) for language understanding  
- Vector Databases for semantic search in unstructured data  
- Chatbot Interfaces for human-machine interaction  
- SQL querying for structured data extraction from relational databases


It includes two core modules:
""")
st.table(pd.DataFrame({
    "Module": ["RAG Module", "NL-to-SQL Module"],
    "Purpose": [
        "Works with unstructured text documents",
        "Interacts with structured relational databases"
    ]
}))

st.header("2. Project Goal")
st.markdown("""
The system aims to build an **agent-based assistant** that:
""")
st.table(pd.DataFrame({
    "Functionality": [
        "Answers natural language questions",
        "Retrieves knowledge from documents or databases",
        "Provides verified responses with explanation"
    ]
}))

st.header("3. Project Tasks")

st.subheader("Task 1: RAG Module")
st.markdown("**Main Functionality:**")
st.table(pd.DataFrame({
    "Step": [
        "File upload",
        "Chunking strategy",
        "Vectorization of text chunks",
        "Store in vector DB",
        "Question vectorization",
        "Search relevant context",
        "Answer generation via GPT-4"
    ]
}))

st.markdown("**Additional Requirements:**")
st.table(pd.DataFrame({
    "Requirement": [
        "Minimize hallucinations",
        "Context-aware answering",
        "Use agent-based architecture"
    ]
}))

st.subheader("Task 2: Natural Language to SQL Module")
st.markdown("**Main Functionality:**")
st.table(pd.DataFrame({
    "Step": [
        "Translate NL query to SQL",
        "Fetch DB schema dynamically",
        "Execute SQL query"
    ]
}))

st.markdown("**Response Presentation:**")
st.table(pd.DataFrame({
    "Condition": ["0 or 1 result", "More than 1 result", "All cases"],
    "Output": ["Natural language", "Table view", "Show SQL query"]
}))

st.header("4. Technologies Used")
st.table(pd.DataFrame({
    "Technology": [
        "LangChain",
        "ChromaDB",
        "Azure OpenAI",
        "Streamlit",
        "PostgreSQL"
    ],
    "Reason for Choice": [
        "Agent orchestration and integration with tools",
        "Fast local vector search with custom embedders",
        "Secure access to GPT-4 with enterprise safety",
        "Rapid creation of interactive UI",
        "Reliable open-source relational DB"
    ]
}))
