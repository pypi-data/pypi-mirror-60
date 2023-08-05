from pixtalks.DataLoader.MultiDataLoader import MultiDataLoader
import pixtalks as pt
import pixtalks.Trainer as Train
from pixtalks import backend as P
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import torch.nn as nn
import numpy as np
import torch.optim as op
import cv2 as cv
from pixtalks.Model.LivenessNet import LivenessNet

NLABEL = 10

def blanknumber(img):
    return P.where(img == 128/255., P.ones(1).to(img.device), P.zeros(1).to(img.device)).sum()

class Model(nn.Module):

    def __init__(self):
        super(Model, self).__init__()

        self.feature = pt.Model.MobileFaceNet(input_channel=1)
        self.classifier = nn.Linear(1536, NLABEL)

    def forward(self, input):
        batch = input.size(0)
        x = self.feature(input)
        x = x.view(batch, -1)
        x = self.classifier(x)

        return x

class ClassifyTrainer(Train.Trainer):

    def __init__(self, model, nlabels, optimizer, loss_function, **kwargs):
        super(ClassifyTrainer, self).__init__(**kwargs)

        self.model = model
        self.nlabels = nlabels
        self.optimizer = optimizer

        load_optimizer = kwargs.get('load_optimizer')
        if load_optimizer is not None and load_optimizer and 'optimizer' in self.checkpoint.keys():
            self.optimizer.load_state_dict(self.checkpoint['optimizer'])

        self.loss_function = loss_function

    def forward(self, data, forward_mode, **kwargs):
        x = data['x']
        y = data['y']
        predict, feature = self.model(x)

        if forward_mode == 'train':
            loss = self.loss_function(predict, y)
            self.update(self.optimizer, loss)
            return {'loss': loss}
        else:
            prob = P.nn.functional.softmax(predict, dim=1)
            return {'y': y, 'predict': prob, 'feature': feature, 'x': x}

    def evaluate(self, batch_size, device, **kwargs):
        real = []
        fake = []
        real_features = []
        fake_features = []
        count = 0

        real_count = 0
        fake_count = 0

        N = 0
        for forward_test in self._evaluate(batch_size, device, **kwargs):
            ys = forward_test['y']
            predicts = forward_test['predict']
            features = forward_test['feature']
            xs = forward_test['x']

            for y, p, feature, x in zip(ys, predicts, features, xs):
                p = p[0]
                if y.item() == 0 and p < 0.8:
                    # print(y, p)
                    # pt.imshow(x.squeeze())
                    pass


                if p.item() > 0.98:
                    count += 1
                N += 1
                if y.item() == 0:
                    real.append(p)
                    real_features.append(feature.view(1, -1))
                else:
                    fake.append(p)
                    fake_features.append(feature.view(1, -1))

        # real_features = P.cat(real_features, dim=0)
        # fake_features = P.cat(fake_features, dim=0)
        # features = P.cat([real_features, fake_features], dim=0).cpu().detach().numpy()
        # labels = P.cat([P.zeros(len(real_features)), P.zeros(len(fake_features))], dim=0)
        # pca_features = pt.Evaluate.PCA(features, 3)

        fake = P.Tensor(fake)
        real = P.Tensor(real)
        print('fake', P.sort(fake)[0][-500:])
        print('real', P.sort(real)[0][:500])
        print('count(>=0.98)', count, N, float(count)/N)

        # fig = plt.figure()
        # ax = Axes3D(fig)
        # ax.scatter(pca_features[:len(real_features), 0], pca_features[:len(real_features), 1],
        #            pca_features[:len(real_features), 2], c='b', label='Real')
        #
        # ax.scatter(pca_features[len(real_features):, 0], pca_features[len(real_features):, 1],
        #            pca_features[len(real_features):, 2], c='r', label='Fake')
        # ax.legend(loc='best')
        # ax.set_zlabel('Z', fontdict={'size': 15, 'color': 'red'})
        # ax.set_ylabel('Y', fontdict={'size': 15, 'color': 'red'})
        # ax.set_xlabel('X', fontdict={'size': 15, 'color': 'red'})
        #
        # plt.show()

        FAR, FRR, fake, real = pt.Evaluate.ROC(fake, real, np.linspace(0, 1, 100, endpoint=True))

        percent = 0.00
        index = min([int(len(fake)*(1-percent)), len(fake)-1])
        thre = fake[min([index, len(fake) - 1])]
        # thre = fake[index]
        print('thre', thre, 'index', index, 'len', len(fake), len(real))
        acc = 0.001
        for i, frr in enumerate(real):
            if frr.item() >= thre.item():
                acc = 1 - float(i) / len(real)
                break
        # plt.plot(FAR, FRR)
        # plt.show()
        return acc

import random


def get_path_label(line):
    path, label = line.split()
    label = int(label)
    if label != 1:
        label = random.choice(np.arange(1, NLABEL))
    else:
        label = 0
    return path, int(label)

def get_path_label_Face(line):
    path, label = line.split()
    return path, 0

def get_path_label_dj502_train(line):
    path, label = line.split()
    if 'DJ_Backups' in path and '3D_FR_Data' not in path:
        return path, random.choice(np.arange(1, NLABEL))
    else:
        return path, 0

def get_path_label_Fake(line):
    path, label = line.split()
    return path, random.choice(np.arange(1, NLABEL))

def Aug_Function(img, label, **kwargs):
    # phase = kwargs['mode']
    img = img[0]/255.
    # img_np = img.numpy()
    # median = cv.medianBlur(img_np, 5)
    # flag = np.abs(median - img_np) > 0.1
    # img_np[flag] = 128/255.
    # img = P.from_numpy(img_np)
    # print(img.shape)

    # if label != 0:
    #     img = pt.GaussBlur(img, 3)

    # if np.random.uniform(0, 1) < 1:
    #     noise = np.random.randn(112, 96)/60.
    #     img += P.from_numpy(noise).float()
        # print(img)

    return img


if __name__ == '__main__':
    dataloader_test = pt.DataLoader.ImageLoader(get_path_label,
                                           # data_root='/media/dj/DJ_Backups/',
                                           # list_filename='3d_liveness_train_img_fake.txt',
                                           list_filename='/media/dj/dj_502/train_liveness.txt',
                                           # data_root='/media/dj/dj_502/zhilin/liveness-speckle-data/train',
                                           # list_filename='/media/dj/dj_502/zhilin/liveness-speckle-data/train/train.txt',
                                           image_size=(1, 112, 96), dtype=P.float32,
                                           Aug_Function=Aug_Function,
                                           shuffle=True, validation_ratio=0.05,
                                           # test_ratio=0.1)
                                           # test_list_filename='/media/dj/DJ_Backups/3D_FR_Data/Face123_Test_Dist/test.txt',
                                           # test_data_root='/media/dj/DJ_Backups/3D_FR_Data/Face123_Test_Dist/')
                                           # test_list_filename='3d_liveness_test.txt',
                                           # test_data_root='/home/dj/Downloads/zhilin/liveness-depth-image/deploy')
                                           # test_list_filename = 'face123_test.txt',
                                           # test_data_root='/home/dj/Downloads/zhilin/liveness-depth-image/deploy')
                                           # test_list_filename='toufa_test.txt',
                                           # test_data_root='/home/dj/Downloads/zhilin/liveness-depth-image/deploy')
                                           # test_list_filename='img_fake_test.txt',
                                           # test_data_root='/media/dj/DJ_Backups/')
                                           test_list_filename='test_file_v3.txt',
                                           test_data_root='/media/dj/DJ_Backups/')
                                           # test_list_filename='/media/dj/DJ_Backups/train.txt',
                                           # test_data_root='/media/dj/DJ_Backups/')
                                           # test_list_filename='/media/dj/dj_502/3D_FR_Data/FuShi1/test.txt',
                                           # test_data_root='/media/dj/dj_502/3D_FR_Data/FuShi1/')
    dl_face123 = pt.DataLoader.ImageLoader(get_path_label_Face, image_size=(1, 112, 96), dtype=P.float32, Aug_Function=Aug_Function,
                                           test_list_filename='/media/dj/DJ_Backups/3D_FR_Data/Face123_Test_Dist/test.txt',
                                           test_data_root='/media/dj/DJ_Backups/3D_FR_Data/Face123_Test_Dist/')
    dl_himax_indoor2 = pt.DataLoader.ImageLoader(get_path_label_Face, image_size=(1, 112, 96), dtype=P.float32,
                                           Aug_Function=Aug_Function,
                                           test_list_filename='/media/dj/dj_502/3D_FR_Data/TestData/himax_indoor2/test.txt',
                                           test_data_root='/media/dj/dj_502/3D_FR_Data/TestData/himax_indoor2')
    dl_pic_attack = pt.DataLoader.ImageLoader(get_path_label, image_size=(1, 112, 96), dtype=P.float32, Aug_Function=Aug_Function,
                                              test_list_filename='3d_liveness_test.txt',
                                              test_data_root='/home/dj/Downloads/zhilin/liveness-depth-image/deploy')

    dataloader_face = pt.DataLoader.ImageLoader(get_path_label_dj502_train, data_root='/media/dj/dj_502/3D_FR_Data', image_size=(1, 112, 96), dtype=P.float32,
                                                list_filename='/media/dj/dj_502/3D_FR_Data/train.txt',
                                                Aug_Function=Aug_Function, shuffle=True, validation_ratio=0.05,
                                                test_ratio=0.01)
    dataloader_fake = pt.DataLoader.ImageLoader(get_path_label_dj502_train, data_root='/media/dj/DJ_Backups/', image_size=(1, 112, 96), dtype=P.float32,
                                                list_filename='all_fake.txt',
                                                Aug_Function=Aug_Function, shuffle=True, validation_ratio=0.05,
                                                test_ratio=0.01)
    # dataloader = MultiDataLoader([dataloader_face, dataloader_fake])
    dataloader = pt.DataLoader.ImageLoader(get_path_label_dj502_train, data_root='', image_size=(1, 112, 96), dtype=P.float32,
                                                list_filename='/media/dj/DJ_Backups/3D_FR_Data/train_3DLN.txt',
                                                Aug_Function=Aug_Function, shuffle=True, validation_ratio=0.98,
                                                test_ratio=0.01)
    print(dataloader.summary())
    # model = Model()
    model = LivenessNet(NLABEL)
    model.cuda()
    # model.load_state_dict(P.load('3d_liveness_model_best.pkl'))
    trainer = ClassifyTrainer(nlabels=NLABEL, model=model, optimizer=op.Adam(model.parameters(), lr=0.001),
                              loss_function=nn.CrossEntropyLoss(), dataloader=dataloader)
    # trainer.resume('checkpoint.pkl', version_name='last_version')
    # model.load_state_dict(P.load('3d_liveness_model_img_fake_6.pkl'))
    # P.save(model.state_dict(), '3d_liveness_model_img_fake_7.pkl')
    # print(trainer.evaluate(256, 'cuda', dataloader=None))
    trainer.fit(epochs=3, batch_size=256, device='cuda', eval_per_step=30, save_path='dontaskme.pkl', save_per_step=30)

                # dataloader=dl_pic_attack)


