import torch

from radioml_amc.data.dataset import SignalDataset
from radioml_amc.data.mock_dataset import generate_mock_radioml
from radioml_amc.features.time_frequency import compute_amplitude_phase_tensor, compute_cwt_tensor, compute_stft_tensor


def test_stft_tensor_shape():
    sample = torch.randn(2, 128)
    view = compute_stft_tensor(sample, nperseg=32, noverlap=16)
    assert view.ndim == 3
    assert view.shape[0] == 1
    assert view.shape[1] == 32
    assert torch.isfinite(view).all()


def test_cwt_tensor_shape():
    sample = torch.randn(2, 128)
    view = compute_cwt_tensor(sample, num_scales=8, min_scale=1.0, max_scale=24.0)
    assert view.shape == (1, 8, 128)
    assert torch.isfinite(view).all()


def test_amplitude_phase_tensor_shape():
    sample = torch.randn(2, 128)
    view = compute_amplitude_phase_tensor(sample)
    assert view.shape == (2, 128)
    assert torch.isfinite(view).all()


def test_signal_dataset_returns_multiview_dict_on_demand():
    x, y, snr, _, _ = generate_mock_radioml(num_samples=8, num_classes=4, seed=7)
    dataset = SignalDataset(
        x,
        y,
        snr,
        feature_config={
            "views": ["iq", "stft", "cwt"],
            "stft": {"nperseg": 32, "noverlap": 16},
            "cwt": {"num_scales": 8, "min_scale": 1.0, "max_scale": 24.0},
        },
    )
    features, label, snr_value = dataset[0]
    assert set(features) == {"iq", "stft", "cwt"}
    assert features["iq"].shape == (2, 128)
    assert features["stft"].shape[0] == 1
    assert features["cwt"].shape == (1, 8, 128)
    assert int(label) >= 0
    assert int(snr_value) in {-6, 0, 6, 12}


def test_signal_dataset_returns_amp_phase_view_on_demand():
    x, y, snr, _, _ = generate_mock_radioml(num_samples=8, num_classes=4, seed=11)
    dataset = SignalDataset(x, y, snr, feature_config={"views": ["iq", "amp_phase"]})
    features, _, _ = dataset[0]
    assert set(features) == {"iq", "amp_phase"}
    assert features["amp_phase"].shape == (2, 128)
