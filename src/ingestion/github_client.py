import os
from github import Github
from langchain.schema import Document

class GithubClient:
    def __init__(self):
        self.gh = Github(os.getenv("GITHUB_TOKEN"))

    def load_readme(self, username):
        documents = []
        user = self.gh.get_user(username)
        
        for repo in user.get_repos():
            try:
                # get README
                readme = repo.get_readme()
                content = readme.decoded_content.decode('utf-8')
                
                # Metadata: repo name + URL
                doc = Document(
                    page_content=content,
                    metadata={
                        "repo_name": repo.name,
                        "url": repo.html_url,
                        "description": repo.description
                    }
                )
                documents.append(doc)
                print(f"Loaded README from: {repo.name}")
            except:
                continue
                
        return documents