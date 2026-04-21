import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from embedder import chunk_documents

DB_NAME = "vector_db"
EMBEDDER_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def create_vectorstore():
    try:
        chunks = chunk_documents()

        if not chunks:
            print("No documents found. Skipping vector store creation.")
            return None

        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDER_MODEL_NAME)

        vectore_store = Chroma.from_documents(
            chunks,
            embeddings,
            persist_directory=DB_NAME
        )

        print("Vector Store Created Successfully")
        return vectore_store

    except Exception as e:
        print("Error creating Vector Store:", e)
        return None


if __name__ == "__main__":
    create_vectorstore()