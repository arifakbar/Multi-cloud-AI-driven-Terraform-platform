# Azure Storage Account Security Best Practices

## 1. Secure Transfer Required
### Risk
If HTTPS is not enforced, data can be intercepted in transit.

### CIS Benchmark Reference
CIS Microsoft Azure 3.1: "Ensure secure transfer to storage accounts is enabled."

### Required Arguments
To enforce HTTPS, set the following argument in `azurerm_storage_account`:
- `enable_https_traffic_only = true`

Severity: HIGH

## 2. Blob Public Access
### Risk
Containers configured for anonymous public read access can leak data.

### Required Arguments
To disable public blob access, set:
- `allow_blob_public_access = false`

Severity: HIGH

## 3. TLS Version
### Risk
Older TLS versions are vulnerable to attacks.

### Required Arguments
To enforce secure TLS, set:
- `min_tls_version = "TLS1_2"`

Severity: MEDIUM