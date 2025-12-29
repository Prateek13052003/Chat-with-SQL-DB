from dotenv import load_dotenv
import os
load_dotenv()

import streamlit as st
from pathlib import Path
import sqlite3

from sqlalchemy import create_engine
from langchain.sql_database import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.callbacks import StreamlitCallbackHandler
from langchain_groq import ChatGroq


# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="LangChain Chat with SQL",
    page_icon="👽",
    layout="wide"
)

st.title("👽 LangChain Chat with SQL Database")


# -------------------- CONSTANTS --------------------
LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"


# -------------------- SIDEBAR --------------------
st.sidebar.header("Database Configuration")

radio_opt = [
    "Use SQLITE 3 Database - student.db",
    "Connect to MySQL Database"
]
selected_opt = st.sidebar.radio("Choose database", radio_opt)

# Initialize variables (IMPORTANT)
mysql_host = mysql_user = mysql_password = mysql_db = None

if selected_opt == radio_opt[1]:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("MySQL Host", placeholder="localhost")
    mysql_user = st.sidebar.text_input("MySQL User", placeholder="root")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database", placeholder="student")
else:
    db_uri = LOCALDB


# -------------------- GROQ API KEY --------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ GROQ_API_KEY not found. Add it to .env file.")
    st.stop()


# -------------------- LLM --------------------
llm = ChatGroq(
    groq_api_key=api_key,
    model_name="meta-llama/llama-4-maverick-17b-128e-instruct",
    streaming=True
)


# -------------------- DATABASE CONFIG --------------------
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == LOCALDB:
        db_path = (Path(__file__).parent / "student.db").absolute()
        creator = lambda: sqlite3.connect(
            f"file:{db_path}?mode=ro",
            uri=True,
            check_same_thread=False
        )
        return SQLDatabase(create_engine("sqlite://", creator=creator))

    elif db_uri == MYSQL:
        if not all([mysql_host, mysql_user, mysql_password, mysql_db]):
            return None

        # 🚨 HARD VALIDATION (prevents your error forever)
        if "@" in mysql_host or ":" in mysql_host:
            st.error("❌ MySQL Host must be ONLY 'localhost' or IP address.")
            st.stop()

        engine = create_engine(
            f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"
        )
        return SQLDatabase(engine)


# -------------------- INIT DB --------------------
db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)

if db is None:
    st.warning("⚠️ Please provide all MySQL connection details.")
    st.stop()


# -------------------- AGENT --------------------
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)


# -------------------- CHAT STATE --------------------
if "messages" not in st.session_state or st.sidebar.button("🧹 Clear Chat"):
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi! Ask me anything about your database 👋"}
    ]


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# -------------------- USER INPUT --------------------
user_query = st.chat_input("Ask a question about the database")

if user_query:
    st.session_state.messages.append(
        {"role": "user", "content": user_query}
    )
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[callback])
        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )
        st.write(response)
