from pathlib import Path

import pytest

from radioml_amc.config import load_config
from radioml_amc.data.dataset import load_data_bundle


def test_rml2016a_loader_if_data_exists():
    root = Path(__file__).resolve().parents[1]
    pkl_path = root / "data" / "raw" / "RML2016.10a_dict.pkl"
    bz2_path = root / "data" / "raw" / "RML2016.10a_dict.pkl.bz2"
    if not pkl_path.exists() and not bz2_path.exists():
        pytest.skip("RadioML2016.10A data file is not present locally.")

    config = load_config(root / "configs" / "stage1_rml2016a.yaml")
    config["data"]["subset_mode"] = True
    config["data"]["max_samples_per_group"] = 5
    bundle = load_data_bundle(config, project_root=root)
    assert bundle.x.ndim == 3
    assert bundle.x.shape[1:] == (2, 128)
    assert bundle.y.shape[0] == bundle.x.shape[0]
    assert bundle.snr.shape[0] == bundle.x.shape[0]

