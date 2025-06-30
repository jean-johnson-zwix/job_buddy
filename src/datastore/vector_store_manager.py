import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.ingestion.github_client import GithubClient

class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_directory = "buddy_chroma_db/project_readmes"
        self.vector_db = None

    def load_readme_files(self, username):
        github_client = GithubClient()
        docs = github_client.load_all_readme(os.getenv("GITHUB_USERNAME"))
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)
        
        self.vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print("Vector Store updated with latest GitHub data!")

    def search_relevant_projects(self, job_description):
        """Finds project snippets most relevant to the JD."""
        if not self.vector_db:
            self.vector_db = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
        
        results = self.vector_db.similarity_search(job_description, k=3)
        return "\n\n".join([res.page_content for res in results])