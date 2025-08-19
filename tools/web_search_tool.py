import requests
from langchain.tools import Tool
from dotenv import load_dotenv
load_dotenv('.env')
import os

def web_search(query: str):
    res = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": "Bearer <os.getenv(TAVILY_API)>"},
        json={"query": query}
    )
    return res.json()["results"][0]["content"]

WebSearchTool = Tool.from_function(
    func=web_search,
    name="WebSearchTool",
    description="Search web to retrieve missing context")
