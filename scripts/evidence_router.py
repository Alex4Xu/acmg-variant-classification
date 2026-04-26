import json
import sys
from pathlib import Path


# SVI note: several criteria now have variable strength (see ClinGen SVI recommendations).
# The "default" column below reflects the 2015 original; actual applied strength depends on
# SVI updates, VCEP specifications, and case-specific evidence. Use the CALIBRATED_TOOLS
# and POINT_BASED_CRITERIA tables below for evidence-level guidance.

LEDGER_TEMPLATE = [
    ("PVS1", "Very Strong"),       # Variable: decision tree (VS/Strong/Moderate/Supporting)
    ("PS1", "Strong"),
    ("PS2", "Strong"),             # Point-based scoring (SVI v1.1): can be Supporting→Very Strong
    ("PS3", "Strong"),             # Variable: capped at Moderate without validated assay (SVI 2024)
    ("PS4", "Strong"),             # Point-based scoring: can be Supporting→Strong
    ("PM1", "Moderate"),
    ("PM2", "Supporting"),         # CRITICAL SVI 2020: default DOWNGRADED from Moderate to Supporting
    ("PM3", "Moderate"),           # Variable: Supporting/Moderate/Strong (SVI v1.0)
    ("PM4", "Moderate"),
    ("PM5", "Moderate"),
    ("PM6", "Moderate"),           # Point-based scoring (SVI v1.1): can be Supporting→Strong
    ("PP1", "Supporting"),         # Variable: Bayesian LOD (Supporting→Very Strong)
    ("PP2", "Supporting"),
    ("PP3", "Supporting"),         # Calibrated individual tools (Pejaver 2022/2024)
    ("PP4", "Supporting"),
    ("BA1", "Stand-alone"),        # Disease-specific threshold (SVI 2018), NOT flat 5%
    ("BS1", "Strong"),
    ("BS2", "Strong"),             # Point-based scoring for healthy observations
    ("BS3", "Strong"),
    ("BS4", "Strong"),             # Variable: Bayesian LOD (Supporting→Very Strong)
    ("BP1", "Supporting"),
    ("BP2", "Supporting"),         # Point-based scoring
    ("BP3", "Supporting"),
    ("BP4", "Supporting"),         # Calibrated individual tools (Pejaver 2022/2024)
    ("BP5", "Supporting"),         # Point-based scoring
    ("BP7", "Supporting"),
]

# PP3/BP4 calibrated individual tool thresholds (Pejaver 2022, 2024)
# Use ONE calibrated tool — no need for consensus across multiple tools.
# If a VCEP specifies its own thresholds, those override these defaults.
CALIBRATED_TOOLS = {
    "REVEL": {
        "pp3": {"Supporting": 0.700, "Strong": 0.889},
        "bp4": {"Supporting": 0.300, "Strong": 0.183},
    },
    "BayesDel_addAF": {
        "pp3": {"Supporting": 0.340, "Strong": 0.590},
        "bp4": {"Supporting": -0.360, "Strong": -0.610},
    },
    "BayesDel_noAF": {
        "pp3": {"Supporting": 0.210, "Strong": 0.490},
        "bp4": {"Supporting": -0.250, "Strong": -0.480},
    },
    "CADD": {
        "pp3": {"Supporting": 25.3, "Strong": 28.5},
        "bp4": {"Supporting": 22.7, "Strong": 12.6},
    },
    "AlphaMissense": {
        "pp3": {"Supporting": 0.850},
        "bp4": {"Supporting": 0.100},
    },
    "PrimateAI": {
        "pp3": {"Supporting": 0.800, "Strong": 0.930},
        "bp4": {"Supporting": 0.200},
    },
}

# Criteria using point-based scoring (ClinGen SVI v1.1 and VCEP adaptations)
# Instead of binary yes/no, points are summed and mapped to strength levels.
POINT_BASED_CRITERIA = {
    "PS2/PM6": {
        "description": "De novo evidence",
        "scoring": [
            ("Consistent phenotype + confirmed parentage", 2.0),
            ("Consistent phenotype + assumed parentage", 1.0),
            ("Limited phenotype + confirmed parentage", 1.0),
            ("Limited phenotype + assumed parentage", 0.5),
            ("Non-consistent phenotype", 0.0),
        ],
        "strength_map": [
            (6.0, "Very Strong"),
            (4.0, "Strong"),
            (2.0, "Moderate"),
            (0.0, "Supporting"),
        ],
        "note": "Prenatal cases always count as 'limited phenotype'",
    },
    "PS4": {
        "description": "Case observation / prevalence",
        "scoring": [
            ("Consistent phenotype", 1.0),
            ("Limited phenotype", 0.5),
            ("Non-consistent disorder", -1.0),
        ],
        "strength_map": [
            (4.0, "Very Strong"),
            (2.0, "Strong"),
            (1.0, "Moderate"),
            (0.0, "Supporting"),
        ],
        "note": "Check VCEP specifications for disorder-specific point thresholds",
    },
    "BS2": {
        "description": "Healthy observation",
        "scoring": [
            ("Confirmed healthy adult with consistent phenotype data", 2.0),
            ("Observed healthy without detailed phenotypic confirmation", 1.0),
        ],
        "strength_map": [
            (4.0, "Very Strong"),
            (2.0, "Strong"),
            (1.0, "Moderate"),
            (0.0, "Supporting"),
        ],
        "note": "Requires phenotypic context to avoid counting carriers as healthy",
    },
    "BP2/BP5": {
        "description": "Alternate diagnosis / trans configuration",
        "scoring": [
            ("Alternate molecular basis confirmed", 2.0),
            ("Alternate basis probable but not confirmed", 1.0),
        ],
        "strength_map": [
            (2.0, "Moderate"),
            (1.0, "Supporting"),
        ],
        "note": "Can combine additively across BP2 and BP5 observations",
    },
}

# BA1/BS1 population frequency thresholds — disease-specific, NOT flat 5%.
# The generic_fallback below is a safety net only; always prefer disease-specific
# thresholds from ClinGen BA1/BS1 calculator or VCEP specifications.
# https://clinicalgenome.org/tools/calculator-af/
GENERIC_BA1_FALLBACK = 0.05   # 5% — use ONLY when no disease-specific data exists
GENERIC_BS1_FALLBACK = 0.01   # 1% — use ONLY when no disease-specific data exists


def first_nonempty(record, *keys):
    for key in keys:
        value = record.get(key)
        if value not in (None, "", [], {}):
            return value
    return None



def looks_true(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "present", "confirmed"}
    return bool(value)



def normalize_list(value):
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value).strip()]



def as_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None



def source_checked(record: dict, source_name: str, result_key: str | None = None) -> bool:
    explicit_key = f"{source_name.lower()}_has_been_checked"
    checked_key = f"{source_name.lower()}_checked"
    if explicit_key in record:
        return looks_true(record.get(explicit_key))
    if checked_key in record:
        return looks_true(record.get(checked_key))
    return result_key is not None and record.get(result_key) is not None



def literature_deep_dive_reasons(record: dict, context: dict, clinvar: dict | None = None) -> list[str]:
    """Return literature escalation reasons after upstream source status is known.

    Empty intake placeholders should not trigger a deep dive by themselves. Use explicit
    *_checked flags, normalized ClinVar results, or source-verification flags to separate
    "not yet searched" from "searched but absent/sparse/conflicting".
    """
    reasons = []
    if not context.get("phenotype_present"):
        reasons.append("phenotype_context_missing")

    if clinvar is not None:
        if clinvar.get("is_conflicted"):
            reasons.append("clinvar_conflict_flagged")
        if not clinvar.get("has_assertion") and source_checked(record, "clinvar", "clinvar_result"):
            reasons.append("clinvar_absent_or_sparse_after_check")
    elif looks_true(record.get("clinvar_conflict")):
        reasons.append("clinvar_conflict_flagged")

    if source_checked(record, "database_assertions") and not normalize_list(record.get("database_assertions")):
        reasons.append("database_assertions_checked_but_empty")
    if source_checked(record, "literature_evidence") and not normalize_list(record.get("literature_evidence")):
        reasons.append("literature_checked_but_empty")

    if looks_true(record.get("functional_claim_needs_verification")):
        reasons.append("functional_claim_needs_source_check")
    if looks_true(record.get("de_novo_claim_needs_verification")):
        reasons.append("de_novo_claim_needs_source_check")
    if looks_true(record.get("nearby_variant_reasoning")):
        reasons.append("nearby_variant_or_regional_evidence_in_play")

    deduped = []
    for reason in reasons:
        if reason not in deduped:
            deduped.append(reason)
    return deduped



def summarize_variant_context(record: dict) -> dict:
    gene = first_nonempty(record, "gene")
    transcript = first_nonempty(record, "transcript")
    genome_build = first_nonempty(record, "genome_build", "build", "reference_genome")
    c_hgvs = first_nonempty(record, "c_hgvs", "c.HGVS")
    p_hgvs = first_nonempty(record, "p_hgvs", "p.HGVS")
    variant_type = first_nonempty(record, "variant_type")
    phenotype = first_nonempty(record, "phenotype", "disease_context", "suspected_diagnosis")
    inheritance_model = first_nonempty(record, "inheritance_model")
    family_structure = first_nonempty(record, "family_structure")
    parental_genotypes = first_nonempty(record, "parental_genotypes")
    functional_evidence = first_nonempty(record, "functional_evidence")
    database_assertions = first_nonempty(record, "database_assertions")
    literature_evidence = first_nonempty(record, "literature_evidence")

    variant_identity_complete = bool(gene and genome_build and transcript and (c_hgvs or p_hgvs))
    phenotype_present = bool(phenotype)
    family_present = bool(family_structure or parental_genotypes or inheritance_model)

    blockers = []
    if not gene:
        blockers.append("missing_gene")
    if not transcript:
        blockers.append("missing_transcript")
    if not genome_build:
        blockers.append("missing_genome_build")
    if not (c_hgvs or p_hgvs):
        blockers.append("missing_hgvs")
    if not phenotype_present:
        blockers.append("missing_phenotype_context")

    source_order = ["ClinGen", "ClinVar", "gnomAD"]

    base_context = {"phenotype_present": phenotype_present}
    literature_reasons = literature_deep_dive_reasons(record, base_context)

    need_literature_deep_dive = len(literature_reasons) > 0
    if need_literature_deep_dive:
        source_order.extend(["Mastermind", "PubTator3/PubMed"])

    source_roles = {
        "ClinGen": "rule_override_and_disease_mechanism",
        "ClinVar": "database_assertion_context",
        "gnomAD": "population_frequency",
    }
    if need_literature_deep_dive:
        source_roles["Mastermind"] = "variant_level_literature_deep_dive"
        source_roles["PubTator3/PubMed"] = "entity_guided_primary_literature_review"

    candidate_criteria = []
    if variant_identity_complete:
        candidate_criteria.extend(["PM2/BA1/BS1", "ClinVar_context"])
    if phenotype_present:
        candidate_criteria.append("PP4")
    if family_present:
        candidate_criteria.extend(["PS2/PM6", "PP1/BS4"])
    if functional_evidence not in (None, "", [], {}):
        candidate_criteria.extend(["PS3/BS3"])
    if variant_type:
        lowered = str(variant_type).lower()
        if lowered in {"nonsense", "frameshift", "splice", "canonical_splice", "lof"}:
            candidate_criteria.append("PVS1_review")
        if "in-frame" in lowered or "dup" in lowered or "del" in lowered:
            candidate_criteria.extend(["PM1", "PM4"])

    notes = [
        "Outside platforms supply evidence; they do not replace the local ACMG evidence ledger.",
        "Check ClinGen before generic ACMG application whenever gene-specific guidance may exist.",
        "Check gnomAD before using PM2 / BA1 / BS1.",
        "If literature escalation occurs, record exact source-level caveats instead of copying platform conclusions.",
    ]

    return {
        "gene": gene,
        "transcript": transcript,
        "genome_build": genome_build,
        "c_hgvs": c_hgvs,
        "p_hgvs": p_hgvs,
        "variant_type": variant_type,
        "phenotype": phenotype,
        "inheritance_model": inheritance_model,
        "family_structure": family_structure,
        "parental_genotypes": parental_genotypes,
        "variant_identity_complete": variant_identity_complete,
        "phenotype_present": phenotype_present,
        "family_context_present": family_present,
        "enable_external_routing": variant_identity_complete,
        "blockers": blockers,
        "source_order": source_order,
        "source_roles": source_roles,
        "need_literature_deep_dive": need_literature_deep_dive,
        "literature_deep_dive_reasons": literature_reasons,
        "candidate_criteria_needing_external_support": sorted(set(candidate_criteria)),
        "notes": notes,
    }



def normalize_condition_terms(raw):
    terms = []
    for item in normalize_list(raw):
        if item:
            terms.append(item)
    return terms



def normalize_clinvar_result(raw: dict | None) -> dict:
    raw = raw or {}
    germline = raw.get("germline_classification") or {}
    classification = first_nonempty(
        germline,
        "description",
        "clinical_significance_description",
    ) or first_nonempty(raw, "clinical_significance", "classification")
    review_status = first_nonempty(germline, "review_status") or first_nonempty(raw, "review_status")
    condition_terms = []
    conditions = raw.get("conditions")
    if isinstance(conditions, list):
        for condition in conditions:
            if isinstance(condition, dict):
                term = first_nonempty(condition, "name", "term", "display_name")
            else:
                term = str(condition).strip()
            if term:
                condition_terms.append(term)
    elif conditions:
        condition_terms.extend(normalize_condition_terms(conditions))

    conflict_markers = [
        classification,
        review_status,
        raw.get("interpretation_conflict"),
        raw.get("conflicting_classifications"),
    ]
    conflict_text = " ".join(str(v) for v in conflict_markers if v not in (None, "", False))
    is_conflicted = "conflict" in conflict_text.lower()

    return {
        "source": "ClinVar",
        "variation_id": first_nonempty(raw, "variation_id", "id", "accession"),
        "has_assertion": bool(classification or review_status or condition_terms),
        "classification": classification,
        "review_status": review_status,
        "is_conflicted": is_conflicted,
        "condition_terms": condition_terms,
        "submitter_count": raw.get("submitter_count"),
        "raw": raw,
    }



def _collect_population_stats(raw: dict) -> list[dict]:
    populations = []
    for dataset_name in ("genome", "exome"):
        dataset = raw.get(dataset_name)
        if not dataset:
            continue
        af = as_float(first_nonempty(dataset, "af", "AF"))
        ac = first_nonempty(dataset, "ac", "AC")
        an = first_nonempty(dataset, "an", "AN")
        filters = dataset.get("filters") or dataset.get("filter") or []
        if isinstance(filters, str):
            filters = [filters]
        populations.append(
            {
                "dataset": dataset_name,
                "af": af,
                "ac": ac,
                "an": an,
                "filters": filters,
            }
        )
    return populations



def normalize_gnomad_result(raw: dict | None) -> dict:
    raw = raw or {}
    populations = _collect_population_stats(raw)
    af_values = [p["af"] for p in populations if p["af"] is not None]
    max_af = max(af_values) if af_values else None
    filters = [f for p in populations for f in p["filters"] if f not in (None, "", "PASS")]
    found_flag = raw.get("found")
    found = bool(populations) if found_flag is None else bool(found_flag)
    is_absent = not found or len(populations) == 0
    is_rare = (max_af is not None and max_af < 0.0001) or is_absent

    return {
        "source": "gnomAD",
        "variant_id": first_nonempty(raw, "variant_id", "variantId"),
        "found": found,
        "is_absent": is_absent,
        "population_stats": populations,
        "max_af": max_af,
        "is_rare": is_rare,
        "has_filter_flags": len(filters) > 0,
        "filter_flags": filters,
        "raw": raw,
    }



def empty_ledger_rows():
    rows = []
    for code, strength in LEDGER_TEMPLATE:
        rows.append(
            {
                "code": code,
                "strength": strength,
                "triggered": "No",
                "reason": "",
                "source": "",
                "caveat": "",
            }
        )
    return rows



def add_or_replace_row(rows: list[dict], code: str, strength: str, triggered: str, reason: str, source: str, caveat: str = ""):
    for row in rows:
        if row["code"] == code:
            row.update(
                {
                    "strength": strength,
                    "triggered": triggered,
                    "reason": reason,
                    "source": source,
                    "caveat": caveat,
                }
            )
            return
    rows.append(
        {
            "code": code,
            "strength": strength,
            "triggered": triggered,
            "reason": reason,
            "source": source,
            "caveat": caveat,
        }
    )



def summarize_counts(rows: list[dict]) -> dict:
    summary = {
        "candidate_pathogenic": 0,
        "candidate_benign": 0,
        "context_rows": 0,
    }
    for row in rows:
        if row["triggered"] == "Candidate":
            if row["code"].startswith(("P",)):
                summary["candidate_pathogenic"] += 1
            elif row["code"].startswith(("B",)):
                summary["candidate_benign"] += 1
        elif row["triggered"] == "Context":
            summary["context_rows"] += 1
    return summary



def build_candidate_evidence_ledger(record: dict) -> dict:
    context = summarize_variant_context(record)
    clinvar = normalize_clinvar_result(record.get("clinvar_result"))
    gnomad = normalize_gnomad_result(record.get("gnomad_result"))
    rows = empty_ledger_rows()

    if clinvar["has_assertion"]:
        reason = clinvar["classification"] or "ClinVar assertion present"
        caveat_parts = []
        if clinvar["review_status"]:
            caveat_parts.append(f"review_status={clinvar['review_status']}")
        if clinvar["is_conflicted"]:
            caveat_parts.append("assertions_are_conflicted")
        add_or_replace_row(
            rows,
            code="ClinVar_context",
            strength="Context",
            triggered="Context",
            reason=reason,
            source="ClinVar",
            caveat="; ".join(caveat_parts),
        )

    if gnomad["is_absent"]:
        add_or_replace_row(
            rows,
            code="PM2",
            strength="Supporting",  # SVI 2020: PM2 defaults to Supporting, not Moderate
            triggered="Candidate",
            reason="Variant absent from supplied gnomAD result.",
            source="gnomAD",
            caveat="SVI 2020: PM2 defaults to Supporting strength. Some VCEPs may specify Moderate if disease context supports it; check ClinGen VCEP specifications.",
        )
    elif gnomad["max_af"] is not None:
        # BA1/BS1 thresholds are disease-specific (SVI 2018), NOT flat 5%/1%.
        # Use GENERIC_BA1_FALLBACK and GENERIC_BS1_FALLBACK only when no
        # disease-specific thresholds are available from ClinGen calculator or VCEP.
        # ClinGen AF calculator: https://clinicalgenome.org/tools/calculator-af/
        ba1_threshold = record.get("ba1_threshold") or GENERIC_BA1_FALLBACK
        bs1_threshold = record.get("bs1_threshold") or GENERIC_BS1_FALLBACK

        if gnomad["max_af"] >= ba1_threshold:
            add_or_replace_row(
                rows,
                code="BA1",
                strength="Stand-alone",
                triggered="Candidate",
                reason=f"Supplied gnomAD max AF is {gnomad['max_af']:.6g} (BA1 threshold: {ba1_threshold:.4g}).",
                source="gnomAD",
                caveat="BA1 threshold is disease-specific (SVI 2018). This uses ba1_threshold from record or generic fallback. Confirm with ClinGen BA1/BS1 calculator. Check BA1/BS1 exception list.",
            )
        elif gnomad["max_af"] >= bs1_threshold:
            add_or_replace_row(
                rows,
                code="BS1",
                strength="Strong",
                triggered="Candidate",
                reason=f"Supplied gnomAD max AF is {gnomad['max_af']:.6g} (BS1 threshold: {bs1_threshold:.4g}).",
                source="gnomAD",
                caveat="BS1 threshold is disease-specific (SVI 2018). This uses bs1_threshold from record or generic fallback. Confirm with ClinGen calculator. Check disease prevalence and penetrance.",
            )
        elif gnomad["is_rare"]:
            # is_rare uses a conservative 0.01% heuristic only to surface a PM2
            # candidate row. Final PM2 application must use disease-specific maximum
            # credible allele frequency from ClinGen calculator or VCEP guidance.
            add_or_replace_row(
                rows,
                code="PM2",
                strength="Supporting",  # SVI 2020: PM2 defaults to Supporting
                triggered="Candidate",
                reason=f"Supplied gnomAD max AF is rare ({gnomad['max_af']:.6g}).",
                source="gnomAD",
                caveat="Pre-screen only: the router's rare heuristic is max AF <0.01% or absent. Final PM2 requires disease-specific maximum credible allele frequency from ClinGen calculator or VCEP guidance. SVI 2020: PM2 defaults to Supporting; some VCEPs may permit Moderate with additional justification.",
            )

    if context["phenotype_present"]:
        add_or_replace_row(
            rows,
            code="PP4",
            strength="Supporting",
            triggered="Candidate",
            reason="Phenotype context is present and should be checked for gene consistency.",
            source="local_case_context",
            caveat="Requires phenotype specificity review; do not trigger from vague symptom overlap alone.",
        )

    if context["family_context_present"]:
        add_or_replace_row(
            rows,
            code="PS2/PM6",
            strength="Review",
            triggered="Candidate",
            reason="Family / parental genotype context is present for de novo review.",
            source="local_case_context",
            caveat="SVI v1.1: Use point-based scoring (phenotype consistency + parentage status + observation count). Strength ranges from Supporting to Very Strong. See POINT_BASED_CRITERIA['PS2/PM6'] for scoring table. PS2 requires confirmed parentage (genetic testing); trio-WES without biochemical confirmation = PM6.",
        )

    return {
        "context": {
            "gene": context["gene"],
            "transcript": context["transcript"],
            "genome_build": context["genome_build"],
            "c_hgvs": context["c_hgvs"],
            "p_hgvs": context["p_hgvs"],
            "variant_type": context["variant_type"],
        },
        "normalized_sources": {
            "clinvar": clinvar,
            "gnomad": gnomad,
        },
        "rows": [row for row in rows if row["triggered"] != "No"],
        "summary_counts": summarize_counts(rows),
        "notes": [
            "This is a candidate ledger draft, not a final ACMG classification.",
            "Convert candidate rows into final criteria only after expert review and de-duplication.",
        ],
    }



def build_router_summary(record: dict) -> dict:
    context = summarize_variant_context(record)
    clinvar = normalize_clinvar_result(record.get("clinvar_result"))
    gnomad = normalize_gnomad_result(record.get("gnomad_result"))

    literature_reasons = literature_deep_dive_reasons(record, context, clinvar)

    source_order = ["ClinGen", "ClinVar", "gnomAD"]
    need_literature_deep_dive = len(literature_reasons) > 0
    if need_literature_deep_dive:
        source_order.extend(["Mastermind", "PubTator3/PubMed"])

    source_roles = {
        "ClinGen": "rule_override_and_disease_mechanism",
        "ClinVar": "database_assertion_context",
        "gnomAD": "population_frequency",
    }
    if need_literature_deep_dive:
        source_roles["Mastermind"] = "variant_level_literature_deep_dive"
        source_roles["PubTator3/PubMed"] = "entity_guided_primary_literature_review"

    notes = list(context["notes"])
    if clinvar["has_assertion"]:
        notes.append("ClinVar results should be recorded locally with review status and conflict state, never copied blindly.")
    if gnomad["max_af"] is not None or gnomad["is_absent"]:
        notes.append("gnomAD population evidence should be translated into candidate PM2 / BA1 / BS1 rows with disease-context caveats.")

    return {
        "variant_identity_complete": context["variant_identity_complete"],
        "phenotype_present": context["phenotype_present"],
        "family_context_present": context["family_context_present"],
        "enable_external_routing": context["enable_external_routing"],
        "blockers": context["blockers"],
        "source_order": source_order,
        "source_roles": source_roles,
        "need_literature_deep_dive": need_literature_deep_dive,
        "literature_deep_dive_reasons": literature_reasons,
        "candidate_criteria_needing_external_support": context["candidate_criteria_needing_external_support"],
        "normalized_source_snapshots": {
            "clinvar": {
                "has_assertion": clinvar["has_assertion"],
                "classification": clinvar["classification"],
                "review_status": clinvar["review_status"],
                "is_conflicted": clinvar["is_conflicted"],
            },
            "gnomad": {
                "found": gnomad["found"],
                "is_absent": gnomad["is_absent"],
                "max_af": gnomad["max_af"],
                "has_filter_flags": gnomad["has_filter_flags"],
            },
        },
        "notes": notes,
    }



def build_full_report(record: dict) -> dict:
    return {
        "router_summary": build_router_summary(record),
        "candidate_evidence_ledger": build_candidate_evidence_ledger(record),
    }



def load_record(path_arg=None) -> dict:
    if path_arg:
        return json.loads(Path(path_arg).read_text())
    raw = sys.stdin.read().strip()
    if not raw:
        raise SystemExit("Provide a JSON file path or JSON on stdin")
    return json.loads(raw)


if __name__ == "__main__":
    path_arg = sys.argv[1] if len(sys.argv) > 1 else None
    record = load_record(path_arg)
    print(json.dumps(build_full_report(record), ensure_ascii=False, indent=2))
