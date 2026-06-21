import psycopg2
import os
from dotenv import load_dotenv
import logging

load_dotenv()  # loads .env file
logger = logging.getLogger(__name__)


def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", 5432),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise

def run_query(query:str, params=None) -> list:
    if not query.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")
    with get_connection() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                logger.info("Query returned %d rows.", len(results))
                return results
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise