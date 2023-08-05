import torch.nn as nn
import math, torch
import torch.nn.functional as F
from torch.nn import Parameter
from pixtalks.Model.mobilefacenet.MobileFaceNet_Relu import MobileFaceNet as MobileFaceNet_Relu


def conv_bn(inp, oup, stride):
    temp = nn.Conv2d(inp, oup, 3, stride, 1, bias=False)
    return nn.Sequential(
        temp,
        nn.BatchNorm2d(oup),
        nn.ReLU6(inplace=True)
    ), nn.Sequential(
        temp,
        nn.BatchNorm2d(oup),
        nn.ReLU6(inplace=True)
    )

def conv_dw_bn(dim, kernel_size, stride, pad):
    temp = nn.Conv2d(dim, dim, kernel_size, stride, pad, groups=dim, bias=False)
    return nn.Sequential(
        temp,
        nn.BatchNorm2d(dim),
        nn.ReLU6(inplace=True)
    ), nn.Sequential(
        temp,
        nn.BatchNorm2d(dim),
        nn.ReLU6(inplace=True)
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
        nn.ReLU6(inplace=True)
    ), nn.Sequential(
        temp,
        nn.BatchNorm2d(oup),
        nn.ReLU6(inplace=True)
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
                nn.ReLU6(inplace=True),
                # pw-linear
                temp2,
                nn.BatchNorm2d(oup),
            )
            self.conv2 = nn.Sequential(
                # dw
                temp1,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU6(inplace=True),
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
                nn.ReLU6(inplace=True),
                # dw
                temp2,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU6(inplace=True),
                # pw-linear
                temp3,
                nn.BatchNorm2d(oup),
            )
            self.conv2 = nn.Sequential(
                # pw
                temp1,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU6(inplace=True),
                # dw
                temp2,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU6(inplace=True),
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
    def __init__(self, feature_dim=128, input_size=(112, 96), width_mult=0.5, channel=1):
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
        temp = nn.BatchNorm2d(feature_dim, affine=False)
        trunk.append(temp)
        temp = nn.BatchNorm2d(feature_dim, affine=False)
        trunk2.append(temp)
        self.features = nn.Sequential(*trunk)
        self.features2 = nn.Sequential(*trunk2)

        # self._initialize_weights()

    def forward(self, x, checkout=False):
        InvertedResidual.checkout = checkout
        if checkout:
            x = self.features2(x)
        else:
            x = self.features(x)
        x = x.view(x.shape[0], -1)
        return x

    def get_feature(self, input):
        return self.features(input)

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


class ArcMarginProduct(nn.Module):
    r"""Implement of large margin arc distance: :
        Args:
            in_features: size of each input sample
            out_features: size of each output sample
            s: norm of input feature
            m: margin

            cos(theta + m)
        """
    def __init__(self, in_features, out_features, s=30.0, m=0.50, easy_margin=False):
        super(ArcMarginProduct, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.s = s
        self.m = m
        self.weight = Parameter(torch.FloatTensor(out_features, in_features))
        nn.init.xavier_uniform_(self.weight)

        self.easy_margin = easy_margin
        self.cos_m = math.cos(m)
        self.sin_m = math.sin(m)
        self.th = math.cos(math.pi - m)
        self.mm = math.sin(math.pi - m) * m

    def forward(self, input, label):
        # --------------------------- cos(theta) & phi(theta) ---------------------------
        cosine = F.linear(F.normalize(input), F.normalize(self.weight))
        sine = torch.sqrt(1.0 - torch.pow(cosine, 2))
        phi = cosine * self.cos_m - sine * self.sin_m
        if self.easy_margin:
            phi = torch.where(cosine > 0, phi, cosine)
        else:
            phi = torch.where(cosine > self.th, phi, cosine - self.mm)
        # --------------------------- convert label to one-hot ---------------------------
        # one_hot = torch.zeros(cosine.size(), requires_grad=True, device='cuda')
        one_hot = torch.zeros(cosine.size(), device=input.device)
        one_hot.scatter_(1, label.view(-1, 1).long(), 1)
        # -------------torch.where(out_i = {x_i if condition_i else y_i) -------------
        output = (one_hot * phi) + ((1.0 - one_hot) * cosine)  # you can use torch.where if your torch.__version__ is 0.4
        output *= self.s
        # print(output)

        return output

class Net(nn.Module):

    def __init__(self, feature_dim, num_classes, num_classes2, trunk_name, pretrained, width_mult=0.5, channel=1):
        super(Net, self).__init__()
        self.trunk = MobileFaceNet(feature_dim, width_mult=width_mult, channel=channel)
        self.metric_fc = ArcMarginProduct(feature_dim, num_classes, s=30, m=0.5, easy_margin=True)
        self.metric_fc2 = ArcMarginProduct(feature_dim, num_classes2, s=30, m=0.5, easy_margin=True)

        if pretrained:
            checkpoint = torch.load(pretrained)
            state_dict = checkpoint['state_dict']
            state_dict_0 = self.state_dict()
            for key0 in state_dict_0:
                hehe = False
                for key in state_dict:
                    if key.endswith(key0):
                        # print 'hehe', key0
                        if state_dict_0[key0].shape == state_dict[key].shape:
                            state_dict_0[key0] = state_dict[key]
                            hehe = True
                # if not hehe:
                    # print 'not hehe', key0, state_dict_0[key0].shape
            self.load_state_dict(state_dict_0)

    def save_trunk(self, path):
        torch.save(self.trunk, path)

    def forward(self, x, y, x2, y2, valid=False):
        x = self.trunk(x)
        x2 = self.trunk(x2, True)
        if valid:
            return x, x2
        else:
            x = self.metric_fc(x, y)
            x2 = self.metric_fc2(x2, y2)
            return x, x2
    def forward_and_feature(self, x, y, x2, y2):
        f1 = self.trunk(x)
        f2 = self.trunk(x2, True)
        x = self.metric_fc(f1, y)
        x2 = self.metric_fc2(f2, y2)

        return x, x2, f1, f2

    def get_feature(self, x):
        return self(x, 0, x, 0, True)[0]