import argparse
import settings
from pinecone import Pinecone, ServerlessSpec
import time
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from tqdm import tqdm  # Importamos tqdm para las barras de progreso

model_embeding = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def create_index(indexName):
    if indexName is None:
        index_name = "langchain-test-index"
    else:
        index_name = indexName

    existing_indexes = [index_info["name"] for index_info in settings.pc.list_indexes()]

    if index_name not in existing_indexes:
        settings.pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        # Mostrar progreso mientras el índice se está creando
        print(f"Creando índice '{index_name}', espera un momento...")
        with tqdm(total=100, desc="Creando índice") as pbar:
            while not settings.pc.describe_index(index_name).status["ready"]:
                time.sleep(1)
                pbar.update(5)  # Puedes ajustar el valor según el tiempo estimado
        print(f"Índice '{index_name}' creado con éxito.")

    index = settings.pc.Index(index_name)
    return index


def preprocess_text(text):
    # Reemplazar espacios, saltos de línea y tabulaciones consecutivas
    text = re.sub(r'\s+', ' ', text)
    return text

def process_pdf(file_path):
    # Crear un loader para el archivo PDF
    loader = PyPDFLoader(file_path)
    # Cargar los datos
    data = loader.load()

    # Dividir los datos en documentos más pequeños con Chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(data)

    # Convertir objetos Document en cadenas de texto
    texts = [str(doc) for doc in documents]

    return texts


def create_embeddings(texts):
    embeddings_list = []
    print("Generando embeddings...")

    # Usar tqdm para mostrar el progreso de la generación de embeddings
    for text in tqdm(texts, desc="Progreso de embeddings"):
        embeddings = model_embeding.encode(text)
        embeddings_list.append(embeddings)
    
    print("Embeddings generados exitosamente.")
    return embeddings_list

def upsert_embeddings_to_pinecone(index, embeddings, ids):
    print("Subiendo embeddings a Pinecone...")

    # Convertir los IDs a cadenas de texto
    for i in tqdm(range(len(embeddings)), desc="Subiendo embeddings"):
        index.upsert(vectors=[(str(ids[i]), embeddings[i])])
    
    print("Embeddings subidos a Pinecone correctamente.")
    

def main(args):
    path = args.file
    indexname = args.indexName

    index = create_index(indexname)

    # Mostrar barra de progreso mientras se procesa el PDF
    print("Procesando el archivo PDF...")
    texts = process_pdf(path)
    print(f"PDF procesado. Se encontraron {len(texts)} chunks de texto.")

    # Generar embeddings y subir a Pinecone
    embeddings = create_embeddings(texts)
    upsert_embeddings_to_pinecone(index, embeddings, range(len(embeddings)))  # Usar índices de los embeddings como IDs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        argument_default=argparse.SUPPRESS, description="cli-llm")
    parser.add_argument('-f', '--file', type=str, required=True,
                        help="Debe ser la ruta de tu documento externo (pdf, txt..)")
    parser.add_argument('-n', '--indexName', nargs='?', default=None, const=None, type=str, required=False)

    args = parser.parse_args()
    main(args)
