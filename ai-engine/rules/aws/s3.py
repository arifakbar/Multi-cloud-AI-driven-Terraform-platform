from base import build_violation, ensure_list

def check(resource):
    if resource.get("type") != "aws_s3_bucket":
        return None

    after = resource.get("change", {}).get("after", {})
    violations = []
    
    public_access_block = after.get("public_access_block", {})
    if isinstance(public_access_block, dict):
        if not public_access_block.get("block_public_acls", False):
            violations.append(
                build_violation("high", "S3 bucket does not block public ACLs", "AWS-S3-001")
            )
        if not public_access_block.get("block_public_policy", False):
            violations.append(
                build_violation("high", "S3 bucket does not block public policies", "AWS-S3-002")
            )

    encryption = after.get("server_side_encryption_configuration", {})
    if not encryption:
        violations.append(
            build_violation("high", "S3 bucket does not have default encryption enabled", "AWS-S3-003")
        )

    versioning = after.get("versioning", {})
    if isinstance(versioning, dict) and not versioning.get("enabled", False):
        violations.append(
            build_violation("medium", "S3 bucket versioning is not enabled", "AWS-S3-004")
        )

    return ensure_list(violations)