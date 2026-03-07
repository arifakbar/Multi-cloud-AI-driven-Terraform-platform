import os
import importlib.util


# ----------------------------
# Detect Cloud Provider
# ----------------------------
def detect_provider(resource_type: str):
    if resource_type.startswith("aws_"):
        return "aws"
    elif resource_type.startswith("azurerm_"):
        return "azure"
    return None


# ----------------------------
# Load All Rule Modules
# ----------------------------
def load_rules(provider: str):
    rules = []
    base_path = os.path.dirname(__file__)
    rules_path = os.path.join(base_path, "rules", provider)

    if not os.path.exists(rules_path):
        return rules

    for filename in os.listdir(rules_path):
        if filename.endswith(".py") and not filename.startswith("__"):
            file_path = os.path.join(rules_path, filename)
            module_name = filename[:-3]

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "check"):
                rules.append(module.check)

    return rules


# ----------------------------
# Analyze Terraform Plan
# ----------------------------
def analyze_plan(plan: dict):
    violations = []
    resource_changes = plan.get("resource_changes", [])

    for resource in resource_changes:
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        provider = detect_provider(resource_type)
        if not provider:
            continue

        rules = load_rules(provider)

        for rule in rules:
            result = rule(resource)

            if result:
                if isinstance(result, list):
                    for r in result:
                        violations.append(format_violation(resource_type, resource_name, r))
                else:
                    violations.append(format_violation(resource_type, resource_name, result))

    return violations


# ----------------------------
# Standardize Violation Format
# ----------------------------
def format_violation(resource_type, resource_name, rule_output):
    return {
        "resource": f"{resource_type}.{resource_name}",
        "severity": rule_output.get("severity", "low"),
        "message": rule_output.get("issue", "Violation detected")
    }