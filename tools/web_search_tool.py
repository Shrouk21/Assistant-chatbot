import requests
from langchain.tools import Tool
from dotenv import load_dotenv
import os

load_dotenv('.env')

def web_search(query: str):
    """Search web to retrieve missing context"""
    try:
        res = requests.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {os.getenv('TAVILY_API_KEY')}"},  # Fixed: proper f-string
            json={"query": query, "max_results": 3}  # Added max_results for better control
        )
        
        if res.status_code == 200:
            results = res.json().get("results", [])
            if results:
                # Return the first result's content, or combine multiple results
                return results[0]["content"]
            else:
                return "No search results found."
        else:
            return f"Search failed with status code: {res.status_code}"
    except Exception as e:
        return f"Search error: {str(e)}"

WebSearchTool = Tool.from_function(
    func=web_search,
    name="WebSearchTool",
    description="Search web to retrieve missing context when user input lacks sufficient background information"
)
