import os
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import re


class GmailClient:
    def __init__(self):
        creds = Credentials.from_authorized_user_file('token.json')
        self.service = build('gmail', 'v1', credentials=creds)


    @staticmethod
    def clean_html(raw_html):
        if not raw_html:
            return ""
        # Remove scripts, styles, and HTML tags using RE
        clean = re.sub(r'<(script|style).*?>.*?</\1>', '', raw_html, flags=re.DOTALL)
        clean = re.sub(r'<.*?>', ' ', clean)
        # Collapses spaces & newlines
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean
        
    def fetch_job_alerts(self, max_results=10):
        query = "job alert"
        results = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        full_emails = []
        for msg in messages:
            # retreive email body content
            m = self.service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            # extract text body
            body = ""
            if 'parts' in m['payload']:
                for part in m['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                data = m['payload']['body'].get('data', '')
                body = base64.urlsafe_b64decode(data).decode('utf-8')
            full_emails.append({
                "id": m['id'],
                "content": body if body else m['snippet']
            })
        return full_emails