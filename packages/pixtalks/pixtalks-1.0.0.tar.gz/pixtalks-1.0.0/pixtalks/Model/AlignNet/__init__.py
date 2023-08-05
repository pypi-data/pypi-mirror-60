import torch.nn as nn
from pixtalks.Model.mobilefacenet import MobileFaceNet_oldversion as MobileFaceNet
from pixtalks.Model.AlignNet import Quarter
import torch.nn.functional as F
import torch

class AlignNet(nn.Module):

    def __init__(self, feature_dim, width_mult):
        super(AlignNet, self).__init__()

        self.features = MobileFaceNet(input_channel=1, first_channel=16, last_channel=64, feature_dim=feature_dim, width_mult=width_mult,
                                      GDC_kernel_size=(7, 6))

        self.rotlayer1 = Quarter.Fc_bn_dropout(feature_dim, 64, 0.3)

        # self.rotlayer2 = Quarter.Fc_bn_dropout(64, 32, 0.3)

        self.rotlayer3 = Quarter.Linear_bn_relu_linear(64, 16, 4)
        # self.rotlayer3 = nn.Linear(64, 4)

        self.translayer1 = Quarter.Fc_bn_dropout(feature_dim, 64, 0.3)

        # self.translayer2 = Quarter.Fc_bn_dropout(64, 32, 0.3)

        self.translayer3 = Quarter.Linear_bn_relu_linear(64, 16, 3)
        # self.translayer3 = nn.Linear(64, 3)

    def forward(self, x):
        batch = x.size(0)

        feature_net = self.features(x)
        feature_net = feature_net.view(batch, -1)
        # print(feature_net.shape)
        net = self.rotlayer1(feature_net)
        # net = self.rotlayer2(net)

        quaterion = self.rotlayer3(net)
        quaterion = F.normalize(quaterion)

        """ 
            Transform Matrix Regression
        """

        norm = quaterion.norm(p=2, dim=1, keepdim=True)
        quaterion = quaterion.div(norm.expand_as(quaterion))
        rot_matrix = Quarter.quaterion2rotmatrix(quaterion)

        """
            Translation Regression
        """

        net = self.translayer1(feature_net)
        # net = self.translayer2(net)
        translation = self.translayer3(net)

        return rot_matrix, translation

class AlignNet_v2(nn.Module):

    def __init__(self, feature_dim, width_mult):
        super(AlignNet_v2, self).__init__()

        self.features = MobileFaceNet(input_channel=1, first_channel=16, last_channel=64, feature_dim=feature_dim, width_mult=width_mult,
                                      GDC_kernel_size=(7, 6))

        self.rotlayer1 = Quarter.Fc_bn_dropout(feature_dim, 64, 0.3)

        # self.rotlayer2 = Quarter.Fc_bn_dropout(64, 32, 0.3)

        # self.rotlayer3 = Quarter.Linear_bn_relu_linear(64, 16, 4)
        self.rotlayer3 = nn.Linear(64, 4)

        self.translayer1 = Quarter.Fc_bn_dropout(feature_dim, 64, 0.3)

        # self.translayer2 = Quarter.Fc_bn_dropout(64, 32, 0.3)

        # self.translayer3 = Quarter.Linear_bn_relu_linear(64, 16, 3)
        self.translayer3 = nn.Linear(64, 3)

    def forward(self, x):
        batch = x.size(0)

        feature_net = self.features(x)
        feature_net = feature_net.view(batch, -1)
        # print(feature_net.shape)
        net = self.rotlayer1(feature_net)
        # net = self.rotlayer2(net)

        quaterion = self.rotlayer3(net)
        quaterion = F.normalize(quaterion)

        """ 
            Transform Matrix Regression
        """

        norm = quaterion.norm(p=2, dim=1, keepdim=True)
        quaterion = quaterion.div(norm.expand_as(quaterion))
        rot_matrix = Quarter.quaterion2rotmatrix(quaterion)

        """
            Translation Regression
        """

        net = self.translayer1(feature_net)
        # net = self.translayer2(net)
        translation = self.translayer3(net)

        return rot_matrix, translation