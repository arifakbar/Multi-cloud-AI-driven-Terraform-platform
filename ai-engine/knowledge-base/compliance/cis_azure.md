# CIS Microsoft Azure Foundations Benchmark – Overview

## Purpose

The CIS Azure Foundations Benchmark defines best practices 
for securing Azure subscriptions and resources.

---

## Key Control Areas

### 1. Identity and Access Management

- Enforce MFA for all privileged roles
- Use least privilege access
- Disable legacy authentication

Severity: HIGH

---

### 2. Logging and Monitoring

- Enable Azure Activity Log retention
- Send logs to Log Analytics workspace
- Enable diagnostic settings on critical resources

Severity: HIGH

---

### 3. Storage Controls

CIS Azure Storage Controls include:

3.1 Ensure secure transfer is required  
3.2 Ensure blob public access is disabled  
3.3 Ensure encryption is enabled  

Failure Impact:
- Data interception
- Public exposure
- Compliance violations

Severity: HIGH