from pixtalks.Model.mobilefacenet import MobileFaceNet
import pixtalks as pt
from pixtalks import backend as P
from pixtalks import nn

class KeypointNet(nn.Module):

    def __init__(self):
        super(KeypointNet, self).__init__()

        self.feature = nn.Sequential(MobileFaceNet(input_channel=1, first_channel=32,
                                                   last_channel=64, feature_dim=20, width_mult=1.5).features[:-3])
        self.conv_1x1 = nn.Conv2d(96, 20, 1)

        self.conv_XY = nn.Conv2d(5, 5, 1)
        self.conv_offset = nn.Conv2d(10, 10, 1)
        self.conv_depth = nn.Conv2d(5, 5, 1)
        # self.conv_1x1_depth = nn.Conv2d(64, 5, 1)


    def forward(self, input):
        feature = self.feature(input)
        # print('feature', feature.shape)
        output = P.sigmoid(self.conv_1x1(feature))
        # print(output.shape)
        XY = self.conv_XY(output[:, :5])
        xy_offset = self.conv_offset(output[:, 5:15])
        depth = self.conv_depth(output[:, 15:])
        return XY, xy_offset, depth

    def keypoint(self, img, n_H, n_W):
        batch = img.size(0)
        XY, xy_offset, depths = self(img)
        # print(';XY', XY)
        argmax = P.argmax(XY.view(batch, 5, -1), dim=-1)
        # print('argmax', argmax)
        u_prime = argmax // 6
        v_prime = argmax % 6

        # print('uv_prime', u_prime, v_prime)

        xy_offset = xy_offset.view(batch, 5, 2, -1)
        depths = depths.view(batch, 5, -1)
        offset = P.empty((batch, 5, 2), device=img.device)
        depth = P.empty((batch, 5), device=img.device)
        for n, arg in enumerate(argmax):
            for m, a in enumerate(arg):
                offset[n, m] = xy_offset[n, m, :, a]
                depth[n, m] = depths[n, m, a]

        # print(offset)

        u = ((u_prime.float() + offset[..., 0]) * n_H).long().unsqueeze(-1)
        v = ((v_prime.float() + offset[..., 1]) * n_W).long().unsqueeze(-1)

        uv = P.cat([u, v], dim=-1)
        return uv, depth

if __name__ == '__main__':
    model = KeypointNet()
    input = P.rand(128, 1, 112, 96)
    XY, xy_offset = model(input)

    print((XY.shape, xy_offset.shape))