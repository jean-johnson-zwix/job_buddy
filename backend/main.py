from src.retriever.gmail_client import GmailClient
from src.agent.job_extractor import JobExtractor
from src.database.db_manager import DBManager
from dotenv import load_dotenv
load_dotenv()

def run():
    print("Job Buddy is starting...")
    
    # get the job emails
    gmail_client = GmailClient()
    emails = gmail_client.fetch_job_alerts()
    print(f"Retrieved {len(emails)} job emails")

    # llm extracts the relevant details
    extractor = JobExtractor()
    jobs = extractor.extract_details(emails)
    print(f"LLM extracted {len(jobs)} job opportunities.")

    # store jobs in databae (without duplicates)
    db = DBManager()
    new_count = 0
    skipped_count = 0
    
    for job in jobs:
        status = db.insert_job(job)
        if status == "INSERTED":
            new_count += 1
        elif status == "SKIPPED":
            skipped_count += 1
            
    print(f"Phase 1: Job Ingestion & Extraction completed: {new_count} new jobs added, {skipped_count} duplicates skipped.")
    
if __name__ == "__main__":
    run()