# db_handler/connect.py

import os
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),         # <-- Added port
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")  # <-- Corrected variable name
        )
        print("Database connection successful.")
        return conn
    except OperationalError as e:
        print(f"Could not connect to the database: {e}")
        return None