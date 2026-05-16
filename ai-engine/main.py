import json
import os
import sys

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from prompts import rag_system_prompt, llm_system_prompt

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

LLM_MODEL_NAME = 'qwen/qwen3-32b'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "vector_db")
EMBEDDER_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def combined_output(res, res2):
  fix_data = json.loads(res2.content)
  risk_data = json.loads(res.content)

  fix_lookup = {
      f["risk_id"]: f["fix"]
      for f in fix_data["fixes"]
  }

  for resource in risk_data.get("resources", []):
      for risk in resource.get("risks", []):
          fix = fix_lookup.get(risk["risk_id"], "")
          if fix:
              clean_fix = bytes(fix, "utf-8").decode("unicode_escape")
              risk["fix"] = clean_fix.strip().split("\n")
          else:
              risk["fix"] = []

  print(json.dumps(risk_data, indent=2))

  return risk_data

def main():
    
    if not GROQ_API_KEY:
      raise ValueError("GROQ_API_KEY not set")
    
    try:
        plan_path = sys.argv[1]
        with open(plan_path, 'r') as f:
            plan = json.load(f)
    except Exception as e:
        print(f"Error loading plan.json: {e}")
        sys.exit(1)

    q = json.dumps(plan, indent=2)

    if not os.path.exists(DB_NAME):
        raise ValueError(f"Vector DB not found at {DB_NAME}")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDER_MODEL_NAME)
    vector_store = Chroma(persist_directory=DB_NAME, embedding_function=embeddings)

    retriever = vector_store.as_retriever(search_kwargs={"k": 8})
    llm = ChatGroq(api_key=GROQ_API_KEY, model_name=LLM_MODEL_NAME, reasoning_format='parsed')

    docs = retriever.invoke(q)
    context = "\n\n".join(d.page_content for d in docs)
    prompt = rag_system_prompt.format(context=context)
    
    res = llm.invoke([SystemMessage(content=prompt),HumanMessage(content=q)])

    res2 = llm.invoke([
    SystemMessage(content=llm_system_prompt),
    HumanMessage(content=res.content)
])
    
    return combined_output(res, res2)
    
if __name__ == "__main__":
    main()