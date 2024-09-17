from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
import settings
import prompts
from langchain_core.prompts import PromptTemplate


llm = settings.llm


class State(TypedDict):

    messages: Annotated[list, add_messages]


def decider(state):

    prompt = PromptTemplate.from_template(prompts.BASE_PROMTP_INTENT)

    message = prompt.format(pregunta=state["messages"][-1].content)
    return {"messages": [llm.invoke(message)]}


def deciderRouter(state: State):
    
    intention = decider(state)
    
    
    if "Api" == intention["messages"][-1].content:
        return "Api"
    elif "Dataset" == intention["messages"][-1].content:
        return "Dataset"
    elif "General" == intention["messages"][-1].content:
        return "General"
