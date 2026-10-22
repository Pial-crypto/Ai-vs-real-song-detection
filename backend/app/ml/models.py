"""Neural network model architectures for audio classification."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_channels, out_channels, stride=1, downsample=None):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        identity = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        if self.downsample is not None:
            identity = self.downsample(x)
        out += identity
        return F.relu(out)


class ResNet(nn.Module):
    def __init__(self, block, layers, num_classes=2, in_channels=1):
        super().__init__()
        self.in_channels = 64
        self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * block.expansion, num_classes)

    def _make_layer(self, block, out_channels, blocks, stride=1):
        downsample = None
        if stride != 1 or self.in_channels != out_channels * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.in_channels, out_channels * block.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels * block.expansion),
            )
        layers = [block(self.in_channels, out_channels, stride, downsample)]
        self.in_channels = out_channels * block.expansion
        for _ in range(1, blocks):
            layers.append(block(self.in_channels, out_channels))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


def resnet18(num_classes=2, in_channels=1):
    return ResNet(BasicBlock, [2, 2, 2, 2], num_classes=num_classes, in_channels=in_channels)


def resnet34(num_classes=2, in_channels=1):
    return ResNet(BasicBlock, [3, 4, 6, 3], num_classes=num_classes, in_channels=in_channels)


class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, in_channels, out_channels, stride=1, downsample=None):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.conv3 = nn.Conv2d(out_channels, out_channels * self.expansion, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(out_channels * self.expansion)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        identity = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = F.relu(self.bn2(self.conv2(out)))
        out = self.bn3(self.conv3(out))
        if self.downsample is not None:
            identity = self.downsample(x)
        out += identity
        return F.relu(out)


class ResNetDeep(nn.Module):
    def __init__(self, block, layers, num_classes=2, in_channels=1):
        super().__init__()
        self.in_channels = 64
        self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * block.expansion, num_classes)

    def _make_layer(self, block, out_channels, blocks, stride=1):
        downsample = None
        if stride != 1 or self.in_channels != out_channels * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.in_channels, out_channels * block.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels * block.expansion),
            )
        layers = [block(self.in_channels, out_channels, stride, downsample)]
        self.in_channels = out_channels * block.expansion
        for _ in range(1, blocks):
            layers.append(block(self.in_channels, out_channels))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


def resnet50(num_classes=2, in_channels=1):
    return ResNetDeep(Bottleneck, [3, 4, 6, 3], num_classes=num_classes, in_channels=in_channels)


class VGGBlock(nn.Module):
    def __init__(self, in_channels, out_channels, num_convs):
        super().__init__()
        layers = []
        for i in range(num_convs):
            layers.append(nn.Conv2d(in_channels if i == 0 else out_channels, out_channels, kernel_size=3, padding=1))
            layers.append(nn.ReLU(inplace=True))
        layers.append(nn.MaxPool2d(kernel_size=2, stride=2))
        self.block = nn.Sequential(*layers)

    def forward(self, x):
        return self.block(x)


class VGG(nn.Module):
    def __init__(self, arch, num_classes=2, in_channels=1):
        super().__init__()
        layers = []
        in_c = in_channels
        for (num_convs, out_c) in arch:
            layers.append(VGGBlock(in_c, out_c, num_convs))
            in_c = out_c
        self.features = nn.Sequential(*layers)
        self.avgpool = nn.AdaptiveAvgPool2d((7, 7))
        self.classifier = nn.Sequential(
            nn.Linear(in_c * 7 * 7, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        return self.classifier(x)


def vgg11(num_classes=2, in_channels=1):
    arch = [(1, 64), (1, 128), (2, 256), (2, 512), (2, 512)]
    return VGG(arch, num_classes=num_classes, in_channels=in_channels)


def vgg13(num_classes=2, in_channels=1):
    arch = [(2, 64), (2, 128), (2, 256), (2, 512), (2, 512)]
    return VGG(arch, num_classes=num_classes, in_channels=in_channels)


class InceptionModule(nn.Module):
    def __init__(self, in_channels, out_1x1, red_3x3, out_3x3, red_5x5, out_5x5, out_pool):
        super().__init__()
        self.branch1 = nn.Sequential(nn.Conv2d(in_channels, out_1x1, kernel_size=1), nn.ReLU(inplace=True))
        self.branch2 = nn.Sequential(
            nn.Conv2d(in_channels, red_3x3, kernel_size=1), nn.ReLU(inplace=True),
            nn.Conv2d(red_3x3, out_3x3, kernel_size=3, padding=1), nn.ReLU(inplace=True),
        )
        self.branch3 = nn.Sequential(
            nn.Conv2d(in_channels, red_5x5, kernel_size=1), nn.ReLU(inplace=True),
            nn.Conv2d(red_5x5, out_5x5, kernel_size=5, padding=2), nn.ReLU(inplace=True),
        )
        self.branch4 = nn.Sequential(
            nn.MaxPool2d(kernel_size=3, stride=1, padding=1),
            nn.Conv2d(in_channels, out_pool, kernel_size=1), nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return torch.cat([self.branch1(x), self.branch2(x), self.branch3(x), self.branch4(x)], dim=1)


class InceptionNet(nn.Module):
    def __init__(self, num_classes=2, in_channels=1):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(3, stride=2, padding=1),
            nn.Conv2d(64, 192, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(3, stride=2, padding=1),
        )
        self.inception3a = InceptionModule(192, 64, 96, 128, 16, 32, 32)
        self.inception3b = InceptionModule(256, 128, 128, 192, 32, 96, 64)
        self.maxpool = nn.MaxPool2d(3, stride=2, padding=1)
        self.inception4a = InceptionModule(480, 192, 96, 208, 16, 48, 64)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(0.4)
        self.fc = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.stem(x)
        x = self.inception3a(x)
        x = self.inception3b(x)
        x = self.maxpool(x)
        x = self.inception4a(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        return self.fc(x)


class DenseLayer(nn.Module):
    def __init__(self, in_channels, growth_rate, bn_size=4):
        super().__init__()
        self.bn1 = nn.BatchNorm2d(in_channels)
        self.conv1 = nn.Conv2d(in_channels, bn_size * growth_rate, kernel_size=1, bias=False)
        self.bn2 = nn.BatchNorm2d(bn_size * growth_rate)
        self.conv2 = nn.Conv2d(bn_size * growth_rate, growth_rate, kernel_size=3, padding=1, bias=False)

    def forward(self, x):
        out = self.conv1(F.relu(self.bn1(x)))
        out = self.conv2(F.relu(self.bn2(out)))
        return torch.cat([x, out], dim=1)


class DenseBlock(nn.Module):
    def __init__(self, num_layers, in_channels, growth_rate):
        super().__init__()
        layers = []
        for i in range(num_layers):
            layers.append(DenseLayer(in_channels + i * growth_rate, growth_rate))
        self.block = nn.Sequential(*layers)

    def forward(self, x):
        return self.block(x)


class TransitionLayer(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.bn = nn.BatchNorm2d(in_channels)
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self.pool = nn.AvgPool2d(kernel_size=2, stride=2)

    def forward(self, x):
        x = self.conv(F.relu(self.bn(x)))
        return self.pool(x)


class DenseNet(nn.Module):
    def __init__(self, growth_rate=32, block_config=(6, 12, 24, 16), num_classes=2, in_channels=1):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
        )
        num_channels = 64
        for i, num_layers in enumerate(block_config):
            block = DenseBlock(num_layers, num_channels, growth_rate)
            self.features.add_module(f"denseblock{i+1}", block)
            num_channels += num_layers * growth_rate
            if i != len(block_config) - 1:
                trans = TransitionLayer(num_channels, num_channels // 2)
                self.features.add_module(f"transition{i+1}", trans)
                num_channels = num_channels // 2
        self.features.add_module("norm5", nn.BatchNorm2d(num_channels))
        self.classifier = nn.Linear(num_channels, num_classes)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))

    def forward(self, x):
        x = self.features(x)
        x = F.relu(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        return self.classifier(x)


def densenet121(num_classes=2, in_channels=1):
    return DenseNet(growth_rate=32, block_config=(6, 12, 24, 16), num_classes=num_classes, in_channels=in_channels)


class SqueezeExcitation(nn.Module):
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.fc1 = nn.Linear(channels, channels // reduction)
        self.fc2 = nn.Linear(channels // reduction, channels)

    def forward(self, x):
        b, c, _, _ = x.size()
        y = F.adaptive_avg_pool2d(x, 1).view(b, c)
        y = F.relu(self.fc1(y))
        y = torch.sigmoid(self.fc2(y)).view(b, c, 1, 1)
        return x * y


class SEResNetBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1, reduction=16):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.se = SqueezeExcitation(out_channels, reduction)
        self.downsample = None
        if stride != 1 or in_channels != out_channels:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels),
            )

    def forward(self, x):
        identity = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out = self.se(out)
        if self.downsample is not None:
            identity = self.downsample(x)
        out += identity
        return F.relu(out)


class MobileNetBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.depthwise = nn.Conv2d(in_channels, in_channels, 3, stride=stride, padding=1, groups=in_channels, bias=False)
        self.bn1 = nn.BatchNorm2d(in_channels)
        self.pointwise = nn.Conv2d(in_channels, out_channels, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        x = F.relu(self.bn1(self.depthwise(x)))
        x = F.relu(self.bn2(self.pointwise(x)))
        return x


class MobileNet(nn.Module):
    def __init__(self, num_classes=2, in_channels=1, width_mult=1.0):
        super().__init__()
        def c(x):
            return int(x * width_mult)
        self.model = nn.Sequential(
            nn.Conv2d(in_channels, c(32), 3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(c(32)),
            nn.ReLU(inplace=True),
            MobileNetBlock(c(32), c(64), stride=1),
            MobileNetBlock(c(64), c(128), stride=2),
            MobileNetBlock(c(128), c(128), stride=1),
            MobileNetBlock(c(128), c(256), stride=2),
            MobileNetBlock(c(256), c(256), stride=1),
            MobileNetBlock(c(256), c(512), stride=2),
            *[MobileNetBlock(c(512), c(512), stride=1) for _ in range(5)],
            MobileNetBlock(c(512), c(1024), stride=2),
            MobileNetBlock(c(1024), c(1024), stride=1),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.fc = nn.Linear(c(1024), num_classes)

    def forward(self, x):
        x = self.model(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


class EfficientNetBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, expansion=6):
        super().__init__()
        hidden = in_channels * expansion
        self.use_residual = stride == 1 and in_channels == out_channels
        self.conv1 = nn.Conv2d(in_channels, hidden, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(hidden)
        self.conv2 = nn.Conv2d(hidden, hidden, kernel_size, stride=stride, padding=kernel_size // 2, groups=hidden, bias=False)
        self.bn2 = nn.BatchNorm2d(hidden)
        self.conv3 = nn.Conv2d(hidden, out_channels, 1, bias=False)
        self.bn3 = nn.BatchNorm2d(out_channels)
        self.se = SqueezeExcitation(out_channels)

    def forward(self, x):
        identity = x
        out = F.silu(self.bn1(self.conv1(x)))
        out = F.silu(self.bn2(self.conv2(out)))
        out = self.bn3(self.conv3(out))
        out = self.se(out)
        if self.use_residual:
            out += identity
        return out


class EfficientNet(nn.Module):
    def __init__(self, num_classes=2, in_channels=1, width_mult=1.0, depth_mult=1.0):
        super().__init__()
        def c(x):
            return int(x * width_mult)
        layers = [
            (c(32), 3, 1, 1),
            (c(16), 3, 2, 6),
            (c(24), 3, 2, 6),
            (c(40), 5, 2, 6),
            (c(80), 3, 2, 6),
            (c(112), 5, 1, 6),
            (c(192), 5, 2, 6),
            (c(320), 3, 1, 6),
        ]
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, c(32), 3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(c(32)),
            nn.SiLU(inplace=True),
        )
        blocks = []
        in_c = c(32)
        for out_c, ks, stride, exp in layers:
            blocks.append(EfficientNetBlock(in_c, out_c, ks, stride, exp))
            in_c = out_c
        self.blocks = nn.Sequential(*blocks)
        self.head = nn.Sequential(
            nn.Conv2d(in_c, c(1280), 1, bias=False),
            nn.BatchNorm2d(c(1280)),
            nn.SiLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.fc = nn.Linear(c(1280), num_classes)

    def forward(self, x):
        x = self.stem(x)
        x = self.blocks(x)
        x = self.head(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


class ConvNeXtBlock(nn.Module):
    def __init__(self, dim, layer_scale_init_value=1e-6):
        super().__init__()
        self.dwconv = nn.Conv2d(dim, dim, kernel_size=7, padding=3, groups=dim)
        self.norm = nn.LayerNorm(dim, eps=1e-6)
        self.pwconv1 = nn.Linear(dim, 4 * dim)
        self.act = nn.GELU()
        self.pwconv2 = nn.Linear(4 * dim, dim)
        self.gamma = nn.Parameter(layer_scale_init_value * torch.ones(dim)) if layer_scale_init_value > 0 else None

    def forward(self, x):
        input = x
        x = self.dwconv(x)
        x = x.permute(0, 2, 3, 1)
        x = self.norm(x)
        x = self.pwconv1(x)
        x = self.act(x)
        x = self.pwconv2(x)
        if self.gamma is not None:
            x = self.gamma * x
        x = x.permute(0, 3, 1, 2)
        return input + x


class ConvNeXt(nn.Module):
    def __init__(self, in_channels=1, num_classes=2, dims=[48, 96], depths=[2, 2]):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, dims[0], kernel_size=4, stride=4),
            nn.BatchNorm2d(dims[0]),
            nn.GELU(),
        )
        self.stages = nn.ModuleList()
        for i in range(len(dims)):
            blocks = nn.Sequential(*[ConvNeXtBlock(dims[i]) for _ in range(depths[i])])
            self.stages.append(blocks)
            if i < len(dims) - 1:
                self.stages.append(nn.Sequential(
                    nn.BatchNorm2d(dims[i]),
                    nn.Conv2d(dims[i], dims[i+1], kernel_size=2, stride=2),
                ))
        self.norm = nn.BatchNorm2d(dims[-1])
        self.head = nn.Sequential(nn.AdaptiveAvgPool2d((1, 1)), nn.Flatten(), nn.Linear(dims[-1], num_classes))

    def forward(self, x):
        x = self.stem(x)
        for stage in self.stages:
            x = stage(x)
        x = self.norm(x)
        return self.head(x)


class ViTBlock(nn.Module):
    def __init__(self, dim, num_heads, mlp_ratio=4.0, dropout=0.1):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(
            nn.Linear(dim, int(dim * mlp_ratio)),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(int(dim * mlp_ratio), dim),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        x = x + self.attn(self.norm1(x), self.norm1(x), self.norm1(x))[0]
        x = x + self.mlp(self.norm2(x))
        return x


class VisionTransformer(nn.Module):
    def __init__(self, img_size=64, patch_size=8, in_channels=1, num_classes=2, dim=256, depth=6, num_heads=8, mlp_ratio=4.0, dropout=0.1):
        super().__init__()
        self.patch_size = patch_size
        num_patches = (img_size // patch_size) ** 2
        self.patch_embed = nn.Conv2d(in_channels, dim, kernel_size=patch_size, stride=patch_size)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches + 1, dim))
        self.blocks = nn.Sequential(*[ViTBlock(dim, num_heads, mlp_ratio, dropout) for _ in range(depth)])
        self.norm = nn.LayerNorm(dim)
        self.head = nn.Linear(dim, num_classes)

    def forward(self, x):
        b = x.shape[0]
        x = self.patch_embed(x).flatten(2).transpose(1, 2)
        cls = self.cls_token.expand(b, -1, -1)
        x = torch.cat([cls, x], dim=1)
        x = x + self.pos_embed
        x = self.blocks(x)
        x = self.norm(x)
        return self.head(x[:, 0])


class SwinBlock(nn.Module):
    def __init__(self, dim, num_heads, window_size=4, shift=False):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, num_heads, batch_first=True)
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(nn.Linear(dim, dim * 4), nn.GELU(), nn.Linear(dim * 4, dim))
        self.shift = shift
        self.window_size = window_size

    def forward(self, x):
        # simplified global attention
        x = x + self.attn(self.norm1(x), self.norm1(x), self.norm1(x))[0]
        x = x + self.mlp(self.norm2(x))
        return x


class SwinTransformer(nn.Module):
    def __init__(self, img_size=64, patch_size=4, in_channels=1, num_classes=2, dim=96, depths=[2, 2, 6, 2], num_heads=[3, 6, 12, 24]):
        super().__init__()
        self.patch_embed = nn.Conv2d(in_channels, dim, kernel_size=patch_size, stride=patch_size)
        self.layers = nn.ModuleList()
        for i in range(4):
            self.layers.append(nn.Sequential(*[SwinBlock(dim * (2 ** i), num_heads[i]) for _ in range(depths[i])]))
        self.norm = nn.LayerNorm(dim * 8)
        self.head = nn.Linear(dim * 8, num_classes)

    def forward(self, x):
        x = self.patch_embed(x).flatten(2).transpose(1, 2)
        for layer in self.layers:
            x = layer(x)
        x = self.norm(x)
        x = x.mean(dim=1)
        return self.head(x)


class CRNN(nn.Module):
    def __init__(self, num_classes=2, in_channels=1, hidden_size=128):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.rnn = nn.LSTM(64 * 16, hidden_size, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_size * 2, num_classes)

    def forward(self, x):
        x = self.cnn(x)
        b, c, h, w = x.size()
        x = x.permute(0, 3, 1, 2).contiguous().view(b, w, c * h)
        out, _ = self.rnn(x)
        out = out[:, -1, :]
        return self.fc(out)


class TCNBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, dilation=1):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size, padding=(kernel_size - 1) * dilation // 2, dilation=dilation)
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size, padding=(kernel_size - 1) * dilation // 2, dilation=dilation)
        self.bn2 = nn.BatchNorm1d(out_channels)
        self.downsample = nn.Conv1d(in_channels, out_channels, 1) if in_channels != out_channels else None

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        res = x if self.downsample is None else self.downsample(x)
        return F.relu(out + res)


class TemporalConvNet(nn.Module):
    def __init__(self, num_channels, kernel_size=3, num_classes=2):
        super().__init__()
        layers = []
        for i in range(len(num_channels)):
            dilation = 2 ** i
            in_c = num_channels[i - 1] if i > 0 else num_channels[0]
            out_c = num_channels[i]
            layers.append(TCNBlock(in_c, out_c, kernel_size, dilation))
        self.network = nn.Sequential(*layers)
        self.fc = nn.Linear(num_channels[-1], num_classes)

    def forward(self, x):
        # x: (batch, channels, time)
        out = self.network(x)
        out = out.mean(dim=2)
        return self.fc(out)


class TransformerEncoder(nn.Module):
    def __init__(self, input_dim, num_heads=4, num_layers=2, dim_feedforward=256, dropout=0.1, num_classes=2):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, dim_feedforward)
        encoder_layer = nn.TransformerEncoderLayer(d_model=dim_feedforward, nhead=num_heads, dim_feedforward=dim_feedforward, dropout=dropout, batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(dim_feedforward, num_classes)

    def forward(self, x):
        # x: (batch, seq, features)
        x = self.input_proj(x)
        x = self.encoder(x)
        x = x.mean(dim=1)
        return self.fc(x)


class AudioTransformer(nn.Module):
    def __init__(self, n_mels=64, num_classes=2, dim=128, depth=4, num_heads=4):
        super().__init__()
        self.patch_embed = nn.Linear(n_mels, dim)
        self.pos = nn.Parameter(torch.zeros(1, 1000, dim))
        self.blocks = nn.ModuleList([ViTBlock(dim, num_heads) for _ in range(depth)])
        self.norm = nn.LayerNorm(dim)
        self.head = nn.Linear(dim, num_classes)

    def forward(self, x):
        # x: (batch, n_mels, time)
        x = x.transpose(1, 2)
        x = self.patch_embed(x)
        b, t, d = x.shape
        x = x + self.pos[:, :t, :]
        for block in self.blocks:
            x = block(x)
        x = self.norm(x)
        x = x.mean(dim=1)
        return self.head(x)


class WaveNetBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=2, dilation=1):
        super().__init__()
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size, dilation=dilation, padding=(kernel_size - 1) * dilation)
        self.bn = nn.BatchNorm1d(out_channels)
        self.gate = nn.Conv1d(in_channels, out_channels, kernel_size, dilation=dilation, padding=(kernel_size - 1) * dilation)

    def forward(self, x):
        out = torch.tanh(self.conv(x)) * torch.sigmoid(self.gate(x))
        return out


class WaveNet(nn.Module):
    def __init__(self, in_channels=1, num_classes=2, num_blocks=4):
        super().__init__()
        layers = []
        for i in range(num_blocks):
            layers.append(WaveNetBlock(in_channels if i == 0 else 32, 32, dilation=2 ** i))
        self.network = nn.Sequential(*layers)
        self.fc = nn.Linear(32, num_classes)

    def forward(self, x):
        out = self.network(x)
        out = out.mean(dim=2)
        return self.fc(out)


class SqueezeNet(nn.Module):
    def __init__(self, num_classes=2, in_channels=1):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channels, 96, kernel_size=7, stride=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(3, stride=2),
            self._fire(96, 16, 64, 64),
            self._fire(128, 16, 64, 64),
            self._fire(128, 32, 128, 128),
            nn.MaxPool2d(3, stride=2),
            self._fire(256, 32, 128, 128),
            self._fire(256, 48, 192, 192),
            self._fire(384, 48, 192, 192),
            self._fire(384, 64, 256, 256),
            nn.MaxPool2d(3, stride=2),
            self._fire(512, 64, 256, 256),
        )
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Conv2d(512, num_classes, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
        )

    def _fire(self, in_c, squeeze, expand1, expand2):
        return nn.Sequential(
            nn.Conv2d(in_c, squeeze, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Sequential(
                nn.Conv2d(squeeze, expand1, kernel_size=1),
                nn.ReLU(inplace=True),
            ),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return torch.flatten(x, 1)


class ShuffleNetUnit(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1, groups=2):
        super().__init__()
        self.groups = groups
        mid = out_channels // 4
        self.conv1 = nn.Conv2d(in_channels, mid, 1, groups=groups, bias=False)
        self.bn1 = nn.BatchNorm2d(mid)
        self.conv2 = nn.Conv2d(mid, mid, 3, stride=stride, padding=1, groups=mid, bias=False)
        self.bn2 = nn.BatchNorm2d(mid)
        self.conv3 = nn.Conv2d(mid, out_channels, 1, groups=groups, bias=False)
        self.bn3 = nn.BatchNorm2d(out_channels)
        self.shuffle = nn.ChannelShuffle(groups)
        self.downsample = None
        if stride != 1 or in_channels != out_channels:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride=stride, groups=groups, bias=False),
                nn.BatchNorm2d(out_channels),
            )

    def forward(self, x):
        identity = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.shuffle(out)
        out = F.relu(self.bn2(self.conv2(out)))
        out = self.bn3(self.conv3(out))
        if self.downsample is not None:
            identity = self.downsample(x)
        return F.relu(out + identity)


class GhostModule(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=1, ratio=2):
        super().__init__()
        init_channels = out_channels // ratio
        new_channels = init_channels * (ratio - 1)
        self.primary = nn.Sequential(
            nn.Conv2d(in_channels, init_channels, kernel_size, bias=False),
            nn.BatchNorm2d(init_channels),
            nn.ReLU(inplace=True),
        )
        self.cheap = nn.Sequential(
            nn.Conv2d(init_channels, new_channels, kernel_size, groups=init_channels, bias=False, padding=kernel_size // 2),
            nn.BatchNorm2d(new_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        x1 = self.primary(x)
        x2 = self.cheap(x1)
        return torch.cat([x1, x2], dim=1)


class GhostNet(nn.Module):
    def __init__(self, num_classes=2, in_channels=1):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, 16, 3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
        )
        self.blocks = nn.Sequential(
            GhostModule(16, 16),
            GhostModule(32, 32),
        )
        self.head = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(32, num_classes),
        )

    def forward(self, x):
        x = self.stem(x)
        x = self.blocks(x)
        return self.head(x)


class RegNetBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, stride=stride, padding=1, groups=out_channels, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.conv3 = nn.Conv2d(out_channels, out_channels, 1, bias=False)
        self.bn3 = nn.BatchNorm2d(out_channels)
        self.downsample = None
        if stride != 1 or in_channels != out_channels:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels),
            )

    def forward(self, x):
        identity = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = F.relu(self.bn2(self.conv2(out)))
        out = self.bn3(self.conv3(out))
        if self.downsample is not None:
            identity = self.downsample(x)
        return F.relu(out + identity)


class RegNet(nn.Module):
    def __init__(self, num_classes=2, in_channels=1):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, 32, 3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
        )
        self.stage1 = RegNetBlock(32, 32)
        self.stage2 = RegNetBlock(32, 64, stride=2)
        self.stage3 = RegNetBlock(64, 128, stride=2)
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.stem(x)
        x = self.stage1(x)
        x = self.stage2(x)
        x = self.stage3(x)
        x = self.pool(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


class RepVGGBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv3x3 = nn.Conv2d(in_channels, out_channels, 3, stride=stride, padding=1)
        self.conv1x1 = nn.Conv2d(in_channels, out_channels, 1, stride=stride)
        self.bn = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        return self.bn(self.conv3x3(x) + self.conv1x1(x))


class RepVGG(nn.Module):
    def __init__(self, num_classes=2, in_channels=1):
        super().__init__()
        self.stage1 = RepVGGBlock(in_channels, 32)
        self.stage2 = RepVGGBlock(32, 64, stride=2)
        self.stage3 = RepVGGBlock(64, 128, stride=2)
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.stage1(x)
        x = self.stage2(x)
        x = self.stage3(x)
        x = self.pool(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


class ConvMixer(nn.Module):
    def __init__(self, dim=256, depth=8, kernel_size=5, patch_size=4, num_classes=2, in_channels=1):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, dim, kernel_size=patch_size, stride=patch_size),
            nn.GELU(),
            nn.BatchNorm2d(dim),
        )
        self.blocks = nn.ModuleList([
            nn.Sequential(
                nn.Conv2d(dim, dim, kernel_size, groups=dim, padding=kernel_size // 2),
                nn.GELU(),
                nn.BatchNorm2d(dim),
                nn.Conv2d(dim, dim, kernel_size=1),
                nn.GELU(),
                nn.BatchNorm2d(dim),
            ) for _ in range(depth)
        ])
        self.head = nn.Sequential(nn.AdaptiveAvgPool2d((1, 1)), nn.Flatten(), nn.Linear(dim, num_classes))

    def forward(self, x):
        x = self.stem(x)
        for block in self.blocks:
            x = x + block(x)
        return self.head(x)


class MLPBlock(nn.Module):
    def __init__(self, dim, expansion=4, dropout=0.1):
        super().__init__()
        self.fc1 = nn.Linear(dim, dim * expansion)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(dim * expansion, dim)
        self.drop = nn.Dropout(dropout)

    def forward(self, x):
        return x + self.drop(self.fc2(self.act(self.fc1(x))))


class MLPModel(nn.Module):
    def __init__(self, input_dim, hidden_dim=256, num_layers=4, num_classes=2, dropout=0.1):
        super().__init__()
        self.input = nn.Linear(input_dim, hidden_dim)
        self.blocks = nn.Sequential(*[MLPBlock(hidden_dim, dropout=dropout) for _ in range(num_layers)])
        self.norm = nn.LayerNorm(hidden_dim)
        self.head = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        x = self.input(x)
        x = self.blocks(x)
        x = self.norm(x)
        return self.head(x)


class TabNet(nn.Module):
    def __init__(self, input_dim, num_classes=2, n_d=64, n_a=64, n_steps=3):
        super().__init__()
        self.n_d = n_d
        self.n_a = n_a
        self.n_steps = n_steps
        self.initial_bn = nn.BatchNorm1d(input_dim)
        self.encoders = nn.ModuleList([nn.Linear(input_dim, n_d + n_a) for _ in range(n_steps)])
        self.fc = nn.Linear(n_d, num_classes)

    def forward(self, x):
        x = self.initial_bn(x)
        agg = 0
        for enc in self.encoders:
            out = enc(x)
            d = out[:, :self.n_d]
            agg = agg + d
        return self.fc(agg / self.n_steps)


class FTTransformer(nn.Module):
    def __init__(self, input_dim, num_classes=2, dim=128, depth=3, num_heads=4):
        super().__init__()
        self.feature_tokenizer = nn.Linear(1, dim)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, dim))
        self.pos = nn.Parameter(torch.zeros(1, input_dim + 1, dim))
        self.blocks = nn.ModuleList([ViTBlock(dim, num_heads) for _ in range(depth)])
        self.norm = nn.LayerNorm(dim)
        self.head = nn.Linear(dim, num_classes)

    def forward(self, x):
        # x: (batch, features)
        b, f = x.shape
        x = x.unsqueeze(-1)
        x = self.feature_tokenizer(x)  # (b, f, dim)
        cls = self.cls_token.expand(b, -1, -1)
        x = torch.cat([cls, x], dim=1)
        x = x + self.pos[:, :f + 1, :]
        for block in self.blocks:
            x = block(x)
        x = self.norm(x)
        return self.head(x[:, 0])


class AutoEncoder(nn.Module):
    def __init__(self, input_dim, latent_dim=32):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, latent_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(),
            nn.Linear(128, input_dim),
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)

    def encode(self, x):
        return self.encoder(x)


class VAE(nn.Module):
    def __init__(self, input_dim, latent_dim=32):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc_mu = nn.Linear(128, latent_dim)
        self.fc_logvar = nn.Linear(128, latent_dim)
        self.fc2 = nn.Linear(latent_dim, 128)
        self.fc3 = nn.Linear(128, input_dim)

    def encode(self, x):
        h = F.relu(self.fc1(x))
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        h = F.relu(self.fc2(z))
        return self.fc3(h)

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar


class GAN_Generator(nn.Module):
    def __init__(self, latent_dim=100, output_dim=13):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, output_dim),
        )

    def forward(self, z):
        return self.net(z)


class GAN_Discriminator(nn.Module):
    def __init__(self, input_dim=13):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x)


class LSTMClassifier(nn.Module):
    def __init__(self, input_dim=13, hidden_dim=128, num_layers=2, num_classes=2, bidirectional=True):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, bidirectional=bidirectional)
        mult = 2 if bidirectional else 1
        self.fc = nn.Linear(hidden_dim * mult, num_classes)

    def forward(self, x):
        # x: (batch, seq, features)
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        return self.fc(out)


class GRUClassifier(nn.Module):
    def __init__(self, input_dim=13, hidden_dim=128, num_layers=2, num_classes=2, bidirectional=True):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, bidirectional=bidirectional)
        mult = 2 if bidirectional else 1
        self.fc = nn.Linear(hidden_dim * mult, num_classes)

    def forward(self, x):
        out, _ = self.gru(x)
        out = out[:, -1, :]
        return self.fc(out)


class TransformerClassifier(nn.Module):
    def __init__(self, input_dim=13, num_classes=2, dim=128, depth=2, num_heads=4, max_len=100):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, dim)
        self.pos = nn.Parameter(torch.zeros(1, max_len, dim))
        self.blocks = nn.ModuleList([ViTBlock(dim, num_heads) for _ in range(depth)])
        self.norm = nn.LayerNorm(dim)
        self.head = nn.Linear(dim, num_classes)

    def forward(self, x):
        b, t, _ = x.shape
        x = self.input_proj(x)
        x = x + self.pos[:, :t, :]
        for block in self.blocks:
            x = block(x)
        x = self.norm(x)
        x = x.mean(dim=1)
        return self.head(x)


class AttentionPool(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.att = nn.Linear(dim, 1)

    def forward(self, x):
        # x: (batch, seq, dim)
        w = torch.softmax(self.att(x), dim=1)
        return (x * w).sum(dim=1)


class AudioClassifier(nn.Module):
    def __init__(self, num_classes=2, in_channels=1):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.pool = AttentionPool(64 * 4 * 4)
        self.fc = nn.Linear(64 * 4 * 4, num_classes)

    def forward(self, x):
        x = self.conv(x)
        b, c, h, w = x.size()
        x = x.view(b, c * h * w, 1).squeeze(-1).unsqueeze(1)
        # simplify: flatten
        x = x.view(b, -1)
        return self.fc(x)


class SiameseNetwork(nn.Module):
    def __init__(self, input_dim=13, hidden_dim=64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )

    def forward(self, x1, x2):
        z1 = self.encoder(x1)
        z2 = self.encoder(x2)
        return F.pairwise_distance(z1, z2)

    def encode(self, x):
        return self.encoder(x)


class TripletNetwork(nn.Module):
    def __init__(self, input_dim=13, hidden_dim=64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )

    def forward(self, anchor, positive, negative):
        a = self.encoder(anchor)
        p = self.encoder(positive)
        n = self.encoder(negative)
        return a, p, n


class ContrastiveLoss(nn.Module):
    def __init__(self, margin=1.0):
        super().__init__()
        self.margin = margin

    def forward(self, dist, label):
        # label: 1 same, 0 different
        loss = label * dist.pow(2) + (1 - label) * F.relu(self.margin - dist).pow(2)
        return loss.mean()


class TripletLoss(nn.Module):
    def __init__(self, margin=1.0):
        super().__init__()
        self.margin = margin

    def forward(self, anchor, positive, negative):
        d_ap = F.pairwise_distance(anchor, positive)
        d_an = F.pairwise_distance(anchor, negative)
        return F.relu(d_ap - d_an + self.margin).mean()


class FocalLoss(nn.Module):
    def __init__(self, alpha=0.25, gamma=2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, logits, targets):
        ce = F.cross_entropy(logits, targets, reduction="none")
        pt = torch.exp(-ce)
        loss = self.alpha * (1 - pt) ** self.gamma * ce
        return loss.mean()


class LabelSmoothingLoss(nn.Module):
    def __init__(self, num_classes=2, smoothing=0.1):
        super().__init__()
        self.num_classes = num_classes
        self.smoothing = smoothing

    def forward(self, logits, targets):
        log_probs = F.log_softmax(logits, dim=1)
        with torch.no_grad():
            smooth = torch.full_like(log_probs, self.smoothing / (self.num_classes - 1))
            smooth.scatter_(1, targets.unsqueeze(1), 1 - self.smoothing)
        return (-smooth * log_probs).sum(dim=1).mean()


class MixupAugmentation:
    def __init__(self, alpha=0.2):
        self.alpha = alpha

    def __call__(self, x, y):
        lam = torch.distributions.Beta(self.alpha, self.alpha).sample() if self.alpha > 0 else 1.0
        lam = max(lam, 1 - lam)
        index = torch.randperm(x.size(0))
        mixed_x = lam * x + (1 - lam) * x[index]
        y_a, y_b = y, y[index]
        return mixed_x, y_a, y_b, lam


class CutMixAugmentation:
    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def __call__(self, x, y):
        lam = torch.distributions.Beta(self.alpha, self.alpha).sample() if self.alpha > 0 else 1.0
        index = torch.randperm(x.size(0))
        # simplified: mix entire
        mixed_x = lam * x + (1 - lam) * x[index]
        return mixed_x, y, y[index], lam


class SpecAugment:
    def __init__(self, freq_mask=10, time_mask=10):
        self.freq_mask = freq_mask
        self.time_mask = time_mask

    def __call__(self, x):
        # x: (batch, 1, freq, time)
        b, c, f, t = x.shape
        # freq mask
        f0 = torch.randint(0, max(1, f - self.freq_mask), (1,)).item()
        x[:, :, f0:f0 + self.freq_mask, :] = 0
        # time mask
        t0 = torch.randint(0, max(1, t - self.time_mask), (1,)).item()
        x[:, :, :, t0:t0 + self.time_mask] = 0
        return x


class GaussianNoise:
    def __init__(self, std=0.01):
        self.std = std

    def __call__(self, x):
        return x + torch.randn_like(x) * self.std


class RandomErasing:
    def __init__(self, p=0.5, scale=(0.02, 0.33)):
        self.p = p
        self.scale = scale

    def __call__(self, x):
        if torch.rand(1).item() > self.p:
            return x
        _, c, h, w = x.shape
        area = h * w
        target = area * torch.empty(1).uniform_(*self.scale).item()
        aspect = torch.empty(1).uniform_(0.3, 3.3).item()
        eh = int((target * aspect) ** 0.5)
        ew = int((target / aspect) ** 0.5)
        if eh >= h or ew >= w:
            return x
        i = torch.randint(0, h - eh, (1,)).item()
        j = torch.randint(0, w - ew, (1,)).item()
        x[:, :, i:i + eh, j:j + ew] = 0
        return x


MODEL_REGISTRY = {
    "resnet18": resnet18,
    "resnet34": resnet34,
    "resnet50": resnet50,
    "vgg11": vgg11,
    "vgg13": vgg13,
    "inception": InceptionNet,
    "densenet121": densenet121,
    "mobilenet": MobileNet,
    "efficientnet": EfficientNet,
    "convnext": ConvNeXt,
    "vit": VisionTransformer,
    "swin": SwinTransformer,
    "crnn": CRNN,
    "tcn": TemporalConvNet,
    "transformer": TransformerEncoder,
    "audio_transformer": AudioTransformer,
    "wavenet": WaveNet,
    "squeezenet": SqueezeNet,
    "ghostnet": GhostNet,
    "regnet": RegNet,
    "repvgg": RepVGG,
    "convmixer": ConvMixer,
    "mlp": MLPModel,
    "tabnet": TabNet,
    "ft_transformer": FTTransformer,
    "lstm": LSTMClassifier,
    "gru": GRUClassifier,
    "transformer_cls": TransformerClassifier,
    "audio_classifier": AudioClassifier,
    "siamese": SiameseNetwork,
    "triplet": TripletNetwork,
}


def get_model(name: str, **kwargs):
    if name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model: {name}")
    return MODEL_REGISTRY[name](**kwargs)


def list_models():
    return list(MODEL_REGISTRY.keys())
