from tools import WebSearchTool

def test_web_search():
    query = "What is the capital of France?"
    result = WebSearchTool(query)
    print("Search result:", result)

if __name__ == "__main__":
    test_web_search()