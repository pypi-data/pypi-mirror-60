from .networks_stylegan import *
from pixtalks import nn

class StyleGAN(nn.Module):

    def __init__(self):
        super(StyleGAN, self).__init__()

        self.G = StyleGenerator(resolution=128)
        self.D = StyleDiscriminator(128)