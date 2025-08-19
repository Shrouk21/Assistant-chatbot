import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from langchain.agents import initialize_agent, AgentType
# from tools.context_presence_judge import ContextJudgeTool
# from tools.web_search_tool import WebSearchTool
import tools
from langchain_community.llms import Ollama

llm = Ollama(model='llama3')

agent = initialize_agent(
    tools=[ContextJudgeTool, WebSearchTool],
    llm=llm,
    agent=AgentType.REACT_DESCRIPTION,
    verbose=True
)

response = agent.run("What is LangChain used for?")
print(response)