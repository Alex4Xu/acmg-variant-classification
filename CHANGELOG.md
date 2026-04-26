# Changelog

## 2026-04-26 13:45 CST — v0.3.3 clinical-safety hardening

Backup before this round:
- /home/nvidia/.hermes/skills/healthcare/acmg-variant-classification.backup.20260426_134310

Main rationale:
- Keep default combination logic aligned with ACMG/AMP 2015 Table 5.
- Explicitly document that later ClinGen SVI / Tavtigian Bayesian point framework does not justify generic `3 Moderate + 3 Supporting -> Pathogenic` handling.
- Preserve literature deep-dive routing as a post-upstream-check escalation, not a reflex triggered by empty intake placeholders.
- Improve auditability for clinical review: source dates, VCEP/CSpec version, framework version, reclassification triggers.

Files changed:
- SKILL.md
  - Version bumped to 0.3.3.
  - Added authority hierarchy and combination-source guardrail.
  - Added Tavtigian point-framework note: Supporting=1, Moderate=2, Strong=4, Very Strong=8; `3M+3P=9`, below generic Pathogenic threshold.
  - Added validation instructions for classifier edge tests.
- templates/evidence-table.md
  - Added framework/source-version fields.
  - Added explicit PP1/BS4 LOD thresholds.
  - Added reminder to record VCEP/CSpec or local framework before overriding generic combination logic.
- templates/report_cn.md
  - Added case/reviewer/framework fields.
  - Added ClinGen/VCEP, gnomAD, ClinVar retrieval/version fields.
  - Added decision-support disclaimer.
- templates/intake.md
  - Added checked/not-yet states for ClinGen/VCEP, ClinVar, gnomAD, population sources, literature.
  - Added threshold provenance and source-version capture fields.
- references/sop.md
  - Added sign-off section.
  - Added change-control requirements.
- tests/test_classifier.py
  - Added classifier edge tests for 3M+3P, PVS1+1P, invalid counts, and reference cases.

Validation run:
- python3 scripts/classifier.py references/test_cases.json
  - 13 / 13 passed.
- python3 scripts/evidence_router.py templates/example-intake.json
  - JSON output valid.
- Direct test-module execution because pytest is unavailable in this environment:
  - tests/test_classifier.py: 4 / 4 passed.
  - tests/test_evidence_router.py: 7 / 7 passed.

Notes:
- This skill remains decision support only and does not replace expert clinical review, lab SOPs, or disease/gene-specific VCEP/CSpec guidance.
