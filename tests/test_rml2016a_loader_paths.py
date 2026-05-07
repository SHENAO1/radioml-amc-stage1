import bz2
import pickle
import shutil
import uuid
from pathlib import Path

import numpy as np
import pytest

from radioml_amc.data.rml2016a_loader import RadioML2016AMissingError, find_rml2016a_file, load_rml2016a


def _repo_tmp() -> Path:
    root = Path(__file__).resolve().parents[1]
    path = root / ".pytest_tmp" / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    return path


def _write_rml_pickle(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        ("BPSK", -2): np.zeros((3, 2, 128), dtype=np.float32),
        ("QPSK", 0): np.ones((3, 2, 128), dtype=np.float32),
    }
    if path.suffix == ".bz2":
        with bz2.BZ2File(path, "wb") as f:
            pickle.dump(payload, f)
    else:
        with path.open("wb") as f:
            pickle.dump(payload, f)


def test_auto_path_detection_supports_nested_bz2():
    tmp_path = _repo_tmp()
    try:
        data_path = tmp_path / "data" / "raw" / "radioml2016" / "RML2016.10a_dict.pkl.bz2"
        _write_rml_pickle(data_path)

        found = find_rml2016a_file(raw_path="auto", project_root=tmp_path)
        assert found == data_path

        x, y, snr, mod_names, snr_values, metadata = load_rml2016a(raw_path="auto", project_root=tmp_path)
        assert x.shape == (6, 2, 128)
        assert y.shape == (6,)
        assert snr.shape == (6,)
        assert mod_names == ["BPSK", "QPSK"]
        assert snr_values == [-2, 0]
        assert metadata["source_path"] == str(data_path)
        assert metadata["has_nan"] is False
        assert metadata["has_inf"] is False
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_missing_real_data_error_lists_expected_paths():
    tmp_path = _repo_tmp()
    try:
        with pytest.raises(RadioML2016AMissingError) as exc_info:
            find_rml2016a_file(raw_path="auto", project_root=tmp_path)
        message = str(exc_info.value)
        assert "RadioML2016.10A" in message
        assert "data" in message
        assert "RML2016.10a_dict.pkl" in message
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
