from pixtalks.Model.mobilefacenet import MobileFaceNet
from pixtalks.Model.AutoEndoder import ConvEncoder
from pixtalks import nn
from pixtalks.Model.DCGAN import generator

# self.Distribute = self.Distribute
# self.Decoder = self.Decoder

class VAE(nn.Module):

    def __init__(self):
        super(VAE, self).__init__()

        self.Distribute = nn.Sequential(ConvEncoder(128), nn.Linear(128, 2))
        self.Decoder = generator(128)

