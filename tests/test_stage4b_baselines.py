import torch

from radioml_amc.models.baselines import MCLDNN, ParameterMatchedIQOnlyNet, count_parameters
from radioml_amc.models.gated_fusion import ScalarGatedIQSTFTFusionNet
from radioml_amc.training.trainer import build_model, model_required_views


def test_mcldnn_forward_shape_and_parameter_count():
    model = MCLDNN(num_classes=4)
    x = torch.randn(3, 2, 128)
    y = model(x)
    assert y.shape == (3, 4)
    assert count_parameters(model) == 405296


def test_iq_param_matched_forward_shape_and_parameter_budget():
    model = ParameterMatchedIQOnlyNet(num_classes=4)
    gated = ScalarGatedIQSTFTFusionNet(num_classes=4)
    x = torch.randn(3, 2, 128)
    y = model(x)
    assert y.shape == (3, 4)
    assert count_parameters(model) == 135492
    ratio = count_parameters(model) / count_parameters(gated)
    assert 0.95 <= ratio <= 1.05


def test_stage4b_model_registry_and_required_views():
    assert model_required_views("mcldnn") == ["iq"]
    assert model_required_views("mcldnn_iq") == ["iq"]
    assert model_required_views("iq_param_matched") == ["iq"]
    assert model_required_views("parameter_matched_iq") == ["iq"]
    assert isinstance(build_model("mcldnn", num_classes=4), MCLDNN)
    assert isinstance(build_model("iq_param_matched", num_classes=4), ParameterMatchedIQOnlyNet)
