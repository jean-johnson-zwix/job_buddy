import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

class DBManager:
    def __init__(self):
        self.conn_params = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT")
        }
        self._create_table_if_not_exists()

    def _get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def _create_table_if_not_exists(self):
        query = """
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            gmail_id VARCHAR(255) UNIQUE,
            title VARCHAR(255),
            company VARCHAR(255),
            location VARCHAR(255),
            link TEXT,
            status VARCHAR(50) DEFAULT 'New',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()

    def insert_job(self, job_data):
        query = """
        INSERT INTO jobs (gmail_id, title, company, location, link)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (gmail_id) DO NOTHING
        RETURNING id;
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (
                        job_data.get('gmail_id'),
                        job_data.get('title'),
                        job_data.get('company'),
                        job_data.get('location'),
                        job_data.get('link')
                    ))
                    result = cur.fetchone()
                    conn.commit()
                    
                    if result:
                        return "INSERTED"
                    else:
                        return "SKIPPED"
        except Exception as e:
            print(f"DBManager Error: {e}")
            return "ERROR"