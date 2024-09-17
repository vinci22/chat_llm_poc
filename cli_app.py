import os
import time
import argparse
from tqdm import tqdm
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import ServerlessSpec
import settings
from langchain_pinecone import PineconeVectorStore
from uuid import uuid4
from langchain_community.document_loaders import PDFPlumberLoader

def main(file_path):
    # Check if file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file at {file_path} does not exist.")

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    # Load and process PDF with progress indication
    print("Loading and processing PDF...")
    pages = PDFPlumberLoader(file_path).load()
    
    pc = settings.pc
    index_name = "langchain-test-index"  # change if desired

    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    index = pc.Index(index_name)
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)

    # Add documents with progress bar
    uuids = [str(uuid4()) for _ in range(len(pages))]
    print("Adding documents to Pinecone...")
    for page, uuid in tqdm(zip(pages, uuids), total=len(pages), desc="Uploading pages"):
        vector_store.add_documents(documents=[page], ids=[uuid])

if __name__ == "__main__":
#     # Setup argument parsing
    parser = argparse.ArgumentParser(description='Process a PDF file and upload its contents to Pinecone.')
    parser.add_argument('-f','--file_path', type=str, help='Path to the PDF file.')
    args = parser.parse_args()
    
    main(args.file_path)