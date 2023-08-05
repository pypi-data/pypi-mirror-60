import pixtalks as pt
import torch.nn as nn

class ClassifyNet(nn.Module):

    def __init__(self, feature_net, feature_dim, n_labels):
        super(ClassifyNet, self).__init__()

        self.feature = feature_net
        self.classify = nn.Linear(feature_dim, n_labels)

    def forward(self, input):
        feature = self.feature(input)
        return self.classify(feature)