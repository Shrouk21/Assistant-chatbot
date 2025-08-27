from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate

def build_context_relevance_tool(llm):
    """Build context relevance checker tool"""
    prompt_text = """
    You are given a user question and some retrieved context. Determine if the context is relevant to answering the question.
    
    User Question: {question}
    Retrieved Context: {context}
    
    Analyze if the context contains information that would help answer the user's question.
    
    Respond with either:
    - "RELEVANT" if the context is helpful for answering the question
    - "NOT_RELEVANT" if the context doesn't help answer the question
    - "PARTIALLY_RELEVANT" if some parts of the context are useful
    
    Be strict in your evaluation - only mark as RELEVANT if the context genuinely helps answer the specific question.
    """
    
    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["question", "context"]
    )
    
    def check_relevance(input_text: str) -> str:
        """
        Expected input format: "QUESTION: <question> CONTEXT: <context>"
        """
        try:
            parts = input_text.split("CONTEXT:", 1)
            if len(parts) != 2:
                return "Error: Please provide input in format 'QUESTION: <question> CONTEXT: <context>'"
            
            question_part = parts[0].replace("QUESTION:", "").strip()
            context_part = parts[1].strip()
            
            formatted_prompt = prompt.format(question=question_part, context=context_part)
            response = llm.invoke(formatted_prompt)
            return response.strip() if hasattr(response, 'strip') else str(response).strip()
        except Exception as e:
            return f"Error processing input: {str(e)}"
    
    return Tool.from_function(
        func=check_relevance,
        name="ContextRelevanceTool",
        description="Checks if retrieved context is relevant to the user's question. Input format: 'QUESTION: <question> CONTEXT: <context>'"
    )