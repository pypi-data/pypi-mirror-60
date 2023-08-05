from pixtalks.Model.mobilefacenet import MobileFaceNet
from pixtalks.Model.mobilefacenet.MobileFaceNet_Relu import MobileFaceNet as MobileFaceNet_Relu
from pixtalks.Metric import ArcMarginProduct
import pixtalks as pt
import torch.nn as nn
import torch.nn.functional as F
import torch
from torch.nn.parameter import Parameter

def GenerateGrid(H, W, batch):
    grid = torch.zeros((batch, H, W, 2))
    for h in range(H):
        for w in range(W):
            grid[:, h, w, 0] = 2.0*w/W - 1
            grid[:, h, w, 1] = 2.0*h/H - 1

    return grid

class STN(nn.Module):

    def __init__(self):
        super(STN, self).__init__()
        self.grid = Parameter(GenerateGrid(112, 96, 1), requires_grad=False)

        self.localization = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=7),
            nn.MaxPool2d(2, 2),
            nn.ReLU(True),
            nn.Conv2d(8, 10, kernel_size=5),
            nn.MaxPool2d(2, 2),
            nn.ReLU(True),
            nn.Conv2d(10, 10, kernel_size=3),
            nn.MaxPool2d(2, 2),
            nn.ReLU(True),
            nn.Conv2d(10, 10, kernel_size=3),
            nn.MaxPool2d(2, 2),
            nn.ReLU(True)
        )
        self.fc_loc = nn.Sequential(
            nn.Linear(10 * 4 * 3, 32),
            nn.ReLU(True),
            nn.Linear(32, 3 * 2),
            nn.Tanh()
        )

        self.fc_loc[2].weight.data.fill_(0)
        self.fc_loc[2].bias.data = torch.FloatTensor([1, 0, 0, 0, 1, 0])

    def forward(self, input):
        net = self.localization(input)
        # print(net.shape)
        net = net.view(-1, 10 * 4 * 3)
        theta = self.fc_loc(net)
        theta = theta.view(-1, 2, 3)

        grid = F.affine_grid(theta, input.size())
        net = F.grid_sample(input, grid, mode='bilinear', padding_mode='border')
        # pt.imshow(grid[0, :, :, 0], grid[0, :, :, 1])
        return net

class FRNet(nn.Module):

    def __init__(self, feature_dim, n_labels):
        super(FRNet, self).__init__()
        self.feature = MobileFaceNet(input_channel=1, first_channel=64, last_channel=512,
                                     feature_dim=128, width_mult=1.0)
        self.arc_face = ArcMarginProduct(feature_dim, n_labels)

    def forward(self, input):
        return self.feature(input)

    def forward_feature_map(self, input):
        return self.feature.forward_feature_map(input)

    def train_forward(self, input, label):
        # print(input.shape)
        feature = self.feature(input)
        predict = self.arc_face(feature, label)

        return feature, predict

class FRNet_Relu(nn.Module):

    def __init__(self, feature_dim, n_labels):
        super(FRNet_Relu, self).__init__()
        self.feature = MobileFaceNet_Relu(input_channel=1, first_channel=64, last_channel=512,
                                     feature_dim=128, width_mult=1.0)
        self.arc_face = ArcMarginProduct(feature_dim, n_labels)

    def forward(self, input):
        return self.feature(input)

    def forward_feature_map(self, input):
        return self.feature.forward_feature_map(input)

    def train_forward(self, input, label):

        feature = self.feature(input)
        predict = self.arc_face(feature, label)

        return feature, predict

class FRNet_STN(nn.Module):

    def __init__(self, feature_dim, n_labels):
        super(FRNet_STN, self).__init__()
        self.stn = STN()
        self.feature = MobileFaceNet(input_channel=1, first_channel=64, last_channel=512,
                                     feature_dim=128, width_mult=1.0)
        self.arc_face = ArcMarginProduct(feature_dim, n_labels)

    def forward(self, input):
        return self.feature(input)

    def train_forward(self, input, label):
        net = self.stn(input)
        feature = self.feature(net)
        predict = self.arc_face(feature, label)

        return feature, predict

