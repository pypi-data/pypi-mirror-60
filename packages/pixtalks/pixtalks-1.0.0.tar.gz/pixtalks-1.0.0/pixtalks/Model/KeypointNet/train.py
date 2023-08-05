from pixtalks.Model.KeypointNet import KeypointNet
from pixtalks import backend as P
from pixtalks import nn
from pixtalks import optim
import pixtalks as pt
from pixtalks.DataLoader import DataLoader
from pixtalks.Trainer import Trainer
import os
import numpy as np
import cv2 as cv

dirname = os.path.dirname(pt.__file__)
standardface = pt.loadtxt(os.path.join(dirname, 'standard_keypoint.txt'))


def draw(image, u, v, size, color):
    for i, c in enumerate(color):
        image[max([u-size, 0]):u+size,  max([v-size, 0]):v+size, i] = c

def clamp(x, min, max):
    if x < min:
        return min
    elif x > max:
        return max
    else:
        return x

def small(x):
    return x - int(x)

def GetKP(pc, kp_filename):

    if True:
        # print(kp_filename)
        kp_3d = pt.loadtxt(kp_filename)
        area = kp_3d[:, 0] != -1
        R, T = pt.ICP_Transorm_Matrix(kp_3d[area], standardface[area])
        pc[:] = P.matmul(pc, R) + T
        kp_3d = P.matmul(kp_3d, R) + T

        #增广
        x, y, z = pt.math.GetRandomSphereVector(1)[0]
        angle = np.random.uniform(-20, 20)
        Aug_R = pt.math.GetRotateMatrix(x, y, z, angle)
        Aug_T = pt.Tensor(np.random.uniform(-10, 10, size=(3,))).float()
        pc[:] = P.matmul(pc, Aug_R, ) + Aug_T
        kp_3d = P.matmul(kp_3d, Aug_R) + Aug_T

        kp_u = -kp_3d[:, 1] * 96./180 + 112//2
        kp_v = kp_3d[:, 0] * 96./180 + 96//2
        kp_z = (kp_3d[:, 2] - 128.) / 256

        return pc, kp_3d, P.cat([kp_u.view(5, 1), kp_v.view(5, 1)], dim=1), 1 + kp_z
    else:
        return None, None, None, None



class Generator(DataLoader):

    def __init__(self, n_H, n_W, **kwargs):
        super(Generator, self).__init__(**kwargs)

        self.n_H = n_H
        self.n_W = n_W

    def _get_data(self, data_root, line, **kwargs):
        path = line.replace('\n', '')

        pc_filename = os.path.join(data_root, path)
        kp_filename = pc_filename.replace('.txt', '_keypoint.txt')

        pc = pt.loadtxt(pc_filename, length=3)
        pc, kp, kp_uv, kp_z = GetKP(pc, kp_filename)

        if kp is None:
            return None

        # print('kpz', kp_z)
        depth_map = pt.GetDepthMap(pc, 'direct')
        XY = P.zeros(5, 7, 6)
        offset = P.full((10, 7, 6), -1)
        depth = P.full((5, 7, 6), -1)
        for n, (u, v) in enumerate(kp_uv):
            try:
                u_prime = int(u // self.n_H)
                v_prime = int(v // self.n_W)

                offset_u = u / self.n_H - u_prime
                offset_v = v / self.n_W - v_prime

                XY[n, u_prime, v_prime] = 1
                depth[n, u_prime, v_prime] = kp_z[n]

                offset[2 * n, u_prime, v_prime] = offset_u
                offset[2 * n + 1, u_prime, v_prime] = offset_v

                if offset_u < 0.25:
                    uu = clamp(u_prime - 1, 0, 7 - 1)
                    vv = v_prime
                    XY[n, uu, vv] = -1
                    offset[2 * n, uu, vv] = 1
                elif offset_u > 0.75:
                    uu = clamp(u_prime + 1, 0, 7 - 1)
                    vv = v_prime
                    XY[n, uu, vv] = -1
                    offset[2 * n, uu, vv] = 0
                if offset_v < 0.25:
                    uu = u_prime
                    vv = clamp(u_prime - 1, 0, 6 - 1)
                    XY[n, uu, vv] = -1
                    offset[2 * n + 1, uu, vv] = 1
                elif offset_v > 0.75:
                    uu = u_prime
                    vv = clamp(u_prime + 1, 0, 6 - 1)
                    XY[n, uu, vv] = -1
                    offset[2 * n + 1, uu, vv] = 0


            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                return None

        # print('XY')
        # print(XY)
        # print(offset)
        # pt.imshow(depth_map)

        return {'img': depth_map, 'XY': XY, 'xy_offset': offset, 'depth': depth}

class KPNet_Trainer(Trainer):

    def __init__(self, model, optimizer, **kwargs):
        super(KPNet_Trainer, self).__init__(**kwargs)

        self.model = model
        self.optimizer = optimizer

    def forward(self, data, forward_mode, **kwargs):
        img = data['img']
        XY = data['XY']
        xy_offset = data['xy_offset']
        depth = data['depth']

        XY_pred, xy_offset_pred, depth_pred = self.model(img)

        if forward_mode == 'train':
            diff = P.pow(XY - XY_pred, 2)
            loss_XY_one = P.mean(P.where(XY == 1, diff, P.zeros(1, device=img.device))) * 42
            loss_XY_zero = P.mean(P.where(XY == 0, diff, P.zeros(1, device=img.device)))
            loss_XY = loss_XY_one + loss_XY_zero

            temp_xy_offset = P.where(xy_offset == -1, P.full((1,), -1).to(img.device), xy_offset_pred)
            loss_xy_offset = 100 * P.mean(P.pow(xy_offset - temp_xy_offset, 2))

            temp_depth = P.where(depth == -1, P.full((1,), -1).to(img.device), depth_pred)
            loss_depth = 100 * P.mean(P.pow(depth - temp_depth, 2))

            loss = loss_XY + loss_xy_offset + loss_depth
            self.update(self.optimizer, loss)
            return {'loss': loss.item(), 'L_XY': loss_XY.item(), 'L_off': loss_xy_offset.item(), 'L_d': loss_depth.item()}
        else:
            return {'img': img, 'XY': XY, 'xy_offset': xy_offset, 'depth': depth}

    def evaluate(self, batch_size, device, **kwargs):
        n_H = kwargs.get('n_H')
        n_W = kwargs.get('n_W')
        for data in self._evaluate(batch_size, device, **kwargs):
            images = data['img']

            # XY = data['XY']
            # xy_offset = data['xy_offset']
            depth = data['depth']
            # print('e_XY', XY)
            # print('e_offset', xy_offset)
            uvss, depth_pred = self.model.keypoint(images, n_H, n_W)
            print(depth_pred)
            # print('depth', P.where(depth != -1, depth - depth_pred, P.ones(1, device=device)))

            for image, uvs in zip(images, pt.Array(uvss)):
                # print(image)
                image = pt.Array(image)
                image = np.concatenate([image]*3, axis=0).transpose(1, 2, 0)
                for u, v in uvs:
                    # print(image.shape)
                    print(u, v)
                    draw(image, u, v, 2, (1, 0, 0))
                image = pt.Tensor(image)
                pt.imshow(image)



if __name__ == '__main__':
    count_depth = []
    model = KeypointNet()
    model.cuda()
    optimizer = optim.Adam(model.parameters(), lr=0.1)

    generator = Generator(n_H=112/7, n_W=96/6,
                          data_root='/media/dj/dj_502/FuShi1_raw/RAW/',
                          list_filename='/media/dj/dj_502/FuShi1_raw/RAW/train.txt',
                          inputs={'img': (P.float32, (1, 112, 96)), 'XY': (P.float32, (5, 7, 6)),
                                  'xy_offset': (P.float32, (10, 7, 6)), 'depth': (P.float32, (5, 7, 6))},
                          shuffle=True,
                          validation_ratio=0.05, test_ratio=0.1)
    print(generator)
    trainer = KPNet_Trainer(model=model, optimizer=optimizer, dataloader=generator)
    trainer.resume('model.pkl')
    trainer.evaluate(1, 'cuda', n_H=112/7, n_W=96/6)
    # trainer.fit(10, 64, 'model.pkl', 'cuda', save_per_step=30)

    # count_depth = P.cat(count_depth, dim=0)
    # print(count_depth.shape)
    # mean_face = P.mean(count_depth, dim=0).squeeze()
    #
    # pt.imsave('mean_face.png', mean_face*256)
    # std_face = P.std(count_depth, dim=0).squeeze()
    # pt.savetensor('std_face.npy', std_face)
    # # print(std_face.shape)
    # pt.imshow(std_face, mean_face)