import torch.nn as nn
import math


def conv_bn(inp, oup, stride):
    temp = nn.Conv2d(inp, oup, 3, stride, 1, bias=False)
    return nn.Sequential(
        temp,
        nn.BatchNorm2d(oup),
        nn.ReLU(inplace=True)
    ), nn.Sequential(
        temp,
        nn.BatchNorm2d(oup),
        nn.ReLU(inplace=True)
    )

def conv_dw_bn(dim, kernel_size, stride, pad):
    temp = nn.Conv2d(dim, dim, kernel_size, stride, pad, groups=dim, bias=False)
    return nn.Sequential(
        temp,
        nn.BatchNorm2d(dim),
        nn.ReLU(inplace=True)
    ), nn.Sequential(
        temp,
        nn.BatchNorm2d(dim),
        nn.ReLU(inplace=True)
    )

def GDConv(dim, kernel_size):
    temp = nn.Conv2d(dim, dim, kernel_size, groups=dim, bias=False)
    return nn.Sequential(
        temp,
        nn.BatchNorm2d(dim)
    ), nn.Sequential(
        temp,
        nn.BatchNorm2d(dim)
    )

def conv_1x1_bn(inp, oup):
    temp = nn.Conv2d(inp, oup, 1, 1, 0, bias=False)
    return nn.Sequential(
        temp,
        nn.BatchNorm2d(oup),
        nn.ReLU(inplace=True)
    ), nn.Sequential(
        temp,
        nn.BatchNorm2d(oup),
        nn.ReLU(inplace=True)
    )


class InvertedResidual(nn.Module):

    checkout = False

    def __init__(self, inp, oup, stride, expand_ratio):
        super(InvertedResidual, self).__init__()
        self.stride = stride
        assert stride in [1, 2]

        hidden_dim = int(round(inp * expand_ratio))
        self.use_res_connect = self.stride == 1 and inp == oup

        if expand_ratio == 1:
            temp1 = nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, groups=hidden_dim, bias=False)
            temp2 = nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False)
            self.conv = nn.Sequential(
                # dw
                temp1,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU(inplace=True),
                # pw-linear
                temp2,
                nn.BatchNorm2d(oup),
            )
            self.conv2 = nn.Sequential(
                # dw
                temp1,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU(inplace=True),
                # pw-linear
                temp2,
                nn.BatchNorm2d(oup),
            )
        else:
            temp1 = nn.Conv2d(inp, hidden_dim, 1, 1, 0, bias=False)
            temp2 = nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, groups=hidden_dim, bias=False)
            temp3 = nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False)
            self.conv = nn.Sequential(
                # pw
                temp1,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU(inplace=True),
                # dw
                temp2,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU(inplace=True),
                # pw-linear
                temp3,
                nn.BatchNorm2d(oup),
            )
            self.conv2 = nn.Sequential(
                # pw
                temp1,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU(inplace=True),
                # dw
                temp2,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU(inplace=True),
                # pw-linear
                temp3,
                nn.BatchNorm2d(oup),
            )

    def forward(self, x):
        if self.checkout:
            conv = self.conv2
        else:
            conv = self.conv
        if self.use_res_connect:
            return x + conv(x)
        else:
            return conv(x)


class MobileFaceNet(nn.Module):
    def __init__(self, feature_dim=128, input_size=(112, 96), width_mult=0.5, channel=1, **kwargs):
        super(MobileFaceNet, self).__init__()
        block = InvertedResidual
        input_channel = 64
        last_channel = 512
        interverted_residual_setting = [
            # t, c, n, s
            [2, 64, 5, 2],
            [4, 128, 1, 2],
            [2, 128, 6, 1],
            [4, 128, 1, 2],
            [2, 128, 2, 1],
        ]
        # interverted_residual_setting = [
        #     # t, c, n, s
        #     [2, 128, 5, 2],
        #     [4, 256, 1, 2],
        #     [2, 256, 6, 1],
        #     [4, 256, 1, 2],
        #     [2, 256, 2, 1],
        # ]
        # building first layer
        assert input_size == (112, 96)
        input_channel = int(input_channel * width_mult)
        last_channel = int(last_channel * width_mult) if width_mult > 1.0 else last_channel
        temp = conv_bn(channel, input_channel, 2)
        #temp = conv_bn(1, input_channel, 2)
        trunk = [temp[0]]
        trunk2 = [temp[1]]
        temp = conv_dw_bn(input_channel, 3, 1, 1)
        trunk.append(temp[0])
        trunk2.append(temp[1])
        # building inverted residual blocks
        for t, c, n, s in interverted_residual_setting:
            output_channel = int(c * width_mult)
            for i in range(n):
                if i == 0:
                    temp = block(input_channel, output_channel, s, expand_ratio=t)
                    trunk.append(temp)
                    trunk2.append(temp)
                else:
                    temp = block(input_channel, output_channel, 1, expand_ratio=t)
                    trunk.append(temp)
                    trunk2.append(temp)
                input_channel = output_channel
        # building last several layers
        temp = conv_1x1_bn(input_channel, last_channel)
        trunk.append(temp[0])
        trunk2.append(temp[1])
        temp = GDConv(last_channel, (7, 6))
        trunk.append(temp[0])
        trunk2.append(temp[1])
        temp = nn.Conv2d(last_channel, feature_dim, 1, 1, 0, bias=False)
        trunk.append(temp)
        trunk2.append(temp)
        temp = nn.BatchNorm2d(feature_dim)
        trunk.append(temp)
        temp = nn.BatchNorm2d(feature_dim)
        trunk2.append(temp)
        self.features = nn.Sequential(*trunk)
        self.features2 = nn.Sequential(*trunk2)

        self._initialize_weights()

    def forward(self, x, checkout=False):
        InvertedResidual.checkout = checkout
        if checkout:
            x = self.features2(x)
        else:
            x = self.features(x)
        x = x.view(x.shape[0], -1)
        return x

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
