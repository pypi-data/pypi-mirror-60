from pixtalks.Model.FRNet_v2 import FRNet
from pixtalks.Metric.ArcFace import ArcMarginProduct
from pixtalks.Model.AutoEndoder import ConvEncoder
from pixtalks.Model.mobilefacenet import MobileFaceNet
from pixtalks import nn
from pixtalks.Model.DCGAN import generator

# self.Distribute = self.Distribute
# self.Decoder = self.Decoder

class ConditionalAutoEncoder(nn.Module):

    def __init__(self, feature_dim, n_labels):
        super(ConditionalAutoEncoder, self).__init__()

        self.Encoder = nn.Sequential(ConvEncoder(feature_dim), nn.Linear(feature_dim, 6*7*6))
        self.Decoder = generator(128)
        # self.Classifier = ArcMarginProduct(3*7*6, n_labels)
        self.Classifier = FRNet(feature_dim, n_labels)

    def forward(self, input):
        code = self.Encoder(input)
        decode = self.Decoder(code.view(-1, 3, 7, 6))
        pred = self.Classifier(decode)

        return decode, pred

    def feature(self, input):
        code = self.Encoder(input)
        decode = self.Decoder(code.view(-1, 6, 7, 6))
        feature = self.Classifier.feature(decode/2. + 0.5)

        return feature

    def feature_decode(self, input):
        code = self.Encoder(input)
        decode = self.Decoder(code.view(-1, 3, 7, 6))
        feature = self.Classifier.feature(decode/2. + 0.5)

        return feature, decode
