import os 
from pinecone import Pinecone, ServerlessSpec

# Obtener las credenciales de las variables de entorno
PINECONE_APIKEY = os.environ.get("PINECONE_APIKEY")
EXCHANGERATE_APIKEY = os.environ.get("EXCHANGERATE_APIKEY")
LLM_APIKEY = os.environ.get("LLM_APIKEY")



# Inicializar Pinecone con la API key
pc = Pinecone(api_key=PINECONE_APIKEY)
