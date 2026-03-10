import os
from urllib import response
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
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float32,
            device_map="cpu"
        )

        self.model.eval()

    def generate_explanation(self, violation, rag_context):
        context_text = ""
        if rag_context:
            for ctx in rag_context[:2]:
                context_text += ctx.get("text", "")[:300] + "\n\n"

        issue_text = violation.get("message") or violation.get("issue") or "Unknown issue"
        resource = violation.get("resource", "unknown")
        severity = violation.get("severity", "low")

        provider = "AWS" if "aws_" in resource else "Azure" if "azurerm_" in resource else "Cloud"
        
        prompt = f"""
You are a cloud security expert analyzing Terraform infrastructure.

Analyze the violation and produce a structured explanation.

Violation:
Resource: {resource}
Issue: {issue_text}
Severity: {severity.upper()}

Relevant guidance:
{context_text}

Instructions:
1. Explain the risk clearly.
2. Provide valid Terraform HCL code to fix the issue.
3. CRITICAL: Use ONLY official Terraform Provider argument names (e.g., 'enable_https_traffic_only', NOT 'enable_http_workload_security').
4. Ensure code blocks are complete with closing braces.
5. Do not truncate code.

Output Format:
### Security Risk
<Explanation>

### Remediation
<Explanation>

### Terraform Code
```hcl
<Complete Code>

Compliance Reference:
(example: CIS AWS 3.2)
Begin:"""

        inputs = self.tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                do_sample=False,
                temperature=0,
                repetition_penalty=1.2,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id
            )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        if "### Security Risk" in decoded:
            response = decoded.split("### Security Risk")[1]
        else:
            response = decoded.split("Begin:")[-1].strip() if "Begin:" in decoded else decoded

        response = response.strip()

        if "```hcl" in response:
            if response.count("```") % 2 != 0:
                response += "\n```"

        if not response or len(response) < 10:
            return "AI explanation unavailable."

        return response