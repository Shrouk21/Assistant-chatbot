# agent/agent_runner.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv

# Import tools
from tools import (
    WebSearchTool, 
    build_context_judge_tool, 
    build_context_relevance_tool,
    build_context_splitter_tool
)

# Load environment variables
load_dotenv('.env')

def create_context_aware_agent():
    """Create and return a context-aware agent with all tools"""
    
    # Initialize the LLM
    llm = OllamaLLM(model=os.getenv('MODEL_NAME'))
    
    # Build tools that require LLM
    context_judge_tool = build_context_judge_tool(llm)
    context_relevance_tool = build_context_relevance_tool(llm)
    context_splitter_tool = build_context_splitter_tool(llm)
    
    # Collect all tools
    tools = [
        context_judge_tool,
        WebSearchTool,
        context_relevance_tool,
        context_splitter_tool
    ]
    
    # Create React agent prompt
    with open("prompts/agent_runner_prompt.txt", "r") as f:
            prompt_text = f.read()
    prompt = PromptTemplate.from_template(prompt_text)
    
    # Create the React agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True
    )
    
    return agent_executor

def run_agent_with_query(query: str):
    """Run the agent with a specific query"""
    agent_executor = create_context_aware_agent()
    try:
        response = agent_executor.invoke({"input": query})
        return response["output"]
    except Exception as e:
        return f"Agent error: {str(e)}"

