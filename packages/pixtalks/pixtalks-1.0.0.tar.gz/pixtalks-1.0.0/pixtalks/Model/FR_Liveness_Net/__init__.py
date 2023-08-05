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

        feature = self.feature(input)
        predict = self.arc_face(feature, label)

        return feature, predict

class FRNet_Relu(nn.Module):

    def __init__(self, feature_dim, n_labels, liveness_dim, width_mult=1.0):
        super(FRNet_Relu, self).__init__()
        self.feature = MobileFaceNet_Relu(input_channel=1, first_channel=64, last_channel=512,
                                          feature_dim=128, width_mult=width_mult)
        self.liveness = nn.Linear(128, liveness_dim)
        self.arc_face = ArcMarginProduct(feature_dim, n_labels)

    def forward(self, input):
        return self.feature(input)

    def forward_feature_map(self, input):
        return self.feature.forward_feature_map(input)

    def train_forward(self, input, label):

        feature = self.feature(input)
        predict = self.arc_face(feature, label)
        predict_liveness = self.liveness(feature)

        return feature, predict, predict_liveness


