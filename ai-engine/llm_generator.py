import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = os.getenv(
    "LLM_MODEL",
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
)


class LLMGenerator:
    def __init__(self):
        print(f"Loading model: {MODEL_NAME}")

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float32,
            device_map="cpu"
        )

        self.model.eval()

    def generate_explanation(self, violation, rag_context):
        context_text = rag_context[0]["text"][:100] if rag_context else ""
        issue_text = violation.get("message") or violation.get("issue") or "Unknown issue"

        prompt = f"""
You are a cloud security expert analyzing Terraform infrastructure.

Analyze the violation and produce a structured explanation.

Violation:
Resource: {violation['resource']}
Issue: {issue_text}
Severity: {violation['severity']}

Relevant guidance:
{context_text}

Return EXACTLY the following sections.

Security Risk:
(1 sentence describing the risk)

Attack Scenario:
(1 sentence realistic attack)

Terraform Remediation:
(valid Terraform code fixing the issue)

Compliance Reference:
(example: CIS AWS 3.2)

Rules:
- Only discuss the resource above
- Do not invent other services
- Do not output markdown
- Do not output explanations outside the format

Answer:
"""

        inputs = self.tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=120,
                do_sample=False,
                temperature=0,
                repetition_penalty=1.2,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id
            )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        response = decoded.split("Answer:")[-1].strip()
        response = response.replace("```", "").replace("json", "").strip()

        if not response or len(response) < 10:
            return "AI explanation unavailable."

        return response