# External Evidence Routing Checklist

## Normalized intake snapshot
- Gene:
- Transcript:
- Genome build:
- c.HGVS:
- p.HGVS:
- Variant type:
- Phenotype / disease context:
- Inheritance model:
- Family structure:
- Parental genotypes:

## Fixed source order
1. ClinGen
2. ClinVar
3. gnomAD
4. Literature deep dive only if still needed
5. Aggregator dashboards for triage only

## Source worksheet

| Source | Purpose | Checked? | Key finding | Review status / confidence | Caveat |
|--------|---------|----------|-------------|----------------------------|--------|
| ClinGen | Rule override / mechanism | No | | | |
| ClinVar | Assertion context | No | | | |
| gnomAD | Population evidence | No | | | |
| Mastermind | Variant-level literature | No | | | |
| PubTator3 / PubMed | Primary literature review | No | | | |
| VarSome / Franklin | Aggregator summary only | No | | | |

## Candidate ACMG criteria needing outside support
- PVS1 review:
- PM2 / BA1 / BS1:
- PS2 / PM6:
- PP1 / BS4:
- PP4:
- PS3 / BS3:
- PM1 / PM4:

## Blocking gaps
- 

## Escalate to literature deep dive if
- ClinVar is absent, sparse, or conflicting
- exact-variant evidence is missing but regional evidence may matter
- phenotype fit is central and needs literature support
- functional or de novo claims need primary-source verification

## Guardrails
- Do not copy an outside platform's final classification as your final answer.
- Record each outside claim locally with source and caveat.
- Do not double count overlapping evidence across databases and papers.
- If conflicts remain unresolved, prefer conservative handling over forced upgrading.
