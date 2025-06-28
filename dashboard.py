import streamlit as st
from src.database.db_manager import DBManager
from src.ingestion.gmail_client import GmailClient
from src.ingestion.gdrive_client import DriveResumeLoader
from src.agent.job_engine import JobEngine
from src.database.db_manager import DBManager
from dotenv import load_dotenv
load_dotenv()
import time

def run_job_buddy():
    ("Job Buddy is starting...")
    
    # get the resume from drive
    resume_text = DriveResumeLoader().get_resume_text()
    
    # get the job emails
    gmail_client = GmailClient()
    emails = gmail_client.fetch_job_alerts()
    email_link_map = {e['id']: e['link'] for e in emails}
    st.write(f"Retrieved {len(emails)} job emails")

    # llm extracts the relevant details
    extractor = JobEngine()
    jobs = extractor.extract_jobs(emails, resume_text)
    st.write(f"LLM extracted {len(jobs)} job opportunities.")

    # store jobs in database
    db = DBManager()
    new_count = 0
    for job in jobs:
        job['gmail_url'] = email_link_map.get(job['gmail_id'])
        if db.insert_job(job):
            new_count += 1
        # label and archive emails
        gmail_client.label_and_archive(job['gmail_id'], job['score'])

st.set_page_config(page_title="Job Buddy", layout="wide")
st.sidebar.header("Control Panel")
if st.sidebar.button("Load more Jobs", use_container_width=True):
    with st.status("Buddy is working...", expanded=True) as status:
        st.write("Fetching latest resume from Google Drive...")
        try:
            run_job_buddy() 
            status.update(label="Loading Complete!", state="complete", expanded=False)
            st.toast("New jobs processed and scored!", icon="🎉")
        except Exception as e:
            status.update(label="Sync Failed", state="error")
            st.error(f"Error: {e}")


st.title("Job Buddy Dashboard")
st.markdown("---")
db = DBManager()
jobs = db.get_all_scored_jobs()
if not jobs:
    st.info("No jobs found in database")
else:
    # Stats row
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Opportunities", len(jobs))
    col2.metric("High Match (8+)", len([j for j in jobs if j['score'] >= 8]))
    col3.metric("Latest Sync", "Just now" if "status" in locals() else "Earlier today")

    # Filter
    min_score = st.sidebar.slider("Filter by Min Score", 1, 10, 6)
    for job in jobs:
        if job['score'] >= min_score:
            # The expander header shows the most important info first
            with st.expander(f"⭐ **{job['score']}/10** | {job['title']} at {job['company']}"):
                
                # Metadata row
                st.write(f"**Location:** {job['location']}")
                st.info(f"**Why it fits:** {job['match_reason']}")
                job_id = job.get('gmail_id')
                # Action Buttons Row
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    # This opens the specific Gmail message we found
                    # display logic inside your loop
                    gmail_url = job.get('gmail_url')

                    if gmail_url:
                        st.link_button("See in Gmail", gmail_url, use_container_width=True)
                    else:
                        # This handles the case where the URL is None/Null
                        st.button("See in Gmail", disabled=True, use_container_width=True, key=f"missing_{job_id}")
                
                with btn_col2:
                    # This opens the direct application link extracted by Gemini
                    if job['link'] and job['link'].startswith("http"):
                        st.link_button("Apply Now", job['link'], use_container_width=True, type="primary")
                    else:
                        st.button("Apply Now", disabled=True, use_container_width=True, key=f"no_link_{job_id}")