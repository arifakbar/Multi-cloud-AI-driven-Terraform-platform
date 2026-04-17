import os 

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from embedder import chunk_documents

DB_NAME = 'vector_db'
EMBEDDER_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'

def create_vectorstore():
    try:
        chunks = chunk_documents()
        if len(chunks) > 0:
            embeddings = HuggingFaceEmbeddings(model_name=EMBEDDER_MODEL_NAME)
            if os.path.exists(DB_NAME):
                Chroma(persist_directory=DB_NAME, embedding_function=embeddings).delete_collection()
            vectore_store = Chroma.from_documents(chunks, embeddings, persist_directory=DB_NAME)
            print ("Vector Store Created")
        return vectore_store 
    except Exception as e:
        print("Error creating Vector Store:", e)
        return []
