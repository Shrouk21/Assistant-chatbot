from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate

def build_context_judge_tool(llm):
    """Build context presence judge tool with the provided LLM"""
    try:
        with open("prompts/context_judge_prompt.txt", "r") as f:
            prompt_text = f.read()
    except FileNotFoundError:
        # Fallback prompt if file doesn't exist
        prompt_text = """
        Analyze the user's input and determine if it contains sufficient context to provide a good answer.
        
        User input: {input}
        
        Respond with either:
        - "SUFFICIENT_CONTEXT" if the input contains enough background information or context
        - "MISSING_CONTEXT" if the input lacks necessary context and would benefit from additional information
        
        Consider whether the question is specific enough and contains domain context, background details, or clear scope.
        """
    
    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["input"]
    )
    
    def judge_context(input_text: str) -> str:
        """Judge if input contains sufficient context"""
        try:
            formatted_prompt = prompt.format(input=input_text)
            response = llm.invoke(formatted_prompt)
            return response.strip() if hasattr(response, 'strip') else str(response).strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    return Tool.from_function(
        func=judge_context,
        name="ContextJudgeTool",
        description="Determines whether the user input contains sufficient context to provide a comprehensive answer"
    )