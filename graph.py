from token import STAR
from tracemalloc import start
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from decider import deciderRouter
from coneAgent import node_agent_pinecone
from apiAgent import node_agent_api
from generalAgent import node_agent_general
from typing_extensions import TypedDict
from settings import *
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

class State(TypedDict):
    messages: Annotated[list, add_messages]

class FriendlyResponder:
    def __init__(self):
        # Initialize the StateGraph and other components
        self.state_graph = self.build_state_graph()

    def build_state_graph(self) -> StateGraph:
        graph_builder = StateGraph(State)
        graph_builder.add_node("coneAgentNode", node_agent_pinecone)
        graph_builder.add_node("apiAgentNode", node_agent_api)
        graph_builder.add_node("generalAgentNode", node_agent_general)
        graph_builder.add_conditional_edges(
            START,
            deciderRouter,
            {"Dataset": "coneAgentNode", "Api": "apiAgentNode", "General": "generalAgentNode"}
        )
        graph_builder.add_edge("coneAgentNode", END)
        graph_builder.add_edge("apiAgentNode", END)
        graph_builder.add_edge("generalAgentNode", END)
        return graph_builder.compile(checkpointer=memory)

    def respond(self, state: State) -> dict:
        question = state["messages"][-1].content
        response = settings.llm.invoke(question)
        return {"messages": [response]}

    def run(self,message):
        session_id = message["session_id"]
        message = message["question"]
        config = {"configurable": {"thread_id": session_id}}
        responses = []
        events = self.state_graph.stream(
            {"messages": [("user", message)]},
            config,
            stream_mode="values"
        )
        for event in events:
            response_message = event["messages"][-1].content
            responses.append(response_message)
        return responses[-1]
            

# Example usage
if __name__ == "__main__":
    responder = FriendlyResponder()
    responder.run()
