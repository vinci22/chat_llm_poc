import settings 
from langchain_core.prompts import PromptTemplate
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
import prompts




llm = settings.llm
class State(TypedDict):

    messages: Annotated[list, add_messages]
    
def node_agent_general(state:State):
    preguntas = state["messages"]
    pregunta_actual= state["messages"][-1].content
    baseprompt = PromptTemplate.from_template(prompts.BASE_PROMPT_GENERAL_AGENT)
    prompt = baseprompt.format(pregunta=pregunta_actual,contexto=preguntas)
    response = llm.invoke(prompt)
    return {"messages": [response]}
