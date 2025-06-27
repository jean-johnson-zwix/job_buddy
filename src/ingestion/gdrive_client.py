import io
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
import PyPDF2

class DriveResumeLoader:
    def __init__(self):
        creds = Credentials.from_authorized_user_file('token.json')
        self.service = build('drive', 'v3', credentials=creds)
        self.file_id = os.getenv("RESUME_FILE_ID")

    def get_resume_text(self):
        try:
            # download the resume
            request = self.service.files().get_media(fileId=self.file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            # extract text from pdf
            fh.seek(0)
            reader = PyPDF2.PdfReader(fh)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            return text
        except Exception as e:
            print(f"Google Drive Client Error: {e}")
            return None