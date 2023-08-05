from pixtalks.Model.mobilefacenet import MobileFaceNet
from pixtalks import nn
from pixtalks import P
from pixtalks import F
from pixtalks.Model.DCGAN import generator

# self.Distribute = self.Distribute
# self.Decoder = self.Decoder

class con_relu_bn(nn.Module):

    def __init__(self, inp_channels, oup_channels, kernel_size, padding=0, stride=1):
        super(con_relu_bn, self).__init__()

        self.sequential = nn.Sequential(nn.Conv2d(inp_channels, oup_channels, kernel_size=kernel_size,
                                                  padding=padding, stride=stride),
                                        nn.LeakyReLU(0.2),
                                        nn.BatchNorm2d(oup_channels))

    def forward(self, input):
        return self.sequential(input)

class ConvEncoder(nn.Module):

    def __init__(self, feature_dim):
        super(ConvEncoder, self).__init__()

        self.seq = nn.Sequential(con_relu_bn(1, 16, 3, 1),
                                 con_relu_bn(16, 64, 3, 1),
                                 con_relu_bn(64, 128, 3, 1, stride=2),
                                 con_relu_bn(128, 128, 3, 1),
                                 con_relu_bn(128, 256, 3, 1, stride=2),
                                 con_relu_bn(256, 512, 3, 1),
                                 con_relu_bn(512, 256, 3, 1, stride=2),
                                 con_relu_bn(256, 256, 3, 1),
                                 con_relu_bn(256, 256, 3, 1, stride=2),
                                 con_relu_bn(256, 256, (7, 6)),
                                 nn.Conv2d(256, feature_dim, kernel_size=1),
                                 nn.BatchNorm2d(feature_dim))

    def forward(self, input):
        batch = input.size(0)

        return self.seq(input).view(batch, -1)

class AutoEncoder(nn.Module):

    def __init__(self):
        super(AutoEncoder, self).__init__()

        self.Encoder = nn.Sequential(ConvEncoder(128),
                                     nn.Linear(128, 6*7*6))
        self.Decoder = generator(128, inp_channels=6, activation=F.tanh)
        self.Segment = generator(128, inp_channels=6, activation=F.tanh)

    def forward(self, input):
        code = self.Encoder(input).view(-1, 6, 7, 6)
        decode = self.Decoder(code)
        # segment = self.Segment(code)
        return decode
