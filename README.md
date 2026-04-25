# Hermes Agent: ACMG Variant Classification Skill

A Hermes Agent skill for structured ACMG/AMP-style interpretation of germline small variants (SNVs/indels).

This repository provides a reusable clinical-genetics workflow: normalize variant intake, collect evidence in a fixed source order, assign ACMG/AMP criteria with ClinGen refinements, detect conflicts, apply combination logic, and produce a review-ready summary.

Version: 0.3.1

## What this skill is for

Use this skill when you need a disciplined decision-support workflow for germline small-variant classification, especially when you want to avoid skipped evidence categories or over-reliance on database final assertions.

Typical use cases:

- Germline SNV/indel ACMG/AMP evidence review
- ClinVar / gnomAD / ClinGen / literature evidence organization
- Provisional classification summaries for expert review
- Chinese clinical-style report drafting
- Variant curation training and SOP standardization

This skill is not intended for:

- CNV/SV classification
- Somatic oncology interpretation
- Mitochondrial variant interpretation
- Automated clinical sign-out
- Replacing laboratory SOPs, VCEP specifications, or expert review

## Current guidance baseline

The workflow starts from the 2015 ACMG/AMP framework and incorporates major ClinGen refinements.

Important v0.3.1 update:

- ClinGen Variant Classification Guidance is treated as the current hub for general and criteria-specific recommendations.
- The ClinGen Sequence Variant Interpretation Working Group was retired in April 2025, but its recommendations remain important and are surfaced through the ClinGen guidance hub.
- Gene/disease-specific ClinGen VCEP or CSpec specifications override generic ACMG/AMP logic when available.
- ACMG/AMP/CAP/ClinGen SVC v4.0 is currently considered forthcoming / under development and should not be applied as current guidance until final release.

Key refinements covered:

- Point-based de novo scoring: PS2 / PM6
- Disease-specific population frequency thresholds: BA1 / BS1
- PM2 defaulting to Supporting strength under SVI guidance
- PVS1 decision tree and variable-strength loss-of-function interpretation
- Splicing variant framework for PVS1 / PS1 / PP3 / BP4 / BP7
- Functional evidence validation requirements for PS3 / BS3
- Bayesian co-segregation scoring: PP1 / BS4
- Calibrated computational evidence: PP3 / BP4
- PM3 strength scaling for in-trans evidence
- PP5 / BP6 deprecation
- Criterion strength modification convention, e.g. PM2_Supporting

## Repository contents

```text
SKILL.md
  Full Hermes skill definition and step-by-step workflow.

scripts/classifier.py
  Minimal ACMG/AMP combination logic engine.

scripts/evidence_router.py
  Heuristic source-priority router. It does not classify the variant; it recommends evidence-gathering order and drafts a candidate ledger.

templates/intake.md
  Structured case intake form.

templates/evidence-table.md
  Criterion recording sheet with default strength, applied strength, reason, source, and caveat.

templates/external-evidence-checklist.md
  Fixed source-order worksheet: ClinGen → ClinVar → gnomAD → literature → aggregators.

templates/report_cn.md
  Chinese clinical-style report skeleton.

templates/example-intake.json
  Example input record for evidence_router.py.

references/sop.md
  Detailed standard operating procedure.

references/test_cases.json
  Sample test cases for classifier.py.

tests/test_evidence_router.py
  Unit tests for the evidence router.
```

## Recommended workflow

1. Confirm scope
   - Germline SNV/indel only.
   - Transcript, genome build, HGVS, disease context, and inheritance model should be defined before classification.

2. Normalize the case
   - Use templates/intake.md.
   - Record known facts, unknowns, and unresolved blockers.

3. Route evidence collection
   - Use ClinGen first for VCEP/CSpec/gene-disease rules.
   - Use ClinVar for prior assertions and review status.
   - Use gnomAD for population frequency / absence evidence.
   - Escalate to literature only when required.
   - Treat VarSome / Franklin-style aggregators as triage aids, not final evidence.

4. Assign criteria
   - Record both default and applied strength.
   - Attach every criterion to source evidence and caveats.
   - Avoid double-counting.

5. Resolve conflicts
   - If pathogenic and benign evidence conflict, re-check independence and correct misapplied criteria.
   - If unresolved, prefer VUS rather than forced certainty.

6. Apply combination logic
   - Use scripts/classifier.py or manually reproduce the logic.

7. Produce review-ready output
   - Variant summary
   - Pathogenic evidence
   - Benign evidence
   - Conflicts / limitations
   - Provisional class
   - Reclassification triggers
   - Explicit note that expert review is required

## Quick validation

Run from the repository root:

```bash
python3 scripts/classifier.py references/test_cases.json
python3 scripts/evidence_router.py templates/example-intake.json
```

Expected classifier result:

```text
passed: 6 / 6
```

If pytest is installed:

```bash
python3 -m pytest -q tests/test_evidence_router.py
```

Expected pytest result:

```text
3 passed
```

## Example: evidence router

```bash
python3 scripts/evidence_router.py templates/example-intake.json
```

The router returns a structured plan including:

- Required source order
- Blockers that prevent confident scoring
- Candidate criteria needing outside evidence
- Whether literature escalation is needed
- Draft evidence ledger entries

Important: the router does not perform final classification.

## Example: classifier

```bash
python3 scripts/classifier.py references/test_cases.json
```

The classifier applies ACMG/AMP combination rules to already-assigned criteria. It assumes the evidence assignment has already been reviewed.

## Install as a Hermes skill

If this repository is cloned locally, you can use it as a Hermes skill by placing or symlinking it under your Hermes skills directory.

Example:

```bash
mkdir -p ~/.hermes/skills/healthcare
ln -s /path/to/acmg-variant-classification ~/.hermes/skills/healthcare/acmg-variant-classification
```

Then load it in Hermes when doing ACMG/AMP case work.

## Safety and clinical limitations

This repository is decision support only.

Do not use it as the sole basis for clinical diagnosis, patient management, genetic counseling, embryo selection, or laboratory sign-out.

Always apply:

- Local laboratory SOPs
- Disease-specific ClinGen VCEP / CSpec rules
- Current ClinGen Variant Classification Guidance
- Manual expert review
- Appropriate privacy and data governance controls

Sensitive genetic and medical data should be handled according to applicable institutional, legal, and ethical requirements. Avoid sending identifiable patient data to online services unless explicitly permitted and appropriately governed.

## License

MIT
