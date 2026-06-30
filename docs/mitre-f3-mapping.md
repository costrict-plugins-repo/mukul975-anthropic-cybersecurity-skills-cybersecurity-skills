# MITRE Fight Fraud Framework (F3) — Mapping Schema

This repository maps fraud-relevant skills to the **MITRE Fight Fraud Framework (F3)**,
released April 9, 2026 by MITRE's Center for Threat-Informed Defense (CTID). F3 is an
ATT&CK-compatible TTP catalog for cyber-enabled financial fraud.

- Upstream project: <https://ctid.mitre.org/fraud/>
- Source repo: <https://github.com/center-for-threat-informed-defense/fight-fraud-framework>
- License: Apache-2.0
- Mapped version in this repo: **F3 v1.1**

## Why F3 in addition to ATT&CK

ATT&CK collapses post-compromise fraud into the single `T1657` (Financial Theft)
technique. F3 decomposes the "how a cyber intrusion becomes a financial loss" stages
into two dedicated tactics that ATT&CK does not have:

- **Positioning** (`FA0001`) — after access, collect/manipulate data and prepare the fraud.
- **Monetization** (`FA0002`) — convert stolen assets into usable funds.

So `mitre_attack` answers "how did the adversary get in / operate technically" and
`mitre_f3` answers "how did that turn into money." They are kept as **separate
frontmatter blocks** because F3 redefines several ATT&CK tactics for the fraud context.

## The 8 F3 v1.1 tactics

| Tactic slug | F3 ID | Origin |
|---|---|---|
| `reconnaissance` | TA0043 | ATT&CK (redefined) |
| `resource-development` | TA0042 | ATT&CK (redefined) |
| `initial-access` | TA0001 | ATT&CK (redefined) |
| `stealth` | TA0005 | ATT&CK (redefined) |
| `positioning` | **FA0001** | **F3-new** |
| `execution` | TA0002 | ATT&CK (redefined) |
| `monetization` | **FA0002** | **F3-new** |
| `defense-impairment` | TA0112 | ATT&CK (redefined) |

## Technique ID conventions

- **`F1XXX`** — fraud-specific techniques introduced by F3 (e.g. `F1005.003`
  Account Manipulation: Add Beneficiary, `F1025.003` Electronic Funds Transfer:
  Wire Transfer, `F1018` Convert to Cryptocurrency).
- **`T1XXX`** — ATT&CK techniques reused verbatim inside F3 (e.g. `T1566` Phishing,
  `T1586` Compromise Accounts, `T1557` Adversary-in-the-Middle).
- Sub-techniques use ATT&CK dot notation (`F1005.003`, `T1566.002`).

Every ID used in this repo is a real, active technique present in the F3 v1.1 STIX
bundle — there are no `TBD`/placeholder IDs.

## Frontmatter schema

The `mitre_f3` block sits alongside the existing `mitre_attack` block:

```yaml
mitre_f3:
  version: '1.1'
  tactics:
    - positioning
    - monetization
  techniques:
    - id: F1005.003
      name: 'Account Manipulation: Add Beneficiary'
      tactic: positioning
      source: f3          # F-prefixed = fraud-specific
    - id: T1586
      name: Compromise Accounts
      tactic: resource-development
      source: attack      # T-prefixed = reused ATT&CK
```

Rules:
1. `id` must be a real F3 v1.1 technique ID.
2. `name` must match the technique's official name in the F3 catalog.
3. `tactic` must be one the technique actually lists in the catalog.
4. `source` is `f3` for `F1XXX` IDs and `attack` for `T1XXX` IDs.

## Scope

F3 mappings are applied only to **fraud-relevant skills** — phishing/social
engineering, account takeover, banking malware/stealers, BEC, identity/KYC,
payment/card fraud, money-mule/cash-out, ransomware extortion, and the cross-cutting
DFIR and threat-intelligence skills. Skills with no fraud dimension do not carry an
`mitre_f3` block.

## Regenerating / verifying the catalog

```bash
git clone --depth 1 https://github.com/center-for-threat-informed-defense/fight-fraud-framework
# technique catalog is the STIX bundle:
#   fight-fraud-framework/public/f3-stix-v1.1.json
```

All `mitre_f3` IDs in this repo are validated against that bundle on every update.
