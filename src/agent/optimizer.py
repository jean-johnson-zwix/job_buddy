from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import SystemMessage, HumanMessage
from src.datastore.vector_store_manager import VectorStoreManager
from tavily import TavilyClient
import os

class OptimizerBuddy:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0.3, # Low temperature for professional accuracy
        )
        self.vector_store = VectorStoreManager()
        self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    def search_for_job_link(self, title, company):
        query = f"{company} {title} job description apply page"
        search_result = self.tavily.search(query=query, search_depth="advanced", max_results=5)
        for result in search_result['results']:
            url = result['url']
            if "/job/" in url or "myworkdayjobs.com" in url or "/posting/" in url:
                return url
            return search_result['results'][0]['url'] if search_result['results'] else None
        return None

    def get_job_description(self, job):
        print("getting the job description...")
        job_link = job.get('link')
        if not job_link:
            print("Buddy don't have the link from the email. Let's search for it!")
            job_link = self.search_for_job_link(job['title'], job['company'])
            print(f'Tavily has found a link: {job_link}')
        if job_link:
            print(f"Let's get the job description from {job_link}")
            return self.tavily.extract(urls=[job_link])['results'][0]['raw_content']
        else:
            print(f"Sorry, Buddy was not able to get the details.")
            return None

    def optimize_resume(self, base_resume, job):
        # Retrieve relevant project details
        job_description = self.get_job_description(job)
        if job_description is None:
            return None
        relevant_projects = self.vector_store.search_relevant_projects(job_description)
        print(f'RELEVANT PROJECTS: \n{relevant_projects}\n')
        # Augment the prompt
        system_prompt = f"""
        You are an expert technical recruiter and career coach.
        INSTRUCTIONS:
            1. Extract all required skills, preferred skills, and important keywords from the job description
            2. Identify which of my experiences and skills are most relevant
            3. Create a professional summary (2-3 sentences) that:
            - Includes 5-7 key keywords from the job description
            - Highlights my most relevant skills and quantifiable achievements
            - Matches the tone and level of the position
            4. Ensure ATS compatibility by:
            - Using standard section headings (Work Experience, Education, Skills)
            - Avoiding tables, columns, graphics, or special formatting
            - Keeping each keyword mentioned 2-4 times throughout the resume
            - Using simple, clean formatting
            6. Provide a keyword frequency analysis showing which important keywords from the job appear in my resume and how many times
            7. List any critical missing keywords or skills I should add if I have them
            RETURN FORMAT:
            - Optimized professional summary
            - Rewritten bullet points for each role
            - Skills section with categorized technical and soft skills
            - Keyword frequency analysis
            - Gap analysis (what's missing)
            - Overall ATS compatibility score and tips
            Use the following PROJECT DETAILS to add specific, quantifiable achievements 
            to the work experience or projects section:
            {relevant_projects}
        """
        user_prompt = f"""
        I need help optimizing my resume for this job posting. 
        Please analyze the job description and help me tailor my resume to maximize ATS compatibility and recruiter appeal.
        JOB DESCRIPTION
        {job_description}
        MY CURRENT RESUME
        {base_resume}
        """
        # Generate the response
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        return self.llm.invoke(messages).content