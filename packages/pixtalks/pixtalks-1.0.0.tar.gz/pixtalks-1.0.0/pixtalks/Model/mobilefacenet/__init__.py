import torch.nn as nn
import math
from pixtalks.Model import conv_1x1_bn, conv_bn, conv_dw_bn, GDConv, InvertedResidual


class MobileFaceNet(nn.Module):
    def __init__(self, input_channel=3, first_channel=64, last_channel=512, feature_dim=128,
                 width_mult=1., GDC_kernel_size=(7, 6), **kwargs):
        super(MobileFaceNet, self).__init__()
        block = InvertedResidual

        if kwargs.get('interverted_residual_setting') is None:
            interverted_residual_setting = [
                # t, c, n, s
                [2, 64, 5, 2],
                [4, 128, 1, 2],
                [2, 128, 6, 1],
                [4, 128, 1, 2],
                [2, 128, 2, 1],
            ]
        else:
            interverted_residual_setting = kwargs.get('interverted_residual_setting')

        first_channel = int(first_channel * width_mult)
        last_channel = int(last_channel * width_mult) if width_mult > 1.0 else last_channel
        temp = conv_bn(input_channel, first_channel, kernel_size=3, stride=2, padding=1)
        trunk = [temp]
        # building inverted residual blocks
        for t, c, n, s in interverted_residual_setting:
            output_channel = int(c * width_mult)
            for i in range(n):
                if i == 0:
                    temp = block(first_channel, output_channel, s, expand_ratio=t)
                    trunk.append(temp)
                else:
                    temp = block(first_channel, output_channel, 1, expand_ratio=t)
                    trunk.append(temp)
                first_channel = output_channel
        # building last several layers
        temp = conv_1x1_bn(first_channel, last_channel)
        trunk.append(temp)
        temp = GDConv(last_channel, GDC_kernel_size)
        trunk.append(temp)
        temp = nn.Conv2d(last_channel, feature_dim, 1, 1, 0, bias=False)
        trunk.append(temp)
        temp = nn.BatchNorm2d(feature_dim, affine=False)
        trunk.append(temp)
        self.trunk = trunk
        self.features = nn.Sequential(*trunk)

        self._initialize_weights()

    def forward(self, x):

        x = self.features(x)
        x = x.view(x.shape[0], -1)

        return x

    def forward_feature_map(self, x):
        feature_map = self.features[:-3]

        return feature_map(x)

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
                if m.bias is not None:
                    m.bias.data.zero_()
            elif isinstance(m, nn.BatchNorm2d):
                if m.weight is not None:
                    m.weight.data.fill_(1)
                if m.bias is not None:
                    m.bias.data.zero_()
            elif isinstance(m, nn.Linear):
                n = m.weight.size(1)
                m.weight.data.normal_(0, 0.01)
                m.bias.data.zero_()

class MobileFaceNet_oldversion(nn.Module):
    def __init__(self, input_channel=3, first_channel=64, last_channel=512, feature_dim=128,
                 width_mult=1., GDC_kernel_size=(7, 6), **kwargs):
        super(MobileFaceNet_oldversion, self).__init__()
        block = InvertedResidual

        if kwargs.get('interverted_residual_setting') is None:
            interverted_residual_setting = [
                # t, c, n, s
                [2, 64, 5, 2],
                [4, 128, 1, 2],
                [2, 128, 6, 1],
                [4, 128, 1, 2],
                [2, 128, 2, 1],
            ]
        else:
            interverted_residual_setting = kwargs.get('interverted_residual_setting')

        first_channel = int(first_channel * width_mult)
        last_channel = int(last_channel * width_mult) if width_mult > 1.0 else last_channel
        temp = conv_bn(input_channel, first_channel, kernel_size=3, stride=2, padding=1)
        trunk = [temp]
        # building inverted residual blocks
        for t, c, n, s in interverted_residual_setting:
            output_channel = int(c * width_mult)
            for i in range(n):
                if i == 0:
                    temp = block(first_channel, output_channel, s, expand_ratio=t)
                    trunk.append(temp)
                else:
                    temp = block(first_channel, output_channel, 1, expand_ratio=t)
                    trunk.append(temp)
                first_channel = output_channel
        # building last several layers
        temp = conv_1x1_bn(first_channel, last_channel)
        trunk.append(temp[0])
        temp = GDConv(last_channel, GDC_kernel_size)
        trunk.append(temp[0])
        temp = nn.Conv2d(last_channel, feature_dim, 1, 1, 0, bias=False)
        trunk.append(temp)
        temp = nn.BatchNorm2d(feature_dim, affine=False)
        trunk.append(temp)
        self.trunk = trunk
        self.features = nn.Sequential(*trunk)

        self._initialize_weights()

    def forward(self, x):

        x = self.features(x)
        x = x.view(x.shape[0], -1)

        return x

    def forward_feature_map(self, x):
        feature_map = self.features[:-3]

        return feature_map(x)

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
                if m.bias is not None:
                    m.bias.data.zero_()
            elif isinstance(m, nn.BatchNorm2d):
                if m.weight is not None:
                    m.weight.data.fill_(1)
                if m.bias is not None:
                    m.bias.data.zero_()
            elif isinstance(m, nn.Linear):
                n = m.weight.size(1)
                m.weight.data.normal_(0, 0.01)
                m.bias.data.zero_()