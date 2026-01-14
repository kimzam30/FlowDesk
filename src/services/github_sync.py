from github import Github
import os
from dotenv import load_dotenv

# Load keys from .env file
load_dotenv()

def fetch_my_issues():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN not found in .env")
        return []

    try:
        g = Github(token)
        # "None" means get issues for the authenticated user
        issues = g.get_user().get_issues(state='open', filter='assigned')
        
        task_list = []
        for issue in issues:
            task_list.append({
                "title": issue.title,
                "repo": issue.repository.name,
                "url": issue.html_url,
                "id": issue.id
            })
        return task_list
    except Exception as e:
        print(f"GitHub Error: {e}")
        return []