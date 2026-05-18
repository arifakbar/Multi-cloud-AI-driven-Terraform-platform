import json

def publish_report(data):
    high_count = 0
    medium_count = 0
    low_count = 0

    # First pass: count severities
    for resource in data.get("resources", []):
        for risk in resource.get("risks", []):

            severity = risk.get("severity", "unknown").lower()

            if severity == "high":
                high_count += 1

            elif severity == "medium":
                medium_count += 1

            elif severity == "low":
                low_count += 1

    approval_required = high_count > 0

    result = {
        "high_severity_count": high_count,
        "medium_severity_count": medium_count,
        "low_severity_count": low_count,
        "approval_required": approval_required
    }

    # Start markdown report
    report = []

    report.append("# Terraform Security Analysis Report\n")

    # Summary Section
    report.append("## Security Summary\n")

    report.append(f"- High Severity Issues: **{high_count}**")
    report.append(f"- Medium Severity Issues: **{medium_count}**")
    report.append(f"- Low Severity Issues: **{low_count}**")
    report.append(f"- Approval Required: **{approval_required}**")

    report.append("\n---\n")

    # Detailed Findings
    for resource in data.get("resources", []):

        report.append(f"## Resource: {resource['resource_name']}")
        report.append(f"**Type:** {resource['resource_type']}\n")

        for risk in resource.get("risks", []):

            severity = risk.get("severity", "unknown").lower()

            report.append(f"### {risk['risk_id']}")
            report.append(f"- Severity: **{severity.upper()}**")
            report.append(f"- Description: {risk['description']}\n")

            report.append("#### Recommendations")

            for r in risk.get("recommendations", []):
                report.append(f"- {r}")

            report.append("\n#### Fix")

            for f in risk.get("fix", []):
                report.append(f"```hcl\n{f}\n```")

            report.append("\n---\n")

    # Write markdown file
    with open("SECURITY_REPORT.md", "w", encoding="utf-8") as file:
        file.write("\n".join(report))

    print("\n=== SECURITY SUMMARY ===")
    print(json.dumps(result, indent=2))

    return result