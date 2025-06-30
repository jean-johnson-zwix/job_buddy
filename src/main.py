from src.ingestion.gmail_client import GmailClient
from src.ingestion.github_client import GithubClient
from src.ingestion.gdrive_client import DriveResumeLoader
from src.agent.extractor import JobScout
from src.datastore.database_manager import DBManager
from src.datastore.vector_store_manager import VectorStoreManager
import os
from dotenv import load_dotenv
load_dotenv()
import time

def run():
    print("Job Buddy is starting...")
    
    # get the resume from drive
    resume_text = DriveResumeLoader().get_resume_text()
    
    # get the job emails
    gmail_client = GmailClient()
    emails = gmail_client.fetch_job_alerts()
    email_link_map = {e['id']: e['link'] for e in emails}
    print(f"Retrieved {len(emails)} job emails")

    # llm extracts the relevant details
    extractor = JobScout()
    jobs = extractor.extract_jobs(emails, resume_text)
    print(f"LLM extracted {len(jobs)} job opportunities.")

    # store jobs in database
    db = DBManager()
    new_count = 0
    for job in jobs:
        job['gmail_url'] = email_link_map.get(job['gmail_id'])
        if db.insert_job(job):
            new_count += 1
        gmail_client.label_and_archive(job['gmail_id'], job['score'])
            
    print(f"Phase 2: Intelligent Scoring: {new_count} new jobs added")

def test():
    vector_store = VectorStoreManager()
    vector_store.load_readme_files(os.getenv("GITHUB_USERNAME"))

if __name__ == "__main__":
    start_time = time.perf_counter()
    test()
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.4f} seconds")