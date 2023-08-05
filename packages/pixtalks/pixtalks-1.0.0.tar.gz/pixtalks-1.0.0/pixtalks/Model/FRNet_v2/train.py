from pixtalks import backend as P
import pixtalks as pt
from pixtalks.Trainer import Trainer
from pixtalks.DataLoader import DataLoader
from pixtalks.Model.FRNet_v2 import FRNet, FRNet_STN
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as op
import os
import cv2 as cv
import numpy as np
import pixtalks

class BlankDetetor(nn.Module):

    def __init__(self, ksize=1, value=128./255):
        super(BlankDetetor, self).__init__()

        self.kernel = P.ones((1, 1, ksize, ksize))
        self.padding = ksize//2
        self.value = value

    def forward(self, input):
        net = P.abs(input - self.value)
        net = F.conv2d(net, self.kernel, padding=self.padding)
        return P.where(net != 0, P.ones_like(net), P.zeros_like(net))


class FRLoader(DataLoader):

    def __init__(self, **kwargs):
        super(FRLoader, self).__init__(**kwargs)

        self._inputs = {'image': (P.float32, (1, 112, 96)),
                        'label': (P.long, None)}
        self.detetor = BlankDetetor()

    def _get_data(self, data_root, line, **kwargs):
        path, label = line.split()
        filename = os.path.join(data_root, path)
        try:
            img = pt.imread(filename)[0]/255.
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            print(('read image fail: %s' % filename))
            return None

        # crop_img = img[40:70, 30:65].clone().view(-1)
        # # print(crop_img.shape)
        # max_value, max_index = P.max(crop_img, dim=0)
        # max_u = max_index // 35
        # max_v = max_index - 35 * max_u
        # max_u += 40
        # max_v += 30
        # U = 56 - max_u
        # V = 48 - max_v
        # # print(max_value, max_u, max_v, U, V)
        # if np.abs(U) > 15 or np.abs(V) > 15:
        #     U, V = 0, 0
        # img_numpy = pt.Array(img)
        # M = pt.transforms.transform_matrix(U, V)
        # img_trans = pt.transforms.affine(img_numpy, M, (112, 96), borderValue=128./255)
        #
        # nimg = pt.Tensor(img_trans)
        # mask = self.detetor(nimg.view((1, 1, 112, 96))).view(112, 96) * (0.667 - max_value)
        # nimg += mask
        # nimg = P.clamp(nimg, 0, 1)
        # pt.imshow(img, nimg, mask, mode='plt')
        # img = nimg

        # img = pt.Array(img)
        # u = np.random.uniform(-10, 10)
        # v = np.random.uniform(-10, 10)
        # M = pt.transforms.transform_matrix(u, v)
        # img = pt.transforms.affine(img, M, (112, 96), 128./255)
        # img = pt.Tensor(img)

        # mask = P.where(img != 128./255, P.Tensor([np.random.uniform(-0.15, 0.15)]), P.Tensor([0.]))
        # img += mask

        # pt.imshow(img)
        label = int(label)

        # if kwargs.get('mode') is 'test':
        # pt.imshow(img, pixtalks.FaceClean(img, 128/255., scale=255.))
        # img = pixtalks.FaceClean(img, 128/255., scale=255.)

        return {'image': img,
                'label': label}

class FRTrainer(Trainer):

    def __init__(self, model, lr, n_labels, **kwargs):
        super(FRTrainer, self).__init__(**kwargs)

        self.model = model
        self.n_labels = n_labels
        self.loss_function = nn.CrossEntropyLoss()
        # self.center_loss = pt.Metric.CenterLoss(n_labels, 128, 2)
        self.optimizer = op.SGD(self.model.parameters(), lr=lr)


    def forward(self, data, forward_mode, **kwargs):
        image = data['image']
        label = data['label']

        feature, predict = self.model.train_forward(image, label)
        loss_cla = self.loss_function(predict, label)
        loss = loss_cla

        self.update(self.optimizer, loss)

        if forward_mode == 'train':
            acc = P.mean((P.argmax(predict, dim=1) == label).float())
            return {'loss': loss.item(), 'acc': acc.item()}
        else:
            return {'feature': feature, 'label': label}

    def evaluate(self, batch_size, device, **kwargs):

        feature_map = {label: [] for label in range(kwargs.get('n_labels'))}
        for forward_test in self._evaluate(batch_size, device, **kwargs):
            labels = forward_test['label']
            features = forward_test['feature']

            for label, feature in zip(labels, features):
                feature_map[label.item()].append(feature.unsqueeze(0))

        for key, value in list(feature_map.items()):
            feature_map[key] = P.cat(value, dim=0) if len(value) is not 0 else []

        # print(('Key:', len(list(feature_map.keys()))))
        FAR, FRR, sort_far, sort_frr = pt.Evaluate.FR_ROC(feature_map)

        percent = 0.001
        index = min([int(len(sort_far) * (1 - percent)), len(sort_far) - 1])
        thre = sort_far[min([index, len(sort_far) - 1])]
        # thre = fake[index]
        print(('thre', thre, 'index', index, 'len', len(sort_far), len(sort_frr)))
        acc = 0.001
        for i, frr in enumerate(sort_frr):
            if frr.item() >= thre.item():
                acc = 1 - float(i) / len(sort_frr)
                break
        # plt.plot(FAR, FRR)
        # plt.show()
        return acc

if __name__ == '__main__':
    # n_labels = 2742
    n_labels = 1700
    model = FRNet(feature_dim=128, n_labels=n_labels)
    model.cuda()

    dataloader = FRLoader(
                          # data_root='/media/dj/dj_502/3D_FR_Data',
                          # list_filename='/media/dj/dj_502/3D_FR_Data/train.txt',
                          # data_root='/media/dj/DJ_Backups/3D_FR_Data/',
                          # list_filename='/media/dj/DJ_Backups/3D_FR_Data/train.txt',
                          data_root='/media/dj/dj_502/3D_FR_Data/',
                          list_filename='/media/dj/dj_502/3D_FR_Data/train.txt',
                          shuffle=True, validation_ratio=0.05,
                          # test_ratio=0.1)
                          test_data_root='/media/dj/DJ_Backups/3D_FR_Data/',
                          test_list_filename='/media/dj/DJ_Backups/3D_FR_Data/test.txt')
                          # test_data_root='/media/dj/dj_502/3D_FR_Data/Face123_ver3/',
                          # test_list_filename='/media/dj/dj_502/3D_FR_Data/Face123_ver3/test.txt')
                          # test_data_root='/media/dj/dj_502/3D_FR_Data/',
                          # test_list_filename='/media/dj/dj_502/3D_FR_Data/test.txt')
                          # test_data_root='/media/dj/dj_502/3D_FR_Data/TestData/',
                          # test_list_filename='/media/dj/dj_502/3D_FR_Data/TestData/himax_indoor2_clean/test.txt')
    dl_himax_indoor2 = FRLoader(test_data_root='/media/dj/dj_502/3D_FR_Data/TestData/',
                                test_list_filename='/media/dj/dj_502/3D_FR_Data/TestData/himax_indoor2_clean/test.txt')
    dl_himax_indoor3 = FRLoader(test_data_root='/home/dj/PycharmProjects/3DFaceRecognition/depth_map/himax_indoor2/',
                                test_list_filename='/home/dj/PycharmProjects/3DFaceRecognition/depth_map/himax_indoor2/test.txt')

    trainer = FRTrainer(lr=0.01, n_labels=n_labels, dataloader=dataloader, model=model)
    # trainer.resume('model_new2.pkl', version_name='model_best', ignore=[trainer.optimizer])

    # print(trainer.__dict__)
    # print((dataloader._summary()))
    # print(trainer.evaluate(128, 'cuda', n_labels=1200, dataloader=dl_himax_indoor2))
    # P.save(model.state_dict(), 'fr_model_new_insert_method_0.45.pkl')
    # trainer.fit(epochs=10, batch_size=128, save_path='model_new4.pkl', device='cuda', eval_per_step=50,
    #             save_per_step=50, n_labels=1200)
    # print(trainer.evaluate(128, 'cuda', n_labels=1200, dataloader=None))
