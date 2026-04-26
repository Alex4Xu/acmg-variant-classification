# ACMG Variant Classification SOP

Purpose: define lab process control for ACMG/AMP-based germline SNV/indel interpretation. Technical criterion details live in SKILL.md; this SOP focuses on intake, review, sign-off, archiving, and version control.

## Scope
Use for:
- germline SNV / indel
- review-oriented variant interpretation
- standardized evidence capture

Do not use as-is for:
- CNV / SV
- somatic oncology
- mitochondrial variants
- final unsupervised clinical reporting

## Core process

### 0. Precheck
Confirm:
- sample and variant identifiers are unique
- transcript is fixed
- genome build is fixed
- HGVS naming is coherent
- gene/disease-specific ACMG guidance was checked

### 1. Intake
Collect variant identity, phenotype context, inheritance model, source list, and missing data.

### 2. Evidence gathering
Use SKILL.md as the technical evidence-gathering reference. This SOP requires documentation that all evidence buckets were considered, without duplicating the criterion-specific rules.

### 3. Criteria assignment
For each criterion record:
- yes/no
- justification
- source
- caveat

### 4. Anti-double-counting review
Do not stack overlapping evidence from the same underlying dataset.

### 5. Conflict review
If pathogenic and benign evidence coexist, prefer explicit conflict analysis over forced upgrading.
Unresolved conflict should usually remain VUS.

### 6. Combination logic
Use the current SKILL.md combination logic / classifier helper after manual confirmation of all triggered criteria. Record the SKILL.md version used.

### 7. Independent review
Check especially:
- transcript correctness
- LoF mechanism before PVS1
- frequency thresholds for BA1/BS1/PM2
- improper PP3/BP4 inflation
- unsupported ClinVar overreliance

### 8. Sign-off
Require at least one qualified reviewer to confirm:
- variant identity and transcript
- gene-disease validity and inheritance model
- VCEP/CSpec applicability
- criteria independence / double-counting review
- final classification and reclassification triggers

### 9. Archive
Store:
- normalized variant description
- evidence table
- final logic summary
- reviewer/date/version
- SKILL.md version and any VCEP/CSpec version used
- evidence source retrieval dates
- reclassification triggers

## Minimum reportable output
- Normalized variant descriptor
- Triggered evidence codes
- Conflict explanation
- Final provisional ACMG class
- Review limitations
- Reclassification triggers


## Change-control rule
When SKILL.md or helper scripts change, record:
- date/time
- files changed
- clinical rationale
- validation commands and results
- backup path if no git repository is available
