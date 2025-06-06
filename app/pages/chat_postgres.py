import streamlit as st
from dotenv import load_dotenv
import os
from core.postgres import *
from core.sql_commands import sql_commands
from langchain_community.utilities import SQLDatabase
from langchain_openai import AzureChatOpenAI
from langchain import hub
from typing_extensions import TypedDict
from typing_extensions import Annotated
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langgraph.graph import START, StateGraph
import pandas as pd
import json
import re
import ast
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()

read_pass = os.getenv('READ_PASS')

host = "localhost"
db_name = "postgres"
user = "postgres"
password = 'your_password'
port = "5432"
new_db_name = "chinook2"
file_path = 'chinook_postgreSql_short.sql'
agent_read_password = 'your_password'
read_only_user_name='readonly_user2'

if not check_tables_exist(host, new_db_name, port, user, password):
    create_postgres_database(new_db_name, host, port, user, password)
    run_sql_commands(new_db_name, host, port, user, password, sql_commands)
    create_readonly_user(
        host=host,
        database=new_db_name,
        user=user,
        password=password,
        new_user_name=read_only_user_name,
        agent_read_password=agent_read_password
        )    

database_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
db = SQLDatabase.from_uri(f"postgresql://{read_only_user_name}:{agent_read_password}@{host}:{port}/{new_db_name}")

openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
api_version = os.getenv('OPENAI_API_VERSION')

llm = AzureChatOpenAI(
    temperature=0.7,
    azure_deployment="gpt-4",
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"))

st.set_page_config(page_title="Thesis", page_icon="📚", layout="wide")
st.title("Talk to your data using natural language combined with SQL")

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]

def write_query(state: State):
    """Generate SQL query to fetch information."""
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 10,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return {"query": result["query"]}

def execute_query(state: State):
    """Execute SQL query."""
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}

def generate_answer(state: State):
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {state["question"]}\n'
        f'SQL Query: {state["query"]}\n'
        f'SQL Result: {state["result"]}\n'
        'if the answer is a list with more than two rows return as a markdown table otherwise just a simple answer'
    )
    response = llm.invoke(prompt)
    return {"answer": response.content}

query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_query, generate_answer]
)
graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()

config = {"configurable": {'thread_id': 41}}

st.write("The database holds legal information, including data on cases, involved parties, and associated documents. For example, you could ask: 'Find all cases filed in 2023 related to corporate law'.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask question about your data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Assistant is typing...")

        context_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        try:
            response = graph.invoke({"question": [HumanMessage(content=prompt)]}, config=config)
            sql_query = response['query']
            answer = response['answer']
            message = f"**SQL Query:**\n```sql\n{sql_query}\n```\n\n**Response:**\n{answer}"
            message_placeholder.markdown(message)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            message_placeholder.markdown(error_message)
            response = error_message

    st.session_state.messages.append({"role": "assistant", "content": message})