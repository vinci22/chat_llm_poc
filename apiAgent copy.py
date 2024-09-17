from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from typing import List
from bs4 import BeautifulSoup
import requests
import re
from uuid import uuid4
from langchain_core.documents import Document
import time
import settings  # Asegúrate de que este módulo esté correctamente importado
from pinecone import Pinecone, ServerlessSpec
import prompts


llm = settings.llm 
class ExchangeRateProcessor:
    def __init__(self, index_name="vector-api-exchange", url='https://www.exchangerate-api.com/docs/supported-currencies'):
        self.index_name = index_name
        self.url = url
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self.llm = settings.llm
        self.index = self._create_or_get_index(index_name)
        
        if self.index:
            # El índice fue creado o ya existía, por lo que configuramos el vector_store
            self.vector_store = PineconeVectorStore(index=self.index, embedding=self.embeddings)
            print(f"Índice '{index_name}' cargado exitosamente.")
            
            # No procesar y agregar documentos si el índice ya existe
            if not self._index_is_empty():
                print(f"El índice '{index_name}' ya tiene documentos. No se agregarán más documentos.")
            else:
                documents_loaded = self.process_and_store()
                if documents_loaded:
                    print("Documentos procesados y almacenados correctamente.")
                else:
                    print("No se encontraron documentos para almacenar.")

    def _create_or_get_index(self, index_name: str):
        # Verifica si el índice ya existe o crea uno nuevo
        try:
            existing_indexes = [index_info["name"] for index_info in settings.pc.list_indexes()]
            if index_name in existing_indexes:
                print(f"El índice '{index_name}' ya existe. Cargando el índice.")
                return settings.pc.Index(index_name)
            else:
                print(f"Creando el índice '{index_name}'...")
                settings.pc.create_index(
                    name=index_name,
                    dimension=384,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
                while not settings.pc.describe_index(index_name).status["ready"]:
                    time.sleep(1)
                return settings.pc.Index(index_name)
        except Exception as e:
            print(f"Error al crear o cargar el índice: {e}")
            return None

    def _index_is_empty(self) -> bool:
        # Método para verificar si el índice tiene documentos
        try:
            index_stats = self.index.describe_index_stats()
            return index_stats['total_vector_count'] == 0
        except Exception as e:
            print(f"Error al verificar el índice: {e}")
            return False

    def fetch_data(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def extract_table(self, table):
        rows = table.find_all('tr')
        table_text = ""
        for row in rows:
            cols = row.find_all('td')
            table_text += " | ".join([col.get_text(strip=True) for col in cols]) + "\n"
        return table_text

    def extract_table_details(self, soup):
        tables = soup.find_all('table')
        result_text = ""
        
        for table in tables:
            title_element = table.find_previous_sibling('u')
            table_title = title_element.get_text(strip=True) if title_element else "Sin título"
            
            description_element = table.find_previous_sibling('p')
            table_description = description_element.get_text(strip=True) if description_element else "Sin descripción"
            
            table_text = self.extract_table(table)
            
            result_text += f"Título de la tabla: {table_title}\nDescripción: {table_description}\n{table_text}\n"
        
        return result_text

    def know_exchange_currenci(self, description: str) -> str:
        try:
            prompt = PromptTemplate.from_template(prompts.BASE_PROMPT_CLASSIFIER_DESCRIPTION)
            message = prompt.format(Description=description)
            return self.llm.invoke(message).content
        except Exception as e:
            print(f"Error al obtener la categoría de fuente: {e}")
            return "Desconocido"

    def parse_text(self, text: str) -> List[Document]:
        blocks = text.strip().split('\n\n')
        parsed_data = []

        for block in blocks:
            title_match = re.search(r'Título de la tabla: (.*?)\n', block)
            description_match = re.search(r'Descripción: (.*?)\n', block)
            table_content_match = re.search(r'(Currency Code.*\n(?:.*\n)+)', block)

            title = title_match.group(1) if title_match else "No Título"
            description = description_match.group(1) if description_match else "No Descripción"
            table_content = table_content_match.group(1) if table_content_match else "No Contenido de la Tabla"
            
            source_category = self.know_exchange_currenci(description)

            parsed_data.append(
                Document(
                    page_content=table_content.strip(),
                    metadata={"source": source_category}
                )
            )

        return parsed_data

    def process_and_store(self) -> bool:
        soup = self.fetch_data()
        extracted_text = self.extract_table_details(soup)
        parsed_documents = self.parse_text(extracted_text)
        if parsed_documents:
            self.vector_store.add_documents(documents=parsed_documents)
            print("Datos procesados y almacenados en el índice.")
            return True
        else:
            print("No se encontraron documentos para almacenar.")
            return False



#Multidocs Agents

def rewiter_qa(original_qa):
    prompt = PromptTemplate.from_template(prompts.BASE_PROMPT_REWITER_QA)

    message = prompt.format(pregunta=original_qa)
    print(message)
    return llm.invoke(message).content
    

def manager_Agents_Multidocs(qa):
    

    prompt = PromptTemplate.from_template(prompts.BASE_PROMPT_MANAGER_AGENT_MULTI_DOCS)

    message = prompt.format(pregunta=qa)
    print(llm.invoke(message).content)



    