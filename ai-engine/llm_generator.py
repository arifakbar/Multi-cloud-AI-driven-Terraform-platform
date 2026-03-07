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
        context_text = rag_context[0]["text"][:250] if rag_context else ""
        issue_text = violation.get("message") or violation.get("issue") or "Unknown issue"

        prompt = f"""
You are a cloud security expert.

Analyze the Terraform security violation below.

Resource: {violation['resource']}
Issue: {issue_text}
Severity: {violation['severity']}

Security guidance:
{context_text}

Respond using ONLY the following format.

Security Risk:
(one short paragraph)

Attack Scenario:
(one short paragraph)

Terraform Remediation:
(provide Terraform code only)

Compliance Reference:
(example: CIS AWS 3.2)

Do not include markdown blocks, titles, or extra commentary.
"""

        inputs = self.tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=120,
                do_sample=False,
                repetition_penalty=1.2,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id
            )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        response = decoded[len(prompt):].strip()
        response = response.replace("```markdown", "")
        response = response.replace("```", "")

        if "### END ANSWER" in response:
            response = response.split("### END ANSWER")[0].strip()
        
        if not response or len(response) < 10:
            return "AI explanation unavailable."

        return response