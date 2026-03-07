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
        context_text = "\n\n".join([c["text"][:500] for c in rag_context[:2]])

        prompt = f"""
You are a cloud security expert reviewing Terraform infrastructure.

Analyze ONLY the violation below.

Resource: {violation['resource']}
Issue: {violation['message']}
Severity: {violation['severity']}

Security guidance:
{context_text}

Instructions:
- Explain ONLY this violation
- Do NOT copy documentation
- Do NOT create sections like "2. Public Access Block"
- Be concise

Respond using EXACTLY this format:

Security Risk:
Attack Scenario:
Terraform Remediation:
Compliance Reference:

Answer:
"""

        inputs = self.tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=300,
                do_sample=False,
                temperature=0.2,
                repetition_penalty=1.2,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id
            )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        response = decoded.replace(prompt, "").strip()

        if "### END ANSWER" in response:
            response = response.split("### END ANSWER")[0].strip()

        return response