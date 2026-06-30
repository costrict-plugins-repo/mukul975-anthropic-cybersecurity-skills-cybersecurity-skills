# Standards and Framework Mapping — Triaging Windows with KAPE

## NIST Cybersecurity Framework 2.0

| ID | Name | Rationale |
|----|------|-----------|
| RS.AN-03 | Analysis is performed to establish what has taken place during an incident and the root cause of the incident | KAPE rapidly collects and parses host artifacts (execution, persistence, account, file-system) that establish the sequence of attacker activity and root cause during incident response. |

## MITRE ATT&CK

| ID | Name | Rationale |
|----|------|-----------|
| T1005 | Data from Local System | KAPE acquires forensic data directly from the local file system; this same data source is what adversaries target with T1005 and what responders must preserve and analyze. |

## Supporting References

- KAPE Documentation (Eric Zimmerman / Kroll): https://ericzimmerman.github.io/KapeDocs/
- KapeFiles Targets/Modules: https://github.com/EricZimmerman/KapeFiles
- SANS DFIR — KAPE: https://www.sans.org/tools/kape/
- NIST SP 800-86 Guide to Integrating Forensic Techniques into Incident Response
- NIST SP 800-61r2 Computer Security Incident Handling Guide
