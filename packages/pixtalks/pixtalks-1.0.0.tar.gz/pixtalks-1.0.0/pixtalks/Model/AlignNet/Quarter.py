import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np


def quaterion2rotmatrix(quaterion):
    """
    Convert quaterion To the corresponding rotation matrix.
    Input:
        quaterion: B x 4
    Output:
        rot matrix: B x 4 x 4
    """

    def diag(a, b):
        return 1 - 2 * torch.pow(a, 2) - 2 * torch.pow(b, 2)

    def tr_add(a, b, c, d):
        return 2 * a * b + 2 * c * d

    def tr_sub(a, b, c, d):
        return 2 * a * b - 2 * c * d

    w = quaterion[:, 0]
    x = quaterion[:, 1]
    y = quaterion[:, 2]
    z = quaterion[:, 3]
    # print w,x,y,z
    m = [[diag(y, z), tr_sub(x, y, z, w), tr_add(x, z, y, w)],
         [tr_add(x, y, z, w), diag(x, z), tr_sub(y, z, x, w)],
         [tr_sub(x, z, y, w), tr_add(y, z, x, w), diag(x, y)]]

    return torch.stack([torch.stack(m[i], dim=-1) for i in range(3)], dim=-2)


def Con_bn_relu(in_channel, out_channel, kernel_size):
    return nn.Sequential(nn.Conv2d(in_channel, out_channel, kernel_size),
                         nn.BatchNorm2d(out_channel),
                         nn.ReLU())


def Fc_bn_dropout(in_channel, out_channel, p):
    return nn.Sequential(nn.Linear(in_channel, out_channel),
                         nn.BatchNorm1d(out_channel),
                         nn.ReLU(),
                         nn.Dropout(p))


def Linear_bn_relu_linear(in_channel, out_channel, out_channel_2):
    return nn.Sequential(nn.Linear(in_channel, out_channel),
                         nn.BatchNorm1d(out_channel),
                         nn.ReLU(),
                         nn.Linear(out_channel, out_channel_2))


class align_torch_model(nn.Module):
    def __init__(self):
        super(align_torch_model, self).__init__()

        self.layer1 = Con_bn_relu(1, 64, (1, 3))

        self.layer2 = Con_bn_relu(64, 64, (1, 1))

        self.layer3 = Con_bn_relu(64, 64, (1, 1))

        self.rotlayer1 = Fc_bn_dropout(64, 64, 0.3)

        self.rotlayer2 = Fc_bn_dropout(64, 32, 0.3)

        self.rotlayer3 = Linear_bn_relu_linear(32, 16, 4)

        self.translayer1 = Fc_bn_dropout(64, 64, 0.3)

        self.translayer2 = Fc_bn_dropout(64, 32, 0.3)

        self.translayer3 = Linear_bn_relu_linear(32, 16, 3)

    def forward(self, point_cloud):
        batch_size = point_cloud.size()[0]
        numpoint = point_cloud.size()[1]
        channel = point_cloud.size()[2]

        input_image = torch.reshape(point_cloud, (batch_size, 1, numpoint, channel))
        input_image = input_image.float()

        net = self.layer1(input_image)
        # print net.size()
        net = self.layer2(net)
        # print net.size()
        net = self.layer3(net)
        # print net.size()
        global_feat = nn.MaxPool2d((net.size()[2], 1))(net)
        feature_net = torch.reshape(global_feat, (batch_size, -1))
        # print feature_net.size()

        """ 
        Transform Matrix Regression
        """

        net = self.rotlayer1(feature_net)
        # print net.size()
        net = self.rotlayer2(net)
        # print net.size()
        quaterion = self.rotlayer3(net)
        quaterion = F.normalize(quaterion)
        # print net.size()
        norm = quaterion.norm(p=2, dim=1, keepdim=True)
        quaterion = quaterion.div(norm.expand_as(quaterion))
        rot_matrix = quaterion2rotmatrix(quaterion)

        """
        Translation Regression
        """

        net = self.translayer1(feature_net)
        net = self.translayer2(net)
        translation = self.translayer3(net)

        return rot_matrix, translation