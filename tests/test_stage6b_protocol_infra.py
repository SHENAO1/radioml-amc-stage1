import pytest

from radioml_amc.data.dataset import DataBundle
from radioml_amc.data.mock_dataset import generate_mock_radioml
from radioml_amc.training.trainer import _prepare_run, _resolve_evidence_tag


def _mock_bundle() -> DataBundle:
    x, y, snr, mod_names, snr_values = generate_mock_radioml(num_samples=32, num_classes=4, seed=13)
    return DataBundle(
        x=x,
        y=y,
        snr=snr,
        mod_names=mod_names,
        snr_values=snr_values,
        mode="mock",
        metadata={},
    )


def test_stage6b_evidence_tag_prefers_configured_label():
    config = {"evidence": {"tag": "diagnostic"}}

    assert _resolve_evidence_tag(config, _mock_bundle()) == "DIAGNOSTIC"


def test_stage6b_mock_defaults_to_smoke_test_label():
    assert _resolve_evidence_tag({}, _mock_bundle()) == "SMOKE TEST"


def test_stage6b_diagnostic_refuses_stage5_result_root(tmp_path):
    config = {
        "project": {"stage": "paper_stage6b"},
        "outputs": {"run_root": "results/paper_stage2/rml2016a/stage6b_diagnostic"},
        "train": {"model": "cnn1d"},
    }

    with pytest.raises(ValueError, match="protected result root"):
        _prepare_run(config, "cnn1d", project_root=tmp_path, evidence_tag="DIAGNOSTIC")
