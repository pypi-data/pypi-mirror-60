import torch.nn as nn
import math
import torch.nn.functional as F


def conv_bn(inp, oup, stride):
    return nn.Sequential(
        nn.Conv2d(inp, oup, 3, stride, 1, bias=False),
        nn.BatchNorm2d(oup),
        nn.ReLU(inplace=True)
    )


def conv_1x1(inp, oup):
    return nn.Conv2d(inp, oup, 1, 1, 0, bias=False)


class LivenessNet(nn.Module):
    def __init__(self, n_label, feature_dim=128):
        super(LivenessNet, self).__init__()
        self.conv1 = conv_bn(1, 8, 2)
        self.conv2 = conv_bn(8, 8, 1)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.conv3 = conv_bn(8, 16, 1)
        self.conv4 = conv_bn(16, 16, 1)
        self.pool2 = nn.MaxPool2d(2, 2)
        self.conv5 = conv_bn(16, 32, 1)
        self.conv6 = conv_bn(32, 32, 1)
        self.pool3 = nn.MaxPool2d(2, 2)
        self.conv7 = conv_bn(32, 64, 1)
        self.conv8 = conv_bn(64, 64, 1)
        self.conv9 = conv_1x1(64, feature_dim)
        self.pool4 = nn.AvgPool2d((7, 6), 1)
        self.linear1 = nn.Linear(feature_dim, n_label)
        # self.linear2 = nn.Linear(32, 2)
        self.feature_dim = feature_dim
        self._initialize_weights()


    def forward(self, x, checkout=False):
        # print(x.shape)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.pool1(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.pool2(x)
        x = self.conv5(x)
        x = self.conv6(x)
        x = self.pool3(x)
        x = self.conv7(x)
        x = self.conv8(x)
        x = self.conv9(x)
        x = self.pool4(x)
        feature = x.view(-1, self.feature_dim)
        # x = self.linear1(x)
        # x = F.sigmoid(x)
        # x = self.linear2(x)
        x = self.linear1(feature)
        # print(x.shape)
        return x, feature

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
