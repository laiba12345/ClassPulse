from app.real_data import TalkMovesCorpus

def test_official_talkmoves_files_load_with_expected_schema_and_real_rows():
    corpus = TalkMovesCorpus.load()
    assert corpus.teacher.row_count > 1000
    assert corpus.student.row_count > 1000
    assert set(corpus.teacher.columns) == {"text_a", "text_b", "labels"}
    assert corpus.teacher.source == "SumnerLab/TalkMoves"
    assert corpus.license == "CC BY-NC-SA 4.0"

def test_real_data_report_has_distributions_examples_and_honest_limits():
    report = TalkMovesCorpus.load().report()
    assert report["total_rows"] == report["teacher"]["rows"] + report["student"]["rows"]
    assert sum(report["teacher"]["label_distribution"].values()) == report["teacher"]["rows"]
    assert len(report["examples"]) >= 4
    assert report["validation"]["schema_valid"] is True
    assert "not confusion ground truth" in report["limitations"].lower()
