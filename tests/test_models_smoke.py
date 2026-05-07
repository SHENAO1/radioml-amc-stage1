import torch

from radioml_amc.models.cnn1d import CNN1D, count_parameters as count_cnn_parameters
from radioml_amc.models.resnet1d import ResNet1D, count_parameters as count_resnet_parameters


def test_cnn1d_forward_shape():
    model = CNN1D(num_classes=4)
    x = torch.randn(4, 2, 128)
    y = model(x)
    assert y.shape == (4, 4)
    assert count_cnn_parameters(model) > 0


def test_resnet1d_forward_shape():
    model = ResNet1D(num_classes=4)
    x = torch.randn(4, 2, 128)
    y = model(x)
    assert y.shape == (4, 4)
    assert count_resnet_parameters(model) > 0

