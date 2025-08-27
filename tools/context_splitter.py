from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate

def build_context_splitter_tool(llm):
    """Build context splitter tool to separate context from question"""
    prompt_text = """
    Analyze the user input and separate the background context from the actual question being asked.
    
    User Input: {input}
    
    Extract and clearly separate:
    1. The background context/information provided
    2. The specific question being asked
    
    Format your response as:
    CONTEXT: <extracted context or "No explicit context provided">
    QUESTION: <the main question being asked>
    
    If the input contains both context and a question, separate them clearly.
    If it's only a question without context, state that no context was provided.
    """
    
    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["input"]
    )
    
    def split_context(input_text: str) -> str:
        """Split context from question in user input"""
        try:
            formatted_prompt = prompt.format(input=input_text)
            response = llm.invoke(formatted_prompt)
            return response.strip() if hasattr(response, 'strip') else str(response).strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    return Tool.from_function(
        func=split_context,
        name="ContextSplitterTool",
        description="Separates background context from the actual question in user input"
    )