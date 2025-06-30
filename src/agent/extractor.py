import google.generativeai as genai
import json
import os

class JobScout:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.MAX_CHARS_PER_EMAIL = 3000  # Trim HTML
        self.MAX_TOTAL_CHARS = 100000    # Token Limit

    def extract_jobs(self, emails, resume_text):
        processed_contents = []
        for e in emails:
            # retrieve email content
            raw_content = e.get('content') or e.get('snippet', 'No content')
            # remove footers/signatures
            trimmed_content = raw_content[:self.MAX_CHARS_PER_EMAIL]
            processed_contents.append(f"ID: {e.get('id')}\nCONTENT: {trimmed_content}")
        
        # ensure token limit not exceeded
        full_context = "\n\n---\n\n".join(processed_contents)
        if len(full_context) > self.MAX_TOTAL_CHARS:
            print(f"Context window exceeded by ({len(full_context)} chars). Truncating total payload.")
            full_context = full_context[:self.MAX_TOTAL_CHARS]

        prompt = f"""
        You are an Expert Career Coach. I will provide my resume and several job alert emails.

        Task 1:
        - Extract job details from these emails. Return ONLY a JSON array.
        - If an email has multiple jobs, extract each one.

        DATA:
        {full_context}

        Task 2:
        - Rate each job (1-10) based on my resume
        - Provide a brief reason for the score.

        RESUME:
        {resume_text}

        OUTPUT FORMAT (Strict JSON array):
        [
          {{
            "gmail_id": "...",
            "title": "...",
            "company": "...",
            "location": "...",
            "link": "...",
            "score": 9,
            "match_reason": "Matches your experience with AWS cloud-native designs at Cognizant."
          }}
        ]
        """

        try:
            print(f'Asking Gemini...')
            response = self.model.generate_content(prompt)
            # Handle potential markdown wrappers in response
            text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(text)
        except Exception as e:
            print(f"Job Extractor Error: {e}")
            return []