import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = os.getenv(
    "LLM_MODEL",
    "microsoft/Phi-3-mini-4k-instruct"
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
- Do not invent EC2 or other services
- Do not output markdown
- Do not output explanations outside the format

Answer:
"""

        messages = [
            {"role": "system", "content": "You are a precise cloud security expert. Follow the requested format exactly."},
            {"role": "user", "content": prompt}
        ]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            return_tensors="pt",
            add_generation_prompt=True
        )

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=120,
                do_sample=False,
                temperature=0,
                top_p=0.9,
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