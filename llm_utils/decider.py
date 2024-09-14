from typing import Annotated

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from langchain_mistralai.chat_models import ChatMistralAI
import settings
import prompts
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import PromptTemplate


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


llm = ChatMistralAI(api_key=settings.LLM_APIKEY)


def decider(state: State):

    prompt = PromptTemplate.from_template(prompts.BASE_PROMTP_INTENT)

    message = prompt.format(pregunta=state["messages"][-1].content)
    message
    return {"messages": [llm.invoke(message)]}

def decider(state: State):

    prompt = PromptTemplate.from_template(prompts.BASE_PROMTP_INTENT)

    message = prompt.format(pregunta=state["messages"][-1].content)
    message
    return {"messages": [llm.invoke(message)]}
graph_builder.add_node("deciderNode", decider)
graph_builder.add_edge(START, "deciderNode")
graph_builder.add_edge("deciderNode", END)

graph = graph_builder.compile()


while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    for event in graph.stream({"messages": ("user", user_input)}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
