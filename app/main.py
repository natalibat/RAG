import streamlit as st

if __name__ == '__main__':
    
    pages = {
        "Thesis": [
            st.Page("pages/Tasks.py", title="Description"),
            st.Page("rag_chatbot.py", title="RAG Chatbot"),
            st.Page("pages/chat_postgres.py", title="Talk to your DB")
        ],
    }
    pg = st.navigation(pages)
    pg.run()