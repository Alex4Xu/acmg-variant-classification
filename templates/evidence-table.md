# ACMG Evidence Table

> **SVI 2020+:** PM2 defaults to **Supporting** (not Moderate). PP5/BP6 are deprecated.
> **SVI 2018+:** BA1/BS1 use **disease-specific thresholds**, not flat 5%/1%.
> **SVI v1.1:** PS2/PM6, PS4, BS2, BP2/BP5 use **point-based scoring** for variable strength.
> **SVI 2022/2024:** PP3/BP4 use **calibrated individual tool thresholds** (one tool suffices).
> **Framework:** Record VCEP/CSpec or local lab framework before overriding generic ACMG/AMP 2015 combination logic.

| Code | Default Strength | Applied Strength | Triggered | Reason | Source | Caveat / limitation |
|------|-----------------|-----------------|-----------|--------|--------|---------------------|
| PVS1 | Very Strong | | No | | | Decision tree: VS/Strong/Moderate/Supporting per Abou Tayoun 2018 |
| PS1 | Strong | | No | | | |
| PS2 | Strong | | No | | | Point-based (SVI v1.1): Supporting→Very Strong. Confirmed parentage required. |
| PS3 | Strong | | No | | | Capped at Moderate without validated assay (SVI 2024) |
| PS4 | Strong | | No | | | Point-based: Supporting→Strong per VCEP adaptation |
| PM1 | Moderate | | No | | | |
| PM2 | **Supporting** | | No | | | **SVI 2020: default Supporting.** Use disease-specific MAF threshold from ClinGen calculator. |
| PM3 | Moderate | | No | | | Variable: Supporting/Moderate/Strong (SVI v1.0). Requires in trans phase. |
| PM4 | Moderate | | No | | | |
| PM5 | Moderate | | No | | | |
| PM6 | Moderate | | No | | | Point-based (SVI v1.1): Supporting→Strong. Assumed parentage. |
| PP1 | Supporting | | No | | | Bayesian LOD: ≥1.9 Supporting, ≥3.0 Moderate, ≥5.0 Strong, >5.0 Very Strong |
| PP2 | Supporting | | No | | | |
| PP3 | Supporting | | No | | | Calibrated individual tool. REVEL/BayesDel/CADD use ClinGen/Pejaver-style thresholds; AlphaMissense requires later calibrated intervals or VCEP approval, not developer default cutoffs. |
| PP4 | Supporting | | No | | | ClinGen 2023: phenotype specificity is coupled to PP1/BS4/locus evidence; avoid vague phenotype-only upgrading |
| ~~PP5~~ | ~~Supporting~~ | | — | | | **DEPRECATED** (ClinGen SVI, ACGS 2023). Do not use. |
| BA1 | Stand-alone | | No | | | **Disease-specific threshold** (SVI 2018). Use ClinGen BA1/BS1 calculator. |
| BS1 | Strong | | No | | | **Disease-specific threshold** (SVI 2018). |
| BS2 | Strong | | No | | | Point-based for healthy observations. Requires phenotype context. |
| BS3 | Strong | | No | | | Requires validated assay (SVI 2024) |
| BS4 | Strong | | No | | | Bayesian LOD: ≥1.9 Supporting, ≥3.0 Moderate, ≥5.0 Strong, >5.0 Very Strong |
| BP1 | Supporting | | No | | | |
| BP2 | Supporting | | No | | | Point-based scoring for alternate molecular basis |
| BP3 | Supporting | | No | | | |
| BP4 | Supporting | | No | | | Calibrated individual tool. REVEL/BayesDel/CADD use ClinGen/Pejaver-style thresholds; AlphaMissense requires later calibrated intervals or VCEP approval, not developer default cutoffs. |
| BP5 | Supporting | | No | | | Point-based scoring for alternate diagnosis |
| ~~BP6~~ | ~~Supporting~~ | | — | | | **DEPRECATED** (ClinGen SVI, ACGS 2023). Do not use. |
| BP7 | Supporting | | No | | | Splicing update 2023: synonymous with predicted splice impact ≠ automatic BP7 |

## Applied Strength Notes

When a criterion's applied strength differs from its default (2015), record the SVI justification:
- **PM2**: If applying as Moderate, document VCEP specification or additional disease-specific justification
- **PVS1**: Record decision tree path (e.g., PVS1_Strong for NMD-eligible LOF, PVS1_Moderate for non-canonical splice)
- **PS3**: If applying as Strong, document validated assay status; otherwise cap at Moderate
- **PS2/PM6**: Record point calculation and final strength mapping
- **PP1/BS4**: Record LOD score and strength mapping

## Framework / source version
- ACMG/AMP combination framework used: ACMG/AMP 2015 default / VCEP-CSpec / local lab framework / other:
- VCEP/CSpec name and version/date, if any:
- ClinGen guidance pages checked date:

## Summary counts
- Pathogenic: VS= , S= , M= , P=
- Benign: BA= , BS= , BP=
- Conflicting evidence unresolved? Yes / No

## Provisional conclusion
- Final ACMG class:
- Why:
- What data could change it:
