import json
import sys
import traceback
from engine import analyze_plan

from rag_retriever import RAGRetriever
from llm_generator import LLMGenerator


# Toggle debug logs (set to True locally if needed)
DEBUG = True


def log(message):
    if DEBUG:
        print(message)


# --------------------------------------
# AI ENRICHMENT
# --------------------------------------

def enrich_with_ai(violations):
    """
    Adds RAG retrieval + LLM explanation to each violation.
    Fails gracefully if AI components break.
    """

    try:
        retriever = RAGRetriever()
        generator = LLMGenerator()
    except Exception as e:
        print(f"⚠️ AI components failed to initialize: {e}")
        return violations

    enriched = []

    for v in violations:
        try:
            issue_text = v.get("issue") or v.get("message") or "security violation"

            query = (
                f"{issue_text} "
                f"{v.get('resource', '')} "
                f"{v.get('severity', '')} "
                f"CIS benchmark security risk remediation terraform"
            )

            log(f"Embedding query: {query}")

            rag_context = retriever.search(query)

            explanation = generator.generate_explanation(
                violation={
                    "resource": v.get("resource"),
                    "issue": issue_text,
                    "severity": v.get("severity")
                },
                rag_context=rag_context
            )

            if explanation:
                explanation = explanation.split("### END ANSWER")[0]
                explanation = explanation.strip()

            v["ai_explanation"] = explanation

        except Exception as e:
            print(f"⚠️ AI enrichment failed for {v.get('resource')}: {e}")
            v["ai_explanation"] = "AI explanation unavailable."

        enriched.append(v)

    return enriched


# --------------------------------------
# MARKDOWN REPORT GENERATION
# --------------------------------------

def generate_markdown_report(results):
    severity_emoji = {
        "high": "🔴 HIGH",
        "medium": "🟡 MEDIUM",
        "low": "🟢 LOW"
    }

    report = []
    report.append("# 🛡️ Terraform AI Security Report\n")

    report.append(f"**Total Violations:** {results['total_violations']}")
    report.append(f"- 🔴 High: {results['high']}")
    report.append(f"- 🟡 Medium: {results['medium']}")
    report.append(f"- 🟢 Low: {results['low']}\n")

    report.append("---\n")

    for v in results["violations"]:
        sev = v["severity"].lower()

        report.append(f"## 🔍 {v['resource']}")
        report.append(f"**Severity:** {severity_emoji.get(sev, sev.upper())}")
        report.append(f"**Issue:** {v.get('message')}\n")

        report.append(v.get("ai_explanation", "No AI explanation available."))
        report.append("\n---\n")

    return "\n".join(report)


# --------------------------------------
# MAIN
# --------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <plan.json>")
        sys.exit(1)

    plan_path = sys.argv[1]

    try:
        with open(plan_path, "r") as f:
            plan = json.load(f)
    except Exception as e:
        print(f"Failed to load plan file: {e}")
        sys.exit(1)

    print("🔍 Running deterministic rule engine...")
    violations = analyze_plan(plan)

    if violations:
        print("🤖 Enhancing violations with AI...")
        violations = enrich_with_ai(violations)
    else:
        print("✅ No violations found. Skipping AI enrichment.")

    # Normalize severity case
    for v in violations:
        v["severity"] = v["severity"].lower()

    high_count = sum(1 for v in violations if v["severity"] == "high")
    medium_count = sum(1 for v in violations if v["severity"] == "medium")
    low_count = sum(1 for v in violations if v["severity"] == "low")

    output = {
        "total_violations": len(violations),
        "high": high_count,
        "medium": medium_count,
        "low": low_count,
        "violations": violations
    }

    # Save JSON for automation
    with open("violations.json", "w") as f:
        json.dump(output, f, indent=2)

    # Save Markdown report for humans
    markdown_report = generate_markdown_report(output)

    with open("SECURITY_REPORT.md", "w") as f:
        f.write(markdown_report)

    # Clean console summary (CI-friendly)
    print("\n🛡️ SECURITY SUMMARY")
    print(f"Total: {output['total_violations']} | "
          f"High: {high_count} | "
          f"Medium: {medium_count} | "
          f"Low: {low_count}")

    print("\nDetailed report written to SECURITY_REPORT.md")


if __name__ == "__main__":
    main()