# JOB BUDDY

## Phase 1: Data Ingestion and Extraction

In the Phase 1, this job 'buddy' assists me:
- retrieve all the pilled up job alerts emails in my inbox
- extracts all the important info I need from these emails
- store it in my database for ranking and tracking.

### Architecture

![alt text](media/phase1_architecture.png)

### Technical Stack

- Language: Python 3.11+
- AI Model: Google Gemini 1.5 Flash
- Database: PostgreSQL
- APIs: Google Gmail API v1
- Libraries: ```google-api-python-client, psycopg2-binary, python-dotenv```

#### Additional features

- HTML Sanitization: regex-based custom clearning to reduce the email payload size by 80%
- Deduplication: uses gmail_id to handle duplicate alerts
- Context Safety: managed LLM context windows by added character limits
- Batch Processing: Retrieves 10-30 batches of emails, resulting in extraction of dozens of job opportunities in seconds