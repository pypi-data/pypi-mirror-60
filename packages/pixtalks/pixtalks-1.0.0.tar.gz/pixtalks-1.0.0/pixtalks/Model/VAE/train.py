from pixtalks.Model.VAE import VAE
from pixtalks import nn
from pixtalks import optim
from pixtalks.Trainer.VAETrainer import VAETrainer
from pixtalks import backend as P
import pixtalks as pt
import numpy as np
import random
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
    # array = pt.Array(net)[0]
    # array = cv.resize(array, (128, 128))
    return net
    # print(array.shape)
    # return pt.Tensor(array).unsqueeze(0)

if __name__ == '__main__':
    model = VAE()
    op = optim.SGD(model.parameters(), lr=0.01)

    dataloader = pt.DataLoader.ImageLoader(get_path_label,
                                           data_root='/media/dj/DJ_Backups/',
                                           list_filename='/home/dj/anaconda3/envs/python2/lib/python2.7/site-packages/pixtalks/Model/LivenessNet/3d_liveness_train.txt',
                                           # data_root='/media/dj/dj_502/zhilin/liveness-speckle-data/train',
                                           # list_filename='/media/dj/dj_502/zhilin/liveness-speckle-data/train/train.txt',
                                           image_size=(1, 112, 96), dtype=P.float32,
                                           Aug_Function=Aug_Function,
                                           shuffle=True, validation_ratio=0.05,
                                           test_ratio=0.001)
                                           # test_data_list_filename='/media/dj/DJ_Backups/3D_FR_Data/Face123_Test_Dist/test.txt',
                                           # test_data_root='/media/dj/DJ_Backups/3D_FR_Data/Face123_Test_Dist/')
                                           # test_data_list_filename='3d_liveness_test.txt',
                                           # test_data_root='/home/dj/Downloads/zhilin/liveness-depth-image/deploy')
                                           # test_data_list_filename='toufa_test.txt',
                                           # test_data_root='/home/dj/Downloads/zhilin/liveness-depth-image/deploy')
    gan_trainer = VAETrainer(op, 6*7*6, nn.MSELoss(), model=model, save_path='model.pkl',
                             dataloader=dataloader, resume='model.pkl', version_name='last_version')
    # gan_trainer.evaluate(128, 'cuda')
    gan_trainer.fit(2, 128, 'cuda', eval_per_step=1000, save_per_step=1000)
