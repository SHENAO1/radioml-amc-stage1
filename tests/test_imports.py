def test_core_imports():
    import radioml_amc
    from radioml_amc.data.dataset import DataBundle, SignalDataset
    from radioml_amc.models.cnn1d import CNN1D
    from radioml_amc.models.resnet1d import ResNet1D
    from radioml_amc.training.trainer import run_training

    assert radioml_amc.__version__
    assert DataBundle
    assert SignalDataset
    assert CNN1D
    assert ResNet1D
    assert run_training

