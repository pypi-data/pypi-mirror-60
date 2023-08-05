from pixtalks import nn
from pixtalks import backend as P
import pixtalks as pt
from pixtalks import optim
from pixtalks.Model.DCGAN import DCGAN
from pixtalks.Model.StyleGAN import StyleGAN
from pixtalks.Trainer.GenerativeAdversarialTrainer import GenerativeAdversarialTrainer
import random
import numpy as np
import cv2 as cv


def get_path_label(line):
    path, label = line.split()
    label = int(label)
    if label != 1:
        label = random.choice(np.arange(1, 10))
        label = 1
    else:
        label = 0
    return path, int(label)

def Aug_Function(img, **kwargs):
    # print(img.shape)

    net = img/256.
    net -= 0.5
    net *= 2
    # print(net.shape)
    array = pt.Array(net)[0]
    array = cv.resize(array, (128, 128))
    # return net
    # print(array.shape)
    return pt.Tensor(array).unsqueeze(0)


if __name__ == '__main__':
    # model = DCGAN(250, 64)
    model = StyleGAN()
    opG = optim.Adam(model.G.parameters(), lr=0.001)
    opD = optim.Adam(model.D.parameters(), lr=0.001)

    dataloader = pt.DataLoader.ImageLoader(get_path_label,
                                           data_root='/media/dj/DJ_Backups/',
                                           list_filename='3d_liveness_train.txt',
                                           # data_root='/media/dj/dj_502/zhilin/liveness-speckle-data/train',
                                           # list_filename='/media/dj/dj_502/zhilin/liveness-speckle-data/train/train.txt',
                                           image_size=(1, 128, 128), dtype=P.float32,
                                           Aug_Function=Aug_Function,
                                           shuffle=True, validation_ratio=0.05,
                                           test_ratio=0.001)
                                           # test_data_list_filename='/media/dj/DJ_Backups/3D_FR_Data/Face123_Test_Dist/test.txt',
                                           # test_data_root='/media/dj/DJ_Backups/3D_FR_Data/Face123_Test_Dist/')
                                           # test_data_list_filename='3d_liveness_test.txt',
                                           # test_data_root='/home/dj/Downloads/zhilin/liveness-depth-image/deploy')
                                           # test_data_list_filename='toufa_test.txt',
                                           # test_data_root='/home/dj/Downloads/zhilin/liveness-depth-image/deploy')

    gan_trainer = GenerativeAdversarialTrainer(512, 3, opG, opD, nn.Softplus(), model=model, save_path='model.pkl',
                                               dataloader=dataloader, resume='model.pkl', version_name='last_version')


    gan_trainer.fit(2, 8, 'cuda', eval_per_step=50, save_per_step=50, save_dir='output')
