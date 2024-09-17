from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
import settings 
from langchain_pinecone import PineconeVectorStore
from prompts import BASE_WINDOW_PROMPT_RETRIEVAL
from langchain_core.prompts import PromptTemplate
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):

    messages: Annotated[list, add_messages]

class PineConeAgent():
    
    def __init__(self):
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        index = settings.pc.Index("langchain-test-index")
        vector_store = PineconeVectorStore(index=index, embedding=embeddings)
        self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 3, "score_threshold": 0.4},
        )
        self.llm = settings.llm
        
        self.tempalte = PromptTemplate.from_template(BASE_WINDOW_PROMPT_RETRIEVAL)
        
    def retriever_context(self,qa):
        
        retrieval = (self.retriever.invoke(qa))
        all_page_content = " ".join([page.page_content for page in retrieval])

        return all_page_content
    
    
    def invoke(self, query):
        
        context = self.retriever_context(query)
        prompt_message = self.tempalte.format(contexto=context, pregunta=query)
        response = self.llm.invoke(prompt_message)
        return response
        
agent_pinecone = PineConeAgent()
def node_agent_pinecone(state:State):
    qa = state["messages"][-1].content
    response = agent_pinecone.invoke(qa)
    return {"messages": [response]}
    
    
# print(agent_pinecone.invoke("como puedo pagar los cursos con que medio ").content)