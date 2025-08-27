# agent/agent_runner.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama
from dotenv import load_dotenv

# Import tools
from tools import (
    WebSearchTool, 
    build_context_judge_tool, 
    build_context_relevance_tool,
    build_context_splitter_tool
)

# Load environment variables
load_dotenv()

def create_context_aware_agent():
    """Create and return a context-aware agent with all tools"""
    
    # Initialize the LLM
    llm = Ollama(model='llama3')
    
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
    prompt = PromptTemplate.from_template("""
    You are a context-aware conversational agent. Your goal is to provide helpful answers by intelligently using available tools.

    WORKFLOW:
    1. First, analyze if the user provided sufficient context using ContextJudgeTool
    2. If context is missing, search for relevant information using WebSearchTool
    3. If you found information, check its relevance using ContextRelevanceTool
    4. Use ContextSplitterTool to separate context from questions when needed
    5. Finally, provide a comprehensive answer based on available information

    You have access to the following tools:
    {tools}

    Use the following format:
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought: {agent_scratchpad}
    """)
    
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

if __name__ == "__main__":
    # Test the agent
    test_queries = [
        "What is LangChain used for?",
        "In the context of neural networks for computer vision, how do convolutional layers work?",
        "Tell me about attention mechanisms"
    ]
    
    agent_executor = create_context_aware_agent()
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        
        try:
            response = agent_executor.invoke({"input": query})
            print(f"Response: {response['output']}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n" + "-"*50)