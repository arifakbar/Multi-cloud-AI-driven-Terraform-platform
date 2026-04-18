import os
import glob

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(BASE_DIR, "knowledge-base")


def load_documents():
    try:
        folders = glob.glob(os.path.join(KB_PATH, "*"))

        if not folders:
            print(f"No folders found in knowledge base: {KB_PATH}")
            return []

        docs = []

        for folder in folders:
            doc_type = os.path.basename(folder)

            loader = DirectoryLoader(
                folder,
                glob="**/*.md",
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"},
            )

            folder_docs = loader.load()

            if not folder_docs:
                print(f"No markdown files found in {folder}")
                continue

            for d in folder_docs:
                d.metadata["type"] = doc_type

            docs.extend(folder_docs)

        print(f"Total documents loaded: {len(docs)}")
        return docs

    except Exception as e:
        print(f"Error loading KB documents: {e}")
        return []


def chunk_documents():
    try:
        docs = load_documents()

        if not docs:
            print("No documents to split.")
            return []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = text_splitter.split_documents(docs)

        print(f"Split into chunks: {len(chunks)}")
        return chunks

    except Exception as e:
        print("Error chunking documents:", e)
        return []