from pathlib import Path
import importlib.util


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "evidence_router.py"
spec = importlib.util.spec_from_file_location("evidence_router", MODULE_PATH)
evidence_router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence_router)


def test_normalize_clinvar_result_extracts_conflict_and_review_status():
    raw = {
        "variation_id": 12345,
        "clinical_significance": "Conflicting classifications of pathogenicity",
        "review_status": "criteria provided, multiple submitters, no conflicts",
        "germline_classification": {
            "description": "Conflicting classifications of pathogenicity",
            "review_status": "reviewed by expert panel"
        },
        "conditions": ["Developmental and epileptic encephalopathy"],
        "submitter_count": 4,
    }

    normalized = evidence_router.normalize_clinvar_result(raw)

    assert normalized["source"] == "ClinVar"
    assert normalized["has_assertion"] is True
    assert normalized["is_conflicted"] is True
    assert normalized["classification"] == "Conflicting classifications of pathogenicity"
    assert normalized["review_status"] == "reviewed by expert panel"
    assert normalized["condition_terms"] == ["Developmental and epileptic encephalopathy"]


def test_normalize_gnomad_result_flags_absence_and_low_frequency():
    raw = {
        "found": True,
        "variant_id": "1-100-A-G",
        "genome": {
            "af": 0.00002,
            "ac": 1,
            "an": 50000,
            "filters": []
        },
        "exome": None,
    }

    normalized = evidence_router.normalize_gnomad_result(raw)

    assert normalized["source"] == "gnomAD"
    assert normalized["is_absent"] is False
    assert normalized["max_af"] == 0.00002
    assert normalized["is_rare"] is True
    assert normalized["has_filter_flags"] is False


def test_build_candidate_evidence_ledger_generates_population_and_database_rows():
    record = {
        "gene": "SCN2A",
        "transcript": "NM_021007.3",
        "genome_build": "GRCh38",
        "c_hgvs": "c.4765A>G",
        "p_hgvs": "p.Lys1589Glu",
        "variant_type": "missense",
        "phenotype": "developmental and epileptic encephalopathy",
        "family_structure": "trio",
        "parental_genotypes": "proband positive, both unaffected parents negative, parentage not confirmed",
        "clinvar_result": {
            "variation_id": 12345,
            "clinical_significance": "Conflicting classifications of pathogenicity",
            "review_status": "criteria provided, conflicting classifications",
            "conditions": ["Developmental and epileptic encephalopathy"],
        },
        "gnomad_result": {
            "found": False,
            "variant_id": "2-166166210-T-C",
            "genome": None,
            "exome": None,
        },
    }

    ledger = evidence_router.build_candidate_evidence_ledger(record)
    by_code = {row["code"]: row for row in ledger["rows"]}

    assert "PM2" in by_code
    assert by_code["PM2"]["triggered"] == "Candidate"
    assert by_code["PM2"]["source"] == "gnomAD"
    assert "ClinVar_context" in by_code
    assert by_code["ClinVar_context"]["triggered"] == "Context"
    assert ledger["summary_counts"]["candidate_pathogenic"] >= 1


def test_build_router_summary_does_not_escalate_for_empty_unchecked_placeholders():
    record = {
        "gene": "SCN2A",
        "transcript": "NM_021007.3",
        "genome_build": "GRCh38",
        "c_hgvs": "c.1A>G",
        "phenotype": "developmental and epileptic encephalopathy",
        "database_assertions": [],
        "literature_evidence": [],
    }

    summary = evidence_router.build_router_summary(record)

    assert summary["need_literature_deep_dive"] is False
    assert summary["literature_deep_dive_reasons"] == []
    assert summary["source_order"] == ["ClinGen", "ClinVar", "gnomAD"]


def test_build_router_summary_escalates_after_empty_clinvar_check():
    record = {
        "gene": "SCN2A",
        "transcript": "NM_021007.3",
        "genome_build": "GRCh38",
        "c_hgvs": "c.1A>G",
        "phenotype": "developmental and epileptic encephalopathy",
        "clinvar_result": {},
    }

    summary = evidence_router.build_router_summary(record)

    assert summary["need_literature_deep_dive"] is True
    assert "clinvar_absent_or_sparse_after_check" in summary["literature_deep_dive_reasons"]
    assert summary["source_order"] == ["ClinGen", "ClinVar", "gnomAD", "Mastermind", "PubTator3/PubMed"]


def test_build_router_summary_reports_blockers_for_incomplete_record():
    summary = evidence_router.build_router_summary({"gene": "SCN2A"})

    assert summary["variant_identity_complete"] is False
    assert "missing_transcript" in summary["blockers"]
    assert "missing_genome_build" in summary["blockers"]
    assert "missing_hgvs" in summary["blockers"]
    assert "missing_phenotype_context" in summary["blockers"]


def test_high_af_generates_ba1_candidate_row():
    record = {
        "gene": "SCN2A",
        "transcript": "NM_021007.3",
        "genome_build": "GRCh38",
        "c_hgvs": "c.1A>G",
        "phenotype": "developmental and epileptic encephalopathy",
        "ba1_threshold": 0.01,
        "gnomad_result": {
            "found": True,
            "genome": {"af": 0.02, "ac": 20, "an": 1000, "filters": []},
            "exome": None,
        },
    }

    ledger = evidence_router.build_candidate_evidence_ledger(record)
    by_code = {row["code"]: row for row in ledger["rows"]}

    assert "BA1" in by_code
    assert by_code["BA1"]["triggered"] == "Candidate"
    assert by_code["BA1"]["source"] == "gnomAD"
