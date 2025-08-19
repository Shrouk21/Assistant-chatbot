from langchain.tools import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def build_context_judge_tool(llm):
    prompt = PromptTemplate(open("prompts/context_judge_prompt.txt").read(), ["input"])
    chain = LLMChain(llm=llm, prompt=prompt)
    return Tool.from_function(
        func=chain.run,
        name="ContextJudgeTool",
        description="Checks if the context is present in the user input"

    )