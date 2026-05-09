import pytest
import torch

from radioml_amc.models.baselines import LWAMCNet, count_parameters
from radioml_amc.training.trainer import build_model, model_required_views


def test_lwamcnet_forward_shape_and_parameter_count():
    model = LWAMCNet(num_classes=4)
    x = torch.randn(3, 2, 128)
    y = model(x)
    assert y.shape == (3, 4)
    assert count_parameters(model) == 20164


def test_lwamcnet_rejects_unexpected_signal_length():
    model = LWAMCNet(num_classes=4)
    with pytest.raises(ValueError, match="signal length 128"):
        model(torch.randn(3, 2, 64))


def test_stage4c_model_registry_and_required_views():
    assert model_required_views("lwamcnet") == ["iq"]
    assert model_required_views("lwamcnet_iq") == ["iq"]
    assert model_required_views("lw_amc_net") == ["iq"]
    assert model_required_views("lightweight_amc") == ["iq"]
    assert isinstance(build_model("lwamcnet", num_classes=4), LWAMCNet)
    assert isinstance(build_model("lwamcnet_iq", num_classes=4), LWAMCNet)
