import torch

from radioml_amc.models.baselines import CLDNN, count_parameters
from radioml_amc.training.trainer import build_model, model_required_views


def test_cldnn_forward_shape_and_parameter_count():
    model = CLDNN(num_classes=4)
    x = torch.randn(3, 2, 128)
    y = model(x)
    assert y.shape == (3, 4)
    assert count_parameters(model) == 240772


def test_cldnn_accepts_mapping_input():
    model = CLDNN(num_classes=4)
    y = model({"iq": torch.randn(2, 2, 128)})
    assert y.shape == (2, 4)


def test_stage4d_model_registry_and_required_views():
    assert model_required_views("cldnn") == ["iq"]
    assert model_required_views("cldnn_iq") == ["iq"]
    assert model_required_views("cnn_lstm") == ["iq"]
    assert model_required_views("cnn_lstm_iq") == ["iq"]
    assert model_required_views("iq_cldnn") == ["iq"]
    assert isinstance(build_model("cldnn", num_classes=4), CLDNN)
    assert isinstance(build_model("cnn_lstm", num_classes=4), CLDNN)
