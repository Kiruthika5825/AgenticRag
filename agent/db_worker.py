from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import logging
import os
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

def get_db_agent():
    password = quote_plus(os.getenv('DB_PASSWORD'))
    db = SQLDatabase.from_uri(
        f"postgresql://{os.getenv('DB_USER')}:{password}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
        include_tables=["orders"],
        sample_rows_in_table_info=2
    )
    llm = ChatNVIDIA(
        model="meta/llama-3.1-8b-instruct",
        api_key=os.getenv("NVIDIA_API_KEY"),
        temperature=0.0
    )
    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True
    )
    return agent

def run_db_worker(query: str) -> dict:
    try:
        agent = get_db_agent()
        result = agent.invoke({"input": query})
        logger.info("DB agent answered successfully")
        return {
            "answer": result["output"],
            "source": "database"
        }
    except Exception as e:
        logger.error("DB worker failed: %s", e)
        raise