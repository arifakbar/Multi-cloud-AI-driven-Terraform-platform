import json

from vector_store import create_vectorstore

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

GROQ_API_KEY='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'
LLM_MODEL_NAME = 'qwen/qwen3-32b'


def main():
    try:
        with open('plan.json', 'r') as f:
            plan = json.load(f)
    except Exception as e:
        print(f"Error loading plan.json: {e}")
        return []
    
    q = json.dumps(plan, indent=2)

    retriever = create_vectorstore().as_retriever()
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