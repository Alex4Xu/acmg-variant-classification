# Changelog

## 2026-04-26 13:45 CST — v0.3.3 clinical-safety hardening

Backup before this round:
- Local backup created before edit

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


## 2026-04-26 13:58 CST — v0.3.4 reviewer-feedback scientific refinements

Backup before this round:
- Local backup created before edit

Reviewer feedback checked:
- ClinGen SVI page confirms the SVI WG was retired in April 2025 and asks users, as of July 2025, to use the ClinGen Variant Classification Guidance hub.
- ClinGen/Pejaver 2022 PP3/BP4 calibration does not include AlphaMissense developer thresholds. Later ClinGen-associated work in Genetics in Medicine 2025 calibrates AlphaMissense/ESM1b/VARITY, but developer defaults should not be used as ACMG PP3/BP4 thresholds.
- ClinGen Dec 2023 guidance links PP1/BS4 co-segregation and PP4 phenotype specificity and provides a points-based framework.

Files changed:
- SKILL.md
  - Version bumped to 0.3.4.
  - Clarified SVI retirement vs July 2025 guidance-hub transition.
  - Replaced AlphaMissense 0.85/0.1 as PP3/BP4 thresholds with a caution to use later calibrated intervals or VCEP/CSpec thresholds.
  - Added ClinGen 2023 PP1/BS4 + PP4 phenotype/segregation framework notes.
  - Added ACGS 2020/2023 to the authority hierarchy as a practice reference.
- scripts/evidence_router.py
  - Removed hard-coded AlphaMissense developer thresholds from CALIBRATED_TOOLS.
  - Added EMERGING_CALIBRATED_TOOL_NOTES for AlphaMissense, ESM1b, and VARITY.
- templates/evidence-table.md
  - Updated PP3/BP4 caveat and PP4 caveat.

Validation:
- classifier reference cases: passed.
- evidence_router example JSON: valid.
- direct test module execution: tests/test_classifier.py and tests/test_evidence_router.py passed.


## 2026-04-26 17:05 CST — v0.3.5 portability wording

Backup before this round:
- Local backup created before edit

Rationale:
- The workflow should be broadly reusable by agents, CLI scripts, notebooks, LIMS/case-management systems, and human SOPs.
- Reduce runtime-specific wording and document portable usage modes.

Files changed:
- SKILL.md
  - Version bumped to 0.3.5.
  - Added portability note near the introduction.
  - Added "Portable usage" section.
  - Marked Python helper scripts as plain Python.
  - Reworded several "skill" references to "workflow" where the clinical method is meant.
- README.md
  - Updated in the GitHub repository to present the project as a portable ACMG/AMP workflow.

Validation:
- classifier reference cases: passed.
- evidence_router example JSON: valid.
- direct test module execution: tests/test_classifier.py and tests/test_evidence_router.py passed.


## 2026-04-26 17:12 CST — v0.3.6 neutral platform wording

Backup before this round:
- Local backup created before edit

Rationale:
- Avoid over-explaining platform independence. The documentation should read naturally as a generic ACMG/AMP workflow rather than repeatedly emphasizing any one runtime.

Files changed:
- SKILL.md
  - Version bumped to 0.3.6.
  - Replaced explicit platform-brand wording with neutral platform-agnostic language.
  - Replaced absolute installation-path validation examples with repository-relative commands.
- README.md
  - Updated in the GitHub repository with the same neutral wording.

Validation:
- classifier reference cases: passed.
- evidence_router example JSON: valid.
- direct test module execution: tests/test_classifier.py and tests/test_evidence_router.py passed.
