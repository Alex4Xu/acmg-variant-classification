---
name: acmg-variant-classification
description: Standard workflow for ACMG/AMP germline small-variant classification — collect evidence, route external databases in a fixed priority order, assign criteria, detect conflicts, and produce a review-ready classification summary.
version: 0.3.3
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [acmg, clinvar, genomics, variant-classification, clinical-genetics]
    caution: This skill is a decision-support workflow only and does not replace expert clinical review.
prerequisites:
  commands: [python3]
---

# ACMG Variant Classification

Use this skill when a user wants a structured ACMG/AMP-style interpretation workflow for a **germline SNV/indel**.

This skill is for:
- Standardizing intake
- Preventing skipped evidence categories
- Applying combination logic consistently
- Producing a review-ready summary

This skill is **not** for:
- CNV/SV classification
- Somatic oncology interpretation
- Mitochondrial variant interpretation
- Fully automated clinical sign-out

## Safety / scope

Always say clearly:
- This is decision support, not a final clinical diagnosis.
- Gene/disease-specific ClinGen guidance overrides generic ACMG rules where applicable.
- Use ClinGen Variant Classification Guidance as the current hub for general and criteria-specific recommendations; the SVI WG itself was retired in April 2025.
- ACMG/AMP/CAP/ClinGen SVC v4.0 is currently forthcoming/under development and should not be applied as current guidance until final release.
- Final classification requires expert manual review.

## Inputs you should collect

Use `templates/intake.md` and ask for or normalize these fields:
- Gene
- Transcript
- Genome build
- c.HGVS
- p.HGVS
- Variant type
- Zygosity
- Inheritance model
- Phenotype / disease context
- Population frequency evidence
- Functional evidence
- Segregation / de novo evidence
- Database assertions
- Literature evidence

If transcript, genome build, or HGVS is unclear, stop and ask for clarification before classification.

## Interaction mode

Default to a guided interview workflow.

When using this skill with a live user:
1. Ask for one block of information at a time
2. Wait for the user's answer before moving on
3. Do not request all evidence at once unless the user asks for a bulk template
4. Explicitly track what is known, unknown, and still needed
5. Treat phenotype, family history, segregation data, and parental genotypes as user-supplied inputs that may arrive incrementally

Recommended guided sequence:
1. Variant identity: gene, transcript, build, c.HGVS, p.HGVS, variant type
2. Clinical phenotype / suspected disease
3. Inheritance model and family structure
4. Parental genotype status and de novo / segregation details
5. Population / database / literature evidence
6. Functional and computational evidence
7. Criteria assignment and final review

At each step, summarize back in one compact block:
- confirmed facts
- missing facts
- provisional ACMG implications

## External evidence routing (fixed heuristic subflow)

When variant identity is sufficiently defined, run a fixed external-evidence routing pass before scoring criteria.

### Trigger conditions

Activate this subflow automatically when any of the following is true:
- the user explicitly asks for ACMG / AMP classification
- the user provides `gene` plus `c.HGVS` or `p.HGVS`
- the user provides transcript/build/HGVS plus phenotype in a germline context
- the user asks whether PM2 / BA1 / BS1 / PS2 / PM6 / PP4 / PS3 should apply

### Source priority

Treat outside resources as evidence suppliers, not as final judges.

Priority order:
1. **ClinGen** — gene / disease-specific guidance, disease mechanism, rule overrides
2. **ClinVar** — prior assertions, conflict pattern, review status
3. **gnomAD** — population frequency / absence checks
4. **Literature deep dive** — Mastermind, PubTator 3, PubMed only if the first three layers leave unresolved questions
5. **Aggregators** — VarSome / Franklin style dashboards for rapid triage only; never let them replace the local evidence ledger

### Routing rules

- Always check **ClinGen first** before applying generic ACMG logic.
- Always check **ClinVar** and record review status and whether assertions are concordant or conflicting.
- Always check **gnomAD** before using PM2 / BA1 / BS1.
- Escalate to **literature deep dive** only when one of these is true:
  - ClinVar is absent, sparse, or strongly conflicting
  - exact-variant evidence is missing but nearby-variant or regional evidence may matter
  - phenotype match is central to PP4 and needs literature support
  - functional evidence or de novo claims need source-level verification
- Keep every outside claim attached to a local note: criterion candidate, source, and caveat.

### Programmatic hinting

Use `scripts/evidence_router.py` to convert a normalized intake record into:
- required source order
- blockers that prevent confident scoring
- candidate criteria needing outside evidence
- whether literature escalation is actually needed
- normalized ClinVar / gnomAD snapshots suitable for local note-taking
- a candidate evidence ledger draft that can be reviewed and edited locally

This script does **not** classify the variant. It decides what evidence-gathering path should run next and produces a draft ledger for human review.

## Standard workflow

### Step 1: Confirm scope

Proceed only if all are true:
1. Variant is a germline small variant (SNV/indel)
2. Naming/build/transcript are defined
3. User understands output is review-only
4. Any gene-specific ACMG framework has been checked

If not, stop and explain what is missing.

### Step 2: Normalize the record

Create a clean variant record using `templates/intake.md`.

Record at minimum:
- identity fields
- disease context
- inheritance assumptions
- source list
- unresolved data gaps

### Step 2.5: Run external-evidence routing

Before assigning criteria, run the fixed heuristic routing pass.

Recommended flow:
1. normalize the intake record
2. run `scripts/evidence_router.py` on that normalized record
3. follow the returned source order
4. review the returned normalized source snapshots and candidate evidence ledger draft
5. fill the evidence table with local notes rather than copying outside conclusions

At this stage, explicitly label each source as one of:
- rule override
- database assertion context
- population evidence
- literature evidence
- aggregator summary only

### Step 3: Gather evidence by ACMG bucket

Check every bucket explicitly so nothing is skipped.
Record both the **default** (2015) and **applied** strength — they often differ due to ClinGen SVI updates.

Pathogenic side:
- PVS1 (variable: Very Strong → Supporting per decision tree)
- PS1, PS2 (point-based), PS3 (capped at Moderate without validated assay), PS4 (point-based)
- PM1, PM2 (**default Supporting** — SVI 2020), PM3 (variable: Supporting→Strong), PM4, PM5, PM6 (point-based)
- PP1 (Bayesian LOD: LOD ≥1.9 Supporting, ≥3.0 Moderate, ≥5.0 Strong, >5.0 Very Strong), PP2, PP3 (calibrated individual tool), PP4

Benign side:
- BA1 (**disease-specific threshold** — SVI 2018)
- BS1 (**disease-specific threshold**), BS2 (point-based), BS3, BS4 (Bayesian LOD)
- BP1, BP2 (point-based), BP3, BP4 (calibrated individual tool), BP5 (point-based), BP7

**Deprecated — do not use:** PP5, BP6 (ClinGen SVI, ACGS 2023).

### Step 4: Assign criteria carefully

Use `templates/evidence-table.md`.
For each criterion, record:
- code
- strength
- triggered yes/no
- reason
- source
- caveat / limitation

Do not double count:
- overlapping population evidence
- duplicated functional evidence
- literature/database entries that cite the same underlying data

**PP3/BP4 (computational evidence):** Use calibrated individual tool thresholds (Pejaver 2022/2024). One well-calibrated tool suffices — no consensus across multiple tools required. Recommended tools with published thresholds:
- REVEL: PP3 ≥0.7, BP4 ≤0.3
- BayesDel_addAF: PP3 ≥0.34, BP4 ≤-0.36
- CADD: PP3 ≥25.3, BP4 ≤22.7
- AlphaMissense: PP3 ≥0.85, BP4 ≤0.1

If a VCEP specifies its own thresholds, use those instead. Do not double-count multiple tools for the same PP3/BP4 application.

### Step 5: Evaluate conflicts

If both pathogenic and benign evidence exist:
1. Check whether evidence is truly independent
2. Downgrade/remove misapplied criteria if needed
3. If conflict remains unresolved, prefer VUS over forced certainty
4. State what additional data could resolve the conflict

Implementation note: `scripts/classifier.py` treats `conflict=True` as a conservative manual-review flag. Set it only after confirming that pathogenic and benign evidence are both present, independent, and unresolved; do not use it as a raw "any P plus any B" detector.

### Step 5.5: Handle common evidence-substitution pitfalls

Apply these guardrails before final scoring:
- **PS2/PM6 (de novo):** Use SVI v1.1 point-based scoring. Phenotype consistency + parentage status + observation count → total points → strength mapping. PS2 requires **confirmed parentage by genetic testing**; trio-WES without biochemical confirmation = PM6. Prenatal cases always = "limited phenotype". Points: consistent+confirmed=2, consistent+assumed=1, limited+confirmed=1, limited+assumed=0.5. Strength: ≥6=Very Strong, 4-5.99=Strong, 2-3.99=Moderate, <2=Supporting.
- **PS3:** Assay must be validated with known pathogenic/benign controls, reproducible, in appropriate cellular context. Without a validated disease-specific assay, cap PS3 at **Moderate** (SVI 2024). Most VCEPs follow this cap.
- **PVS1:** Do not apply at full Very Strong by default. Use the Abou Tayoun 2018 decision tree to determine applicable strength level (Very Strong/Strong/Moderate/Supporting). Consider: variant type → LOF mechanism → NMD eligibility → critical functional domain → rescue by alternative transcripts. Splice-altering variants confirmed by RNA evidence can reach PVS1_Strong (Walker 2023).
- **BA1/BS1:** Do not use flat 5%/1% thresholds. Use **disease-specific thresholds** from ClinGen BA1/BS1 calculator based on prevalence, genetic heterogeneity, and penetrance. Check ClinGen BA1/BS1 exception list for special cases.
- **PM2:** Default is **Supporting** (SVI 2020), not Moderate. Apply only when allele frequency is below the disease-specific maximum credible MAF. Some VCEPs may permit Moderate with additional justification.
- **PP1/BS4 (co-segregation):** Use Bayesian LOD framework. Strength scales: LOD ≥1.9=Supporting, ≥3.0=Moderate, ≥5.0=Strong, >5.0=Very Strong. Adjust for reduced penetrance.
- **BS2/BP2/BP5:** Use point-based scoring (VCEP adaptations). BS2 requires phenotype context to avoid counting carriers as healthy observations.
- If the exact variant lacks a functional assay, do not assign PS3 from experiments on nearby variants alone.
- Nearby pathogenic in-frame variants in the same constrained / functionally critical region may support PM1 discussion, but not exact-variant equivalence.
- Exact absence from ClinVar is not evidence by itself; use it only as context, not as a criterion.
- For in-frame duplication/insertion events, verify whether the event falls in a known functional domain or mutational cluster before using PM1 or PM4.

### Step 6: Apply combination logic

Use `scripts/classifier.py` or reproduce its logic manually. Applied strength modifiers count by their final strength bucket: for example, `PM3_Strong` counts as one Strong criterion, while `PM3_Supporting` counts as one Supporting criterion.

Combination-source guardrail:
- The default classifier follows ACMG/AMP 2015 Table 5 qualitative combinations.
- Later ClinGen SVI work mainly refines individual criteria and strength calibration; it does not add a general ACMG/AMP rule that `3 Moderate + 3 Supporting` is Pathogenic.
- Under the Tavtigian/ClinGen Bayesian point framework, Supporting=1, Moderate=2, Strong=4, Very Strong=8; Likely Pathogenic starts around 6 points and Pathogenic around 10 points. `3M + 3P = 9 points`, so it remains Likely Pathogenic unless a disease/gene-specific VCEP/CSpec or explicitly adopted lab framework says otherwise.
- If using a non-default framework (Sherloc, InterVar-derived local logic, lab-specific Bayesian thresholds, or VCEP/CSpec-specific combining logic), document the source, version, and scope in the report before overriding this classifier.

Pathogenic if any:
- 1 Very Strong + >=1 Strong
- 1 Very Strong + >=2 Moderate
- 1 Very Strong + 1 Moderate + 1 Supporting
- 1 Very Strong + >=2 Supporting
- >=2 Strong
- 1 Strong + >=3 Moderate
- 1 Strong + 2 Moderate + >=2 Supporting
- 1 Strong + 1 Moderate + >=4 Supporting

Likely Pathogenic if any:
- 1 Very Strong + 1 Moderate
- 1 Strong + 1 to 2 Moderate
- 1 Strong + >=2 Supporting
- >=3 Moderate
- 2 Moderate + >=2 Supporting
- 1 Moderate + >=4 Supporting

Benign if any:
- BA1
- >=2 Strong benign criteria

Likely Benign if any:
- 1 Strong benign + 1 Supporting benign
- >=2 Supporting benign

Else:
- VUS

### Step 7: Mandatory review output

Final answer should include all of:
1. Normalized variant description
2. Evidence table summary
3. Conflict summary
4. Final class
5. Why this class was reached
6. What would change the class later
7. Explicit statement that expert review is still required

## Output format

Recommended sections:
1. Variant summary
2. Evidence supporting pathogenicity
3. Evidence supporting benign impact
4. Conflicts / limitations
5. Provisional ACMG class
6. Reclassification triggers

## Files included

- `templates/intake.md` — structured case intake
- `templates/evidence-table.md` — criterion recording sheet
- `templates/external-evidence-checklist.md` — fixed source-order worksheet for outside evidence
- `templates/report_cn.md` — Chinese report skeleton for case delivery
- `references/sop.md` — process-control SOP; technical criteria remain in SKILL.md
- `scripts/classifier.py` — minimal ACMG combination engine
- `scripts/evidence_router.py` — heuristic router for source priority, blockers, ClinVar/gnomAD normalization, and candidate ledger drafting
- `templates/example-intake.json` — runnable example record for router output
- `references/test_cases.json` — sample logic tests

## ClinGen Variant Classification Guidance / SVI Updates (critical context for all criteria)

As of the 2026-04 wiki refresh, the current entry point is the **ClinGen Variant Classification Guidance** page. The ClinGen Sequence Variant Interpretation Working Group was retired in April 2025, but its recommendations remain the main body of refinements to the 2015 ACMG/AMP framework and are now surfaced through the guidance hub.

Practical rule:
1. Start with ACMG/AMP 2015.
2. Check ClinGen CSpec / VCEP gene-disease specifications first.
3. Use the ClinGen Variant Classification Guidance page as the current canonical index for general and criteria-specific recommendations.
4. Treat older SVI WG pages as archival/source documents.
5. Track ACMG/AMP/CAP/ClinGen SVC v4.0 as forthcoming only; do not apply it as current guidance until final release.

Key changes that affect daily classification:

**Point-based criteria** (replacing binary yes/no):
- PS2/PM6 (de novo): see Step 5.5
- PS4 (case observation): consistent phenotype=1pt, limited=0.5pt, non-consistent=-1pt
- BS2 (healthy observation): confirmed healthy adult=2pt, observed without phenotype detail=1pt
- BP2/BP5 (alternate basis): confirmed=2pt, probable=1pt; can combine additively

**Calibrated computational evidence** (PP3/BP4): see Step 4

**PVS1 decision tree** (Abou Tayoun 2018):
| PVS1 Level | When to Apply |
|-----------|--------------|
| PVS1 (Very Strong) | Confirmed null variant, LOF established, NMD-eligible, not in last exon/critical domain |
| PVS1_Strong | Most LOF variants in known LOF disease genes (NMD-eligible) |
| PVS1_Moderate | Uncertain functional impact (non-canonical splice, partial LOF) |
| PVS1_Supporting | Weak LOF evidence, in-frame LOF in critical domains |

**Splicing framework** (SVI Splicing SG 2023, updated 2024):
- Comprehensive framework for PVS1/PS1/PP3/BP4/BP7 applied to splice-altering variants
- In silico splice prediction tools calibrated for PP3/BP4 splice evidence
- RNA-seq as functional evidence for PS3/BS3 splice impact
- BP7 updated: synonymous variants with predicted splice impact no longer automatically BP7
- Variants causing aberrant splicing confirmed by RNA evidence can reach PVS1_Strong

**PS3/BS3 functional evidence** (SVI 2024):
- Assays must be validated with known pathogenic and benign controls
- Results must be reproducible across independent experiments/labs
- Appropriate cellular context and physiological conditions required
- Many VCEPs cap PS3 at Moderate without validated, disease-specific functional assays
- ClinGen Functional Assay Documentation Worksheet available for standardized reporting

**PM3 in trans** (SVI v1.0):
- Requires evidence that variants are on opposite alleles
- PM3_Supporting: 1 observation in trans + PM2_Supporting met
- PM3_Moderate: 2+ observations, or 1 observation with strong phase evidence
- PM3_Strong: 3+ observations with confirmed phase
- Cannot apply PM3 and PS4 from the same case

**Code modification convention:** When modifying a criterion's strength per SVI, write the applied code as `PM2_Supporting` (not just "PM2 at Supporting"). ClinGen SVI recommends this convention for clarity in reports and databases.

**Multi-disorder genes:** For genes associated with multiple phenotypes (e.g., GJB2 → deafness, skin disorders), evaluate each gene-disease pair separately. Classification may differ for the same variant across disease contexts.

**Non-coding variants:** ClinGen has endorsed recommendations for clinical interpretation of non-coding region variants. Outside the current scope of this skill but note that non-coding variants adjacent to splice regions may qualify for splicing framework analysis.

**gnomAD:** Prefer v4 allele frequencies when available (more diverse populations). Use v4 as default for PM2/BA1/BS1 assessments.


## Key references / authority hierarchy

Use references in this order when rules appear to conflict:
1. Disease/gene-specific ClinGen VCEP / CSpec guidance and documented local lab SOP.
2. ClinGen Variant Classification Guidance / archived SVI recommendations for individual ACMG/AMP criteria.
3. ACMG/AMP 2015 Table 5 for default qualitative combination logic.
4. Tavtigian et al. Bayesian / point framework as a quantitative consistency check and calibration aid.
5. Software implementations (InterVar, VarSome, Franklin, Sherloc-style tools) as triage aids only unless the lab has formally adopted that framework.

Important combination note: `3 Moderate + 3 Supporting` is not a generic Pathogenic combination in ACMG/AMP 2015 and is also below the 10-point Pathogenic threshold in the Tavtigian point framework. Treat it as Likely Pathogenic by default.

## Optional deliverable workflow

For real case work, prefer this output sequence:
1. intake record
2. analysis summary
3. final case report in Markdown
4. optional PDF export

For Chinese clinical-style output, write a concise report with these sections:
- basic variant information
- phenotype summary
- family / trio findings
- external evidence (gnomAD, ClinVar, literature)
- ACMG criteria used / not used
- final provisional classification
- limitations and what could upgrade or downgrade confidence

If producing a PDF locally, keep the Markdown report as the source of truth and render the PDF from that report rather than maintaining two independent versions.

## Maintenance / review workflow

When the user provides an external review or critique of this skill, do not immediately edit files unless the user explicitly asks to continue/implement. Use this sequence:
1. Triage each proposed change as: clinical-safety bug, code-quality bug, documentation clarification, test-coverage gap, or design preference.
2. For clinical rules, verify against the authority hierarchy above before accepting the change. Do not rely on ACMG/AMP 2015 alone when later ClinGen/VCEP/SVI guidance may apply; also do not treat software behavior as authority unless the lab formally adopts that framework.
3. Present the proposed accept/reject/defer list to the user and wait for permission before modifying files.
4. Before editing, create a backup if the skill directory is not in a git repository.
5. After editing, run classifier tests, router JSON smoke test, and direct `test_*` module execution if `pytest` is unavailable.
6. Record the rationale, files changed, backup path, and validation results in `CHANGELOG.md`.

## Validation

Run:

```bash
python3 ~/.hermes/skills/healthcare/acmg-variant-classification/scripts/classifier.py \
  ~/.hermes/skills/healthcare/acmg-variant-classification/references/test_cases.json

python3 ~/.hermes/skills/healthcare/acmg-variant-classification/scripts/evidence_router.py \
  ~/.hermes/skills/healthcare/acmg-variant-classification/templates/example-intake.json
```

Expect the classifier tests to pass and the router to emit both a structured source-order summary and a candidate evidence ledger draft.

When modifying the skill itself, also run the router unit tests. If `pytest` is unavailable in the current Hermes environment, load the test module directly and execute all `test_*` functions:

```bash
python3 - <<'PY'
import importlib.util
from pathlib import Path
p = Path('~/.hermes/skills/healthcare/acmg-variant-classification/tests/test_evidence_router.py').expanduser()
spec = importlib.util.spec_from_file_location('test_evidence_router', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
for name in sorted(n for n in dir(m) if n.startswith('test_')):
    getattr(m, name)()
    print('PASS', name)
PY
```

For literature routing regressions, explicitly test the distinction between empty unchecked intake placeholders and checked-but-empty sources: `database_assertions: []` / `literature_evidence: []` alone should not trigger a literature deep dive; an empty checked ClinVar result should.

Also run classifier edge-case tests when present:

```bash
python3 - <<'PY'
import importlib.util
from pathlib import Path
p = Path('~/.hermes/skills/healthcare/acmg-variant-classification/tests/test_classifier.py').expanduser()
spec = importlib.util.spec_from_file_location('test_classifier', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
for name in sorted(n for n in dir(m) if n.startswith('test_')):
    getattr(m, name)()
    print('PASS', name)
PY
```

## Common pitfalls

**SVI-critical (will cause misclassification):**
- Using PM2 at Moderate strength by default — SVI 2020 changed it to Supporting
- Using flat 5% for BA1 — thresholds are disease-specific (ClinGen calculator required)
- Applying PVS1 at full Very Strength without running the decision tree
- Using PP3/BP4 by counting multiple in-silico tools as separate evidence — use calibrated individual tool thresholds instead
- Applying PS2 without confirmed parentage by genetic testing — use PM6 (point-based scoring)
- Applying PS3 at Strong without a validated, disease-specific functional assay — cap at Moderate

**Evidence quality:**
- Treating nearby pathogenic variants or nearby functional evidence as if they were variant-specific functional proof; nearby-region support may help PM1/PM1_supporting but does not justify PS3 for the exact variant
- Letting ClinVar / VarSome / Franklin style summaries replace the local ACMG evidence ledger instead of treating them as input sources
- Copying an outside platform's final classification without recording source-specific caveats, conflicts, and review status locally
- Going to literature deep dives before checking ClinGen, ClinVar, and gnomAD in order
- Treating PP5/BP6 as valid criteria — both are deprecated
- Forcing a result above VUS when conflicts are unresolved

**Domain-specific:**
- When a dominant early-onset neurodevelopmental variant is absent from gnomAD, conservative use of PM2_supporting is often safer than overcalling PM2 unless your lab framework or VCEP clearly supports stronger weighting
- If phenotype is strongly consistent but MRI/EEG or other ancillary data are missing, PP4 may still be considered cautiously, but explicitly document the missing phenotype data as a limitation
- When the exact variant is absent from ClinVar, nearby pathogenic in-frame variants in the same constrained functional region can support regional interpretation, but usually not exact-variant equivalence
- For splice-altering variants, check the splicing framework (SVI 2023) before automatically applying BP7 to synonymous variants
- Overcalling PM1 from nearby published variants; if evidence is regional but not exact-variant, consider PM1_supporting first

## Practical evidence notes learned in use

- If trio-WES shows the proband carries the variant and both unaffected parents are negative, but no parentage testing was done, prefer **PM6** over **PS2**. Use SVI v1.1 point-based scoring: 1 pt (limited+assumed or consistent+assumed) → Supporting.
- For severe dominant neurodevelopmental phenotypes, if the candidate variant is absent from gnomAD and no stronger population caveats are known, a conservative handling is **PM2_Supporting**. This aligns with the SVI 2020 default; only upgrade to PM2_Moderate if a VCEP or lab framework explicitly supports it.
- When the exact variant is absent from ClinVar, nearby pathogenic in-frame variants in the same constrained functional region can support regional interpretation (PM1), but usually not exact-variant equivalence.
- In guided case review, missing MRI/EEG should not block classification if the phenotype is still strongly gene-consistent, but it should be documented as a limitation on PP4 strength.
- For quick gnomAD checks via GraphQL, query `https://gnomad.broadinstitute.org/api` with dataset values like `gnomad_r4`, `gnomad_r3`, or `gnomad_r2_1`; the `variant` query does not take a `referenceGenome` argument. A "Variant not found" response across releases is usable as absence evidence, but document the exact queried representation. Prefer v4 data when available.
- For BA1/BS1 thresholds, always use the ClinGen BA1/BS1 calculator (https://clinicalgenome.org/tools/calculator-af/) or VCEP-specified thresholds. Never apply flat 5%/1% without confirming no disease-specific data exists.
- For PP3/BP4, one calibrated tool is sufficient. REVEL ≥0.7/≤0.3 are the most widely adopted thresholds. If multiple tools disagree, document the discrepancy rather than counting each as independent evidence.
- For splice variants near canonical sites or deep intronic, use the SVI Splicing SG 2023 framework: combine in silico splice predictions with RNA evidence when available. Do not automatically apply BP7 to synonymous variants with predicted splice impact.

## Guided questioning pattern

Use short, sequential prompts.
Good pattern:
- Step A: ask only for variant identity fields
- Step B: ask only for phenotype and suspected diagnosis
- Step C: ask only for pedigree / family history / inheritance
- Step D: ask only for parental genotypes and segregation/de novo details
- Step E: ask only for outside evidence such as ClinVar, literature, frequency, and functional assays
- Step F: summarize triggered or candidate ACMG criteria before giving a provisional class

Avoid dumping a giant questionnaire unless the user explicitly wants a full form.

## When to stop and ask the user

Ask for clarification if any of these are missing:
- Transcript
- Genome build
- HGVS notation
- Disease context
- Whether a gene-specific framework exists
- Family structure when segregation evidence may matter
- Parental genotype status when de novo logic may matter

## Reminder

This skill helps structure ACMG reasoning. It does not replace clinical-grade review, lab SOPs, or disease-specific expert specifications.
