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
    # print(res.content)
    data = json.loads(res.content)
    final_op = []
    for resource in data["resources"]:
        enriched_risks = []

        for risk in resource["risks"]:
            prompt = f"""
Return ONLY raw Terraform code.

Rules:
- Do NOT use markdown
- Do NOT wrap in ```hcl
- Do NOT add explanations
- Do NOT repeat full Terraform resources
- Only output missing or required blocks to fix the issue.
- Output must be valid Terraform snippet only

Resource: {resource['resource_name']}
Type: {resource['resource_type']}
Risk: {risk['description']}

Generate ONLY Terraform code snippet to fix it.
No explanations.
            """
            fix = llm2.invoke([SystemMessage(content=prompt), HumanMessage(content=risk["description"])])
            enriched_risks.append(
                {
                    **risk,
                    "fix":fix.content.strip().split("\n")
                    }
            )
        final_op.append({
            "resource_name": resource["resource_name"],
            "resource_type": resource["resource_type"],
            "risks": enriched_risks
        }) 
    print(json.dumps(final_op, indent=2))
    return final_op
    
if __name__ == "__main__":
    main()