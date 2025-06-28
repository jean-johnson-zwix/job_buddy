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
        
    def fetch_job_alerts(self, max_results=2):
        query = 'label:INBOX "job alert" -label:JobBuddy/High-Match -label:JobBuddy/Processed'
        results = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        full_emails = []
        for msg in messages:
            # retreive email body content
            m = self.service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            message_id = m['id']
            gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{message_id}"
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
                "content": body if body else m['snippet'],
                "link": gmail_link
            })
        return full_emails

    def label_and_archive(self, message_id, score):
        label_name = "JobBuddy/High-Match" if score >= 7 else "JobBuddy/Processed"
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            label_id = next((l['id'] for l in labels if l['name'] == label_name), None)
            if not label_id:
                label_body = {
                    'name': label_name,
                    'labelListVisibility': 'labelShow',
                    'messageListVisibility': 'show'
                }
                label_id = self.service.users().labels().create(userId='me', body=label_body).execute()['id']
            self.service.users().messages().batchModify(
                userId='me',
                body={
                    'ids': [message_id],
                    'addLabelIds': [label_id],
                    'removeLabelIds': ['INBOX']
                }
            ).execute()
            print(f"Archived and labeled {message_id} as {label_name}")
        except Exception as e:
            print(f"Labeling error: {e}")