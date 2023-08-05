import torch.nn as nn


def conv_bn(inp, oup, kernel_size, stride, padding):
    temp = nn.Conv2d(inp, oup, kernel_size, stride, padding, bias=False)
    return nn.Sequential(
        temp,
        nn.BatchNorm2d(oup),
        nn.ReLU6(inplace=True)
    )

def conv_dw_bn(dim, kernel_size, stride, padding):
    temp = nn.Conv2d(dim, dim, kernel_size, stride, padding, groups=dim, bias=False)
    return nn.Sequential(
        temp,
        nn.BatchNorm2d(dim),
        nn.ReLU6(inplace=True)
    )

def GDConv(dim, kernel_size):
    temp = nn.Conv2d(dim, dim, kernel_size, groups=dim, bias=False)
    return nn.Sequential(
        temp,
        nn.BatchNorm2d(dim)
    )

def conv_1x1_bn(inp, oup):
    temp = nn.Conv2d(inp, oup, 1, 1, 0, bias=False)
    return nn.Sequential(
        temp,
        nn.BatchNorm2d(oup),
        nn.ReLU6(inplace=True)
    )

class InvertedResidual(nn.Module):

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
                temp1,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU6(inplace=True),
                temp2,
                nn.BatchNorm2d(oup),
            )
        else:
            temp1 = nn.Conv2d(inp, hidden_dim, 1, 1, 0, bias=False)
            temp2 = nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, groups=hidden_dim, bias=False)
            temp3 = nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False)
            self.conv = nn.Sequential(
                temp1,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU6(inplace=True),
                temp2,
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU6(inplace=True),
                temp3,
                nn.BatchNorm2d(oup),
            )

    def forward(self, x):
        conv = self.conv
        if self.use_res_connect:
            return x + conv(x)
        else:
            return conv(x)


from . import AlignNet

from . import FRNet_v1
from . import FRNet_v2
# from . import FRNet_v3
from . import LivenessNet

from .mobilefacenet import *
from .ClassifyNet import *
