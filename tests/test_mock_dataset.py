from radioml_amc.data.mock_dataset import generate_mock_radioml


def test_mock_dataset_shape():
    x, y, snr, mod_names, snr_values = generate_mock_radioml(
        num_samples=64,
        num_classes=4,
        snr_values=[-6, 0, 6, 12],
        signal_length=128,
        seed=42,
    )
    assert x.shape == (64, 2, 128)
    assert y.shape == (64,)
    assert snr.shape == (64,)
    assert x.dtype.name == "float32"
    assert len(mod_names) == 4
    assert snr_values == [-6, 0, 6, 12]

