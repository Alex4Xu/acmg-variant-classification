# Hermes Agent: ACMG Variant Classification Skill

Hermes Agent skill for structured ACMG/AMP germline small-variant classification.

Implements the 2015 ACMG/AMP guidelines with ClinGen SVI refinements (2020-2024):
- Point-based de novo scoring (PS2/PM6 — SVI v1.1)
- Disease-specific BA1/BS1 thresholds (SVI 2018)
- Calibrated computational evidence (PP3/BP4 — Pejaver 2022/2024)
- PVS1 decision tree (Abou Tayoun 2018)
- Splicing variant framework (SVI Splicing SG 2023-2024)
- PS3/BS3 functional evidence validation requirements (SVI 2024)
- Bayesian co-segregation scoring (PP1/BS4)
- PM3 strength scaling for in trans evidence
- Code modification convention (e.g., `PM2_Supporting`)

## Contents

| Path | Description |
|------|-------------|
| `SKILL.md` | Full skill definition with step-by-step workflow |
| `scripts/classifier.py` | ACMG combination logic engine |
| `scripts/evidence_router.py` | Source-priority router with candidate evidence ledger |
| `templates/intake.md` | Structured case intake form |
| `templates/evidence-table.md` | Criterion recording sheet with applied strength |
| `templates/external-evidence-checklist.md` | Fixed source-order worksheet |
| `templates/report_cn.md` | Chinese clinical report skeleton |
| `references/sop.md` | Detailed standard operating procedure |
| `tests/test_evidence_router.py` | Router unit tests |

## Quick Validation

```bash
python3 scripts/classifier.py references/test_cases.json
python3 scripts/evidence_router.py templates/example-intake.json
```

## Important

This is a **decision-support workflow** only. It does not replace expert clinical review, laboratory SOPs, or disease-specific expert specifications.

## License

MIT
