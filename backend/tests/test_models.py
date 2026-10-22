from __future__ import annotations

import torch

from backend.app.ml.models import get_model, list_models


def test_list_models():
    models = list_models()
    assert len(models) > 20
    assert "resnet18" in models


def test_resnet18_forward():
    m = get_model("resnet18", num_classes=2, in_channels=1)
    m.eval()
    x = torch.randn(2, 1, 64, 64)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (2, 2)


def test_vgg11_forward():
    m = get_model("vgg11", num_classes=2, in_channels=1)
    m.eval()
    x = torch.randn(2, 1, 64, 64)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (2, 2)


def test_mobilenet_forward():
    m = get_model("mobilenet", num_classes=2, in_channels=1)
    m.eval()
    x = torch.randn(2, 1, 64, 64)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (2, 2)


def test_efficientnet_forward():
    m = get_model("efficientnet", num_classes=2, in_channels=1)
    m.eval()
    x = torch.randn(2, 1, 64, 64)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (2, 2)


def test_vit_forward():
    m = get_model("vit", num_classes=2, in_channels=1, img_size=64, patch_size=8)
    m.eval()
    x = torch.randn(2, 1, 64, 64)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (2, 2)


def test_convnext_forward():
    m = get_model("convnext", num_classes=2, in_channels=1)
    m.eval()
    x = torch.randn(2, 1, 64, 64)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (2, 2)


def test_crnn_forward():
    m = get_model("crnn", num_classes=2, in_channels=1)
    m.eval()
    x = torch.randn(2, 1, 64, 64)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (2, 2)


def test_mlp_forward():
    m = get_model("mlp", input_dim=13, num_classes=2)
    m.eval()
    x = torch.randn(4, 13)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (4, 2)


def test_lstm_forward():
    m = get_model("lstm", input_dim=13, num_classes=2)
    m.eval()
    x = torch.randn(4, 10, 13)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (4, 2)


def test_gru_forward():
    m = get_model("gru", input_dim=13, num_classes=2)
    m.eval()
    x = torch.randn(4, 10, 13)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (4, 2)


def test_transformer_cls_forward():
    m = get_model("transformer_cls", input_dim=13, num_classes=2)
    m.eval()
    x = torch.randn(4, 10, 13)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (4, 2)


def test_ft_transformer_forward():
    m = get_model("ft_transformer", input_dim=13, num_classes=2)
    m.eval()
    x = torch.randn(4, 13)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (4, 2)


def test_tabnet_forward():
    m = get_model("tabnet", input_dim=13, num_classes=2)
    m.eval()
    x = torch.randn(4, 13)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (4, 2)


def test_vae_forward():
    from backend.app.ml.models import VAE
    m = VAE(input_dim=13, latent_dim=4)
    m.eval()
    x = torch.randn(4, 13)
    with torch.no_grad():
        recon, mu, logvar = m(x)
    assert recon.shape == (4, 13)


def test_autoencoder_forward():
    from backend.app.ml.models import AutoEncoder
    m = AutoEncoder(input_dim=13, latent_dim=4)
    m.eval()
    x = torch.randn(4, 13)
    with torch.no_grad():
        out = m(x)
    assert out.shape == (4, 13)


def test_gan_forward():
    from backend.app.ml.models import GAN_Discriminator, GAN_Generator
    g = GAN_Generator(latent_dim=8, output_dim=13)
    d = GAN_Discriminator(input_dim=13)
    z = torch.randn(4, 8)
    fake = g(z)
    assert fake.shape == (4, 13)
    out = d(fake)
    assert out.shape == (4, 1)


def test_siamese_forward():
    from backend.app.ml.models import SiameseNetwork
    m = SiameseNetwork(input_dim=13, hidden_dim=8)
    m.eval()
    x1 = torch.randn(4, 13)
    x2 = torch.randn(4, 13)
    with torch.no_grad():
        out = m(x1, x2)
    assert out.shape == (4,)


def test_unknown_model_raises():
    import pytest
    with pytest.raises(ValueError):
        get_model("nonexistent")
