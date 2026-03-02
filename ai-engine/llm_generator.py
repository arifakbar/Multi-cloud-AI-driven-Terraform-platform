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
        context_text = "\n\n".join([c["text"] for c in rag_context])

        prompt = f"""
You are a Principal Cloud Security Engineer reviewing Terraform infrastructure.

Return your response STRICTLY in the following Markdown format:

## Security Risk
<clear explanation>

## Compliance Impact
<Mention CIS control if applicable>

## Remediation Steps
<step-by-step terraform fix>

Violation:
Resource: {violation["resource"]}
Issue: {violation["issue"]}
Severity: {violation["severity"]}

Security Context:
{context_text}

### START ANSWER
"""

        inputs = self.tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=300,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        if "### START ANSWER" in decoded:
            response = decoded.split("### START ANSWER")[-1].strip()
        else:
            response = decoded.replace(prompt, "").strip()

        response = response.replace(prompt, "").strip()

        return response