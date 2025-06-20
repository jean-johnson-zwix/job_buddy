import google.generativeai as genai
import json
import os

class JobExtractor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.MAX_CHARS_PER_EMAIL = 3000  # Trim HTML
        self.MAX_TOTAL_CHARS = 100000    # Token Limit

    def extract_details(self, emails):
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
        Extract job details from these emails. Return ONLY a JSON array.
        If an email has multiple jobs, extract each one.
        Format: [{{"title": "...", "company": "...", "location": "...", "link": "...", "gmail_id": "..."}}]

        DATA:
        {full_context}
        """

        try:
            response = self.model.generate_content(prompt)
            # Handle potential markdown wrappers in response
            text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(text)
        except Exception as e:
            print(f"Job Extractor Error: {e}")
            return []