import streamlit as st
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os
import chromadb
from chromadb.utils import embedding_functions
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool
from langchain.chains import LLMMathChain
from langchain_core.messages import HumanMessage, AIMessage
from core.simple_rag import ChromaSearchTool, DocumentProcessor, get_chroma_client
from langdetect import detect

load_dotenv()

st.set_page_config(page_title="Thesis", page_icon="📚", layout="wide")
st.title("RAG Chatbot")

llm = AzureChatOpenAI(
    temperature=0.3,
    azure_deployment="gpt-4",
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"))

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_type="azure",
    model_name="text-embedding-ada-002",
    api_version="2023-05-15"
)

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()
if "chroma_client" not in st.session_state:
     st.session_state.chroma_client = get_chroma_client()

prompt = PromptTemplate(
    input_variables=["input", "tools", "tool_names", "chat_history", "agent_scratchpad"],
    template="""
Assistant is designed to help with a variety of tasks using specific tools when required. The assistant must always:
1. First, determine if the user's question is related to the legal domain.
2. If the question is not related to law or legal matters — respond with "I don't know".
3. If the question is legal, continue reasoning and use tools as necessary.
4. Acknowledge uncertainty when information is incomplete or unclear.
5. Explicitly say "I don't know" when:
   - The retrieved context doesn't contain sufficient information
   - The confidence in the answer is low
   - Multiple contradicting pieces of information are found
   - The question goes beyond the available tools and knowledge

Tools available:
{tools}

Chat History:
{chat_history}

Use this format:
Question: the input question to answer  
Thought: check if the question is legal. If not, say "I don't know". Otherwise, reason about what needs to be done.  
Action: tool to use, must be from [{tool_names}]  
Action Input: input for the tool  
Observation: result from tool  
... (repeat Thought/Action/Action Input/Observation if needed)  
Thought: decide on final answer  
Final Answer: answer to the original question in the same language as the user's question with all provided information or provide information that you found with apologies  
                                      
Question: {input}  
Thought: {agent_scratchpad}
"""
)

chroma_tool = ChromaSearchTool(openai_ef)
chroma_db_tool =  Tool(
            name="SemanticSearch",
            func=chroma_tool.multiple_collection_search,
            description="""Useful for searching through stored knowledge to find relevant information. Input should be a search query. Try to search for a relavant information each time you can."""
        )

llm_math = LLMMathChain.from_llm(llm=llm)
math_tool = Tool(
    name='Calculator',
    func=llm_math.run,
    description='Useful for when you need to answer questions about math.'
)

# When giving tools to LLM, we must pass as list of tools
tools = [math_tool, chroma_db_tool]

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

# Create the agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=st.session_state.memory,
    verbose=True,
    max_iterations=3,
    handle_parsing_errors=True  
)

doc_processor = DocumentProcessor()

def display_chat_history():
    chat_history = st.session_state.memory.chat_memory.messages
    for message in reversed(chat_history):
        if isinstance(message, HumanMessage):
            st.write("Human: ", message.content)
        elif isinstance(message, AIMessage):
            st.write("Assistant: ", message.content)

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def get_language_instruction(lang_code):
    if lang_code == "uk":
        return "Відповідай українською мовою."
    elif lang_code == "fr":
        return "Réponds en français."
    elif lang_code == "en":
        return "Answer in English."
    else:
        return "Respond in the language the question was asked."

def prepare_input(user_input):
    lang = detect_language(user_input)
    instruction = get_language_instruction(lang)
    return f"{instruction}\n{user_input}"

def generate_response(input_text):
    prepared_input = prepare_input(input_text)
    try:
        response = agent_executor.invoke({"input": prepared_input})
        st.info(response["output"])
    except Exception as e:
        st.error(f"Error: {str(e)}")
       
col1, col2 = st.columns([1, 2])

def delete_collection(collection_name):
    try:
        st.session_state.chroma_client.delete_collection(collection_name)
        st.success(f"Collection '{collection_name}' deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting collection: {e}")

with col1:
    st.markdown("""
        <style>
            .custom-label {
                color: #FFD700;
                font-size: 19px;
                margin-bottom: -8px;
                line-height: 1;
            }
            div[data-testid="stFileUploader"] {
                padding-top: 0rem;
                margin-top: -10px;
            }
        </style>
        <div class='custom-label'>Choose a pdf, txt, docx file:</div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(label="", accept_multiple_files=False)
    if uploaded_file is not None and uploaded_file.name not in st.session_state.processed_files:
        with st.spinner("Processing your file..."):
            result = doc_processor.process_file(uploaded_file)

            if result["status"] == "exists":
                st.info(f"File '{uploaded_file.name}' was already processed and is ready to use.")
            else:
                st.success('Document processed successfully!')
            
            st.session_state.processed_files.add(uploaded_file.name)

    st.markdown("### Available Collections")
    try:
        collections = st.session_state.chroma_client.list_collections()
        if collections:
            for collection_name in collections:
                st.text(f"📄 {collection_name}")
        
                if st.button(f"Delete {collection_name}"):
                    delete_collection(collection_name)
                    
        else:
            st.text("No collections available")
    except:
        st.text("Looks like you haven't upload files yet")
        pass 

with col2:
    with st.form('my_form'):
        st.markdown("""
        <style>
            .custom-label {
                color: #FFD700;
                font-size: 18px;
                margin-bottom: -8px;
                line-height: 1;
            }

            div.stButton > button {
                background-color: #800000;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                transition: 0.3s;
            }

            div.stButton > button:hover {
                background-color: #F0FFFF;
                transform: scale(1.02);
            }
        </style>

        <div class='custom-label'>Enter text:</div>
    """, unsafe_allow_html=True)

        text = st.text_area(label=" ", height=150)

        submitted = st.form_submit_button('Submit')
        if submitted:
            
            generate_response(text)

        st.markdown("### Chat History")
        display_chat_history()
