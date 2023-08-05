from pixtalks.Model.ConditionalAutoEncoder import ConditionalAutoEncoder

from pixtalks import nn
from pixtalks import optim
from pixtalks.Trainer.ConditionalAutoEncoderTrainer import ConditionalAutoEncoderTrainer
from pixtalks import backend as P
import pixtalks as pt
import numpy as np
import random
import cv2 as cv


def get_path_label(line):
    path, label = line.split()
    label = int(label)
    return path, int(label)

def Aug_Function(img, **kwargs):
    # print(img.shape)
    # pt.imshow(img.view(112, 96)/255., pt.FaceClean(img.view(112, 96)/255., 128 / 255., scale=255.))
    # return pt.FaceClean(img.view(112, 96)/255., 128 / 255., scale=255.)
    net = img/256.
    # net = pt.FaceClean(net, 128 / 256., scale=256.)
    net -= 0.5
    net *= 2
    # print(net)
    # print(net.shape)
    # array = pt.Array(net)[0]
    # array = cv.resize(array, (128, 128))
    return net
    # print(array.shape)
    # return pt.Tensor(array).unsqueeze(0)

if __name__ == '__main__':
    model = ConditionalAutoEncoder(128, 2742)
    model.cuda()
    ops = [optim.Adam(list(model.Encoder.parameters()) + list(model.Decoder.parameters()), lr=0.01),
           optim.Adam(model.Classifier.parameters(), lr=0.01)]

    dataloader = pt.DataLoader.ImageLoader(get_path_label,
                                           data_root='/media/dj/DJ_Backups/3D_FR_Data/',
                                           list_filename='/media/dj/DJ_Backups/3D_FR_Data/train.txt',
                                           # data_root='/media/dj/dj_502/zhilin/liveness-speckle-data/train',
                                           # list_filename='/media/dj/dj_502/zhilin/liveness-speckle-data/train/train.txt',
                                           image_size=(1, 112, 96), dtype=P.float32,
                                           Aug_Function=Aug_Function,
                                           shuffle=True, validation_ratio=0.05,
                                           # test_ratio=0.01)
                                           test_data_root='/media/dj/DJ_Backups/3D_FR_Data/',
                                           test_data_list_filename='/media/dj/DJ_Backups/3D_FR_Data/test.txt')
    print(dataloader._summary())
    gan_trainer = ConditionalAutoEncoderTrainer(model, ops, nn.MSELoss(),
                                                dataloader=dataloader)
    fr_state_dice = P.load('/home/dj/anaconda3/envs/python2/lib/python2.7/site-packages/pixtalks/Model/FRNet_v2/fr_model_clean_0.4878_953.pkl')
    # en_state_dict = P.load('/home/dj/anaconda3/envs/python2/lib/python2.7/site-packages/pixtalks/Model/AutoEndoder/encoder.pkl')
    # de_state_dict = P.load('/home/dj/anaconda3/envs/python2/lib/python2.7/site-packages/pixtalks/Model/AutoEndoder/decoder.pkl')
    gan_trainer.Classifier.load_state_dict(fr_state_dice)
    # gan_trainer.Encoder.load_state_dict(en_state_dict)
    # gan_trainer.Decoder.load_state_dict(de_state_dict)
    # gan_trainer._load('model_best')

    # P.save(gan_trainer.model.state_dict(), 'CAE_FR_model_best.pkl')
    gan_trainer.resume('model.pkl', ignore=[gan_trainer.Classifier])
    # print(gan_trainer.evaluate(128, 'cuda', n_labels=300))
    gan_trainer.fit(20, 128, 'model.pkl', 'cuda', eval_per_step=50, save_per_step=50, n_labels=300)

