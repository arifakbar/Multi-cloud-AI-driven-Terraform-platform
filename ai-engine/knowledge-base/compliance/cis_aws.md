# CIS AWS Foundations Benchmark – Overview

## Purpose

The CIS AWS Foundations Benchmark provides prescriptive guidance 
for establishing a secure baseline configuration for AWS environments.

---

## Key Control Areas

### 1. Identity and Access Management

- Avoid use of root account
- Enable MFA for privileged users
- Rotate access keys regularly

Severity: HIGH

---

### 2. Logging and Monitoring

- Enable CloudTrail in all regions
- Enable log file validation
- Send logs to secure S3 bucket

Severity: HIGH

---

### 3. Storage Controls

CIS AWS 3.x Controls apply to S3 security.

Important Controls:

3.1 Ensure S3 buckets have default encryption enabled  
3.2 Ensure S3 bucket public access block is enabled  
3.3 Ensure S3 bucket logging is enabled  

Failure Impact:
- Data exposure
- Regulatory fines
- Incident response complexity

Severity: HIGH