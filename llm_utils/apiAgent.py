import settings 
from langchain_core.prompts import PromptTemplate
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from bs4 import BeautifulSoup
import requests
import prompts
import re
import requests
llm = settings.llm
class State(TypedDict):

    messages: Annotated[list, add_messages]

# URL de la página de documentación de la API
url = 'https://www.exchangerate-api.com/docs/supported-currencies'

# Realizar la solicitud HTTP
response = requests.get(url)

# Analizar el contenido HTML con BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Función para extraer el texto de una tabla
def extract_table(table):
    rows = table.find_all('tr')
    table_text = ""
    for row in rows:
        cols = row.find_all('td')
        table_text += " | ".join([col.get_text(strip=True) for col in cols]) + "\n"
    return table_text

# Función para extraer el título, descripción y contenido de las tablas
def extract_table_details(soup):
    tables = soup.find_all('table')
    result_text = ""
    
    for table in tables:
        # Encuentra el título de la tabla en una etiqueta <u> justo antes de la tabla
        title_element = table.find_previous_sibling('u')
        table_title = title_element.get_text(strip=True) if title_element else "Sin título"
        
        # Encuentra la descripción de la tabla en una etiqueta <p> justo antes del título
        description_element = table.find_previous_sibling('p')
        table_description = description_element.get_text(strip=True) if description_element else "Sin descripción"
        
        # Extraer el texto de la tabla
        table_text = extract_table(table)
        
        # Añadir el título, descripción y el contenido de la tabla al resultado
        result_text += f"Título de la tabla: {table_title}\nDescripción: {table_description}\n{table_text}\n"
    
    return result_text



def know_exchange_currenci(qa):
    # pregunta = pregunta=state["messages"][-1].content
    pregunta = qa
    prompt = PromptTemplate.from_template(prompts.BASE_PROMTP_EXCHANGE_KNOW)
    tables_details_text = extract_table_details(soup)
    message = prompt.format(contexto=tables_details_text,pregunta=pregunta)
    return llm.invoke(message)
    

def query_to_api(qa):
    codes_currency = know_exchange_currenci(qa)
    
    print(f"url response{codes_currency}")
     
    prompt = PromptTemplate.from_template(prompts.BASE_PROMPT_QA_TO_API)
    message = prompt.format(code=codes_currency,api_key=settings.EXCHANGERATE_APIKEY)
    url_converted = llm.invoke(message).content
    print(F"response agent:{url_converted}")
    pattern = r'https?://[^\s>]+'
    matches = re.findall(pattern,url_converted)
    print(f"url encontrada en el prompt: {matches}")
    return matches[0]
    

def node_agent_api(state:State):
    pregunta=state["messages"][-1].content
    
    url = query_to_api(pregunta)
    print(f"buscando en esta api: {url}")
    try:
        # Realizar la solicitud GET a la API
        requests_data = requests.get(f'{url}')
        
        # Verificar si la solicitud fue exitosa
        requests_data.raise_for_status()
        
        # Obtener los datos en formato JSON
        data = requests_data.json()
        
        # Extraer el valor de 'conversion_result'
        conversion_result = data.get('conversion_result') or data.get('conversion_rate')
        print(conversion_result)
        prompt = PromptTemplate.from_template(prompts.BASE_PROMTP_FRIENDLY_RESPONSE)
        question = prompt.format(pregunta=pregunta,respuesta=conversion_result)
        # response = llm.invoke()
        return {"messages": [llm.invoke(question).content]}

    except requests.RequestException as e:
        return {"messages": ["upss! tengo problemas con la Api!"]}

# print(node_agent_api("¿Cuánto está el peso colombiano respecto al dólar?"))