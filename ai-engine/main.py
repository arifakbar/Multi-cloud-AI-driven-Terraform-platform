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

    q = json.dumps(plan, indent=2)

    if not os.path.exists(DB_NAME):
        raise ValueError(f"Vector DB not found at {DB_NAME}")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDER_MODEL_NAME)
    vector_store = Chroma(persist_directory=DB_NAME, embedding_function=embeddings)

    retriever = vector_store.as_retriever(search_kwargs={"k": 8})
    llm = ChatGroq(api_key=GROQ_API_KEY, model_name=LLM_MODEL_NAME, reasoning_format='parsed')
    llm2 = ChatGroq(api_key=GROQ_API_KEY, model_name=LLM_MODEL_NAME, reasoning_format='parsed')

    system_prompt = """
You are a principal cloud security architect.

Analyze the Terraform plan and identify security risks.

Rules:
- Only analyze resources present in the context
- Do NOT include explanations
- Do NOT include markdown or backticks
- Output MUST be valid JSON only

IMPORTANT:
- Group all risks under the same resource_name
- Do NOT repeat resource entries

Return format:

{{
  "resources": [
    {{
      "resource_name": "",
      "resource_type": "",
      "risks": [
        {{
          "description": "",
          "severity": "low|medium|high",
          "recommendations": []
        }}
      ]
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
    res2 = llm2.invoke([
    SystemMessage(content="""
You are a Terraform expert.

You will receive a JSON object containing security risks.
Your task is to generate ONLY Terraform code snippets that fix the issues.

Rules:
- Do NOT repeat full Terraform resources
- Only output missing or required blocks
- No explanations
- No markdown
"""),
    HumanMessage(content=res.content)
])
    print(res2.content)
    return res2.content
    
if __name__ == "__main__":
    main()