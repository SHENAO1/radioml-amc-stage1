import torch

from radioml_amc.models.multiview import MultiViewFusionNet, TimeFrequencyCNN, count_parameters


def test_time_frequency_cnn_forward_shape():
    model = TimeFrequencyCNN(num_classes=4, view="stft")
    x = {"stft": torch.randn(4, 1, 32, 7)}
    y = model(x)
    assert y.shape == (4, 4)
    assert count_parameters(model) > 0


def test_fusion_iq_stft_cwt_forward_shape():
    model = MultiViewFusionNet(num_classes=4, views=["iq", "stft", "cwt"])
    x = {
        "iq": torch.randn(4, 2, 128),
        "stft": torch.randn(4, 1, 32, 7),
        "cwt": torch.randn(4, 1, 8, 128),
    }
    y = model(x)
    assert y.shape == (4, 4)
    assert count_parameters(model) > 0


def test_fusion_iq_amp_phase_forward_shape():
    model = MultiViewFusionNet(num_classes=4, views=["iq", "amp_phase"])
    x = {
        "iq": torch.randn(4, 2, 128),
        "amp_phase": torch.randn(4, 2, 128),
    }
    y = model(x)
    assert y.shape == (4, 4)
    assert count_parameters(model) > 0
