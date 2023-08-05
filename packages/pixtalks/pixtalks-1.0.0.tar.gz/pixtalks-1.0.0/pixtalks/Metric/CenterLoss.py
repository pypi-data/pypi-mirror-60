import torch
from pixtalks.Metric import cosine_distance
from torch.autograd import Variable


class CenterLoss(torch.nn.Module):
    def __init__(self, num_classes, feat_dim, loss_weight=1.0):
        super(CenterLoss, self).__init__()
        self.num_classes = num_classes
        self.feat_dim = feat_dim
        self.loss_weight = loss_weight
        self.centers = torch.nn.Parameter(torch.randn(num_classes, feat_dim))
        self.use_cuda = True
        self.cuda()

    def forward(self, y, feat):
        if self.use_cuda:
            hist = Variable(
                torch.histc(y.cpu().data.float(), bins=self.num_classes, min=0, max=self.num_classes) + 1).cuda()
        else:
            hist = Variable(torch.histc(y.data.float(), bins=self.num_classes, min=0, max=self.num_classes) + 1)

        centers_count = hist.index_select(0, y.long())

        batch_size = feat.size()[0]
        feat = feat.view(batch_size, 1, 1, -1).squeeze()
        if feat.size()[1] != self.feat_dim:
            raise ValueError("Center's dim: {0} should be equal to input feature's dim: {1}".format(self.feat_dim,
                                                                                                    feat.size()[1]))
        centers_pred = self.centers.index_select(0, y.long())
        # diff = feat - centers_pred
        # loss = self.loss_weight * 1 / 2.0 * (diff.pow(2).sum(1) / centers_count).sum()
        loss = 1.0 - cosine_distance(feat, centers_pred).mean()
        return loss

    def cuda(self, device_id=None):
        self.use_cuda = True
        return self._apply(lambda t: t.cuda(device_id))
