
from agent import create_context_aware_agent
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