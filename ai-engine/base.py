# ai-engine/base.py

def build_violation(severity: str, issue: str, rule_id: str = None):
    return {
        "severity": severity,
        "issue": issue,
        "rule_id": rule_id
    }


def ensure_list(result):
    """
    Ensures rule returns list or None
    """
    if not result:
        return None

    if isinstance(result, list):
        return result

    return [result]