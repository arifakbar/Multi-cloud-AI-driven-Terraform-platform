import os
import glob

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

def load_documents():
    try:
        folders = glob.glob("./knowledge-base/*")
        docs = []
        for folder in folders:
           doc_type = os.path.basename(folder)
           loader = DirectoryLoader(folder, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
           folder_docs = loader.load()
           for d in folder_docs:
               d.metadata['type'] = doc_type
           docs.extend(folder_docs)
        return docs
    except Exception as e:
        print(f"Error loading kb documents: {e}")
        return []

def chunk_documents():
    try:
        docs = load_documents()
        if docs:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(docs)
            print(f'Split into chuck: {len(chunks)}')
            return chunks
        else: return []
    except Exception as e:
        print("Error chinking Documents: ", e)
        return 0
