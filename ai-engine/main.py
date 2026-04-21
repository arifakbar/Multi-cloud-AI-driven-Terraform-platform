import json
import os
import sys

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

LLM_MODEL_NAME = 'qwen/qwen3-32b'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "vector_db")
EMBEDDER_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def main():
    
    if not GROQ_API_KEY:
      raise ValueError("GROQ_API_KEY not set")
    
    try:
        plan_path = sys.argv[1]
        with open(plan_path, 'r') as f:
            plan = json.load(f)
    except Exception as e:
        print(f"Error loading plan.json: {e}")
        return []
    
    resource_types = [
        r.get("type") for r in plan.get("resource_changes", [])
    ]
    q = " ".join(filter(None, resource_types))

    # q = json.dumps(plan, indent=2)

    if not os.path.exists(DB_NAME):
        raise ValueError(f"Vector DB not found at {DB_NAME}")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDER_MODEL_NAME)
    vector_store = Chroma(persist_directory=DB_NAME, embedding_function=embeddings)

    retriever = vector_store.as_retriever(search_kwargs={"k": 8})
    llm = ChatGroq(api_key=GROQ_API_KEY, model_name=LLM_MODEL_NAME, reasoning_format='parsed')
    llm2 = ChatGroq(api_key=GROQ_API_KEY, model_name=LLM_MODEL_NAME, reasoning_format='parsed')

    system_prompt = """
You are a principal cloud security architect.
Analyze the Terraform plan summary below. And provide a risk assessment and recommendations for each risk.
Do not provide any explanation for resources which are not present in the context. Only analyze the resources present in the context.
You MUST respond ONLY in valid JSON.
Do NOT include explanations.
Do NOT include markdown.
Do NOT include backticks.
Return raw JSON only.
Required format:

Format:

{{
  "resources": [
    {{
      "resource_name": "",
      "resource_type": "",
      "risk": "",
      "severity": "low|medium|high",
      "recommendations": []
    }}
  ]
}}

Plan:
{context}
"""

    docs = retriever.invoke(q)
    context = "\n\n".join(d.page_content for d in docs)
    prompt = system_prompt.format(context=context)
    res = llm.invoke([SystemMessage(content=prompt),HumanMessage(content=q)])
    print(res.content)
    res2 = llm2.invoke([SystemMessage(content=res.content),HumanMessage(content="Please provide the terraform code for the recommendations. Not the whole code, just the code snippets for the recommendations.")])
    print(res2.content)
    return res2.content
    
if __name__ == "__main__":
    main()