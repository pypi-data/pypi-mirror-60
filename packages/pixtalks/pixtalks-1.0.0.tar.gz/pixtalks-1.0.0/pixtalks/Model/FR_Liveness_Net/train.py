from pixtalks import backend as P
import pixtalks as pt
from pixtalks.Trainer import Trainer
from pixtalks.DataLoader import DataLoader
from pixtalks.DataLoader import MultiDataLoader
from pixtalks.Model.FR_Liveness_Net import FRNet_Relu
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as op
import os
import random
import cv2 as cv
import numpy as np
import pixtalks

NLABEL = 10

def get_path_label(line):
    path, label = line.split()
    label = int(label)
    if label != 1:
        label = random.choice(np.arange(1, NLABEL))
    else:
        label = 0
    return path, int(label)

def get_path_label_dj502_train(line):
    path, label = line.split()
    if 'DJ_Backups' in path and '3D_FR_Data' not in path:
        return path, random.choice(np.arange(1, NLABEL))
    else:
        return path, 0

def Aug_Function(img, label, **kwargs):
    img = img[0]/255.
    return img

class LivenessNet(nn.Module):

    def __init__(self, feature_dim, n_label):
        super(LivenessNet, self).__init__()

        self.classify = nn.Linear(feature_dim, n_label)

    def forward(self, input):
        return self.classify(input)


class FRLoader(DataLoader):

    def __init__(self, **kwargs):
        super(FRLoader, self).__init__(**kwargs)

        self._inputs = {'image': (P.float32, (1, 112, 96)),
                        'label': (P.long, None)}


    def _get_data(self, data_root, line, **kwargs):
        path, label = line.split()
        filename = os.path.join(data_root, path)
        try:
            img = pt.imread(filename)[0]/255.
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            # print(('read image fail: %s' % filename))
            return None

        label = int(label)

        return {'image': img,
                'label': label}

class LivenessLoader(DataLoader):

    def __init__(self, **kwargs):
        super(LivenessLoader, self).__init__(**kwargs)

        self._inputs = {'image': (P.float32, (1, 112, 96)),
                        'label': (P.long, None)}


    def _get_data(self, data_root, line, **kwargs):
        path, label = line.split()
        filename = os.path.join(data_root, path)
        try:
            img = pt.imread(filename)[0]/255.
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            # print(('read image fail: %s' % filename))
            return None

        label = int(label)

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

        if 0 in data.keys():
            image = data[0]['image']
            label = data[0]['label']
            feature = self.model(image)
            predict = self.model.arc_face(feature, label)
            loss_cla = self.loss_function(predict, label)
            acc_cla = P.mean((P.argmax(predict, dim=1) == label).float())
            fr_dict = {'feature': feature, 'label': label}
        else:
            loss_cla = P.zeros(1, device='cuda')
            acc_cla = P.zeros(1, device='cuda')
            fr_dict = dict()

        if 1 in data.keys():
            image_liveness = data[1]['x']
            label_liveness = data[1]['y']
            feature_liveness = self.model(image_liveness)
            predict_liveness = self.model.liveness(feature_liveness)
            loss_liveness = self.loss_function(predict_liveness, label_liveness)
            acc_liv = P.mean((P.argmax(predict_liveness, dim=1) == label_liveness).float())
            lv_dict = {'pred_live': predict_liveness, 'label_liveness': label_liveness}
        else:
            loss_liveness = P.zeros(1, device='cuda')
            acc_liv = P.zeros(1, device='cuda')
            lv_dict = dict()

        loss = loss_cla + loss_liveness

        self.update(self.optimizer, loss)

        ret = dict()
        if forward_mode == 'train':
            ret.update({'loss': loss.item(), 'acc_cla': acc_cla.item(), 'acc_liv': acc_liv.item()})
            return ret
        else:
            ret.update(fr_dict)
            ret.update(lv_dict)
            return ret

    def evaluate(self, batch_size, device, **kwargs):
        count = 0
        total = 0
        roc = pixtalks.Evaluate.ROC_Helper()
        feature_map = {label: [] for label in range(kwargs.get('n_labels'))}
        for forward_test in self._evaluate(batch_size, device, **kwargs):
            if 'label' in forward_test.keys():
                labels = forward_test['label']
                features = forward_test['feature']

                for label, feature in zip(labels, features):
                    feature_map[label.item()].append(feature.unsqueeze(0))

            if 'pred_live' in forward_test.keys():
                pred_liveness = P.softmax(forward_test['pred_live'], dim=1)
                argmax_liveness = P.argmax(pred_liveness, dim=1)
                label_liveness = forward_test['label_liveness']

                for p, l, a in zip(pred_liveness, label_liveness, argmax_liveness):
                    # print(p[0].item(), l.item(), a.item())
                    if p[0].item() > 0.99:
                        count += 1
                    roc[l.item() == a.item()] = p[0].item()
                    total += 1

        for key, value in list(feature_map.items()):
            feature_map[key] = P.cat(value, dim=0) if len(value) is not 0 else []

        # print(('Key:', len(list(feature_map.keys()))))
        if len(feature_map) > 0:
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

        try:
            R = roc[0.001]
        except:
            R = -1
        print('liveness', R)
        print('liveness_count>0.98', count, total, count/total)

        return acc

dl_himax_indoor2 = pt.DataLoader.ImageLoader(lambda x: (x.split()[0], 0), image_size=(1, 112, 96), dtype=P.float32,
                                       Aug_Function=Aug_Function,
                                       test_list_filename='/media/dj/dj_502/3D_FR_Data/TestData/himax_indoor2/test.txt',
                                       test_data_root='/media/dj/dj_502/3D_FR_Data/TestData/himax_indoor2')
dl_pic_attack = pt.DataLoader.ImageLoader(get_path_label, image_size=(1, 112, 96), dtype=P.float32,
                                          Aug_Function=Aug_Function,
                                          test_list_filename='3d_liveness_test.txt',
                                          test_data_root='/home/dj/Downloads/zhilin/liveness-depth-image/deploy')
dataloader_test = pt.DataLoader.ImageLoader(get_path_label,
                                           list_filename='/media/dj/dj_502/train_liveness.txt',
                                           image_size=(1, 112, 96), dtype=P.float32,
                                           Aug_Function=Aug_Function,
                                           shuffle=True, validation_ratio=0.05,
                                           test_list_filename='/home/dj/anaconda3/lib/python3.6/site-packages/pixtalks/Model/LivenessNet/test_file_v3.txt',
                                           test_data_root='/media/dj/DJ_Backups/')

if __name__ == '__main__':
    n_labels = 2742
    # n_labels = 1700
    model = FRNet_Relu(feature_dim=128, n_labels=n_labels, width_mult=0.75, liveness_dim=NLABEL)
    model.cuda()

    dataloader_fr = FRLoader(
                          # data_root='/media/dj/dj_502/3D_FR_Data',
                          # list_filename='/media/dj/dj_502/3D_FR_Data/train.txt',
                          data_root='/media/dj/DJ_Backups/3D_FR_Data/',
                          list_filename='/media/dj/DJ_Backups/3D_FR_Data/train.txt',
                          # data_root='/media/dj/dj_502/3D_FR_Data/',
                          # list_filename='/media/dj/dj_502/3D_FR_Data/train.txt',
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
    # dataloader_lv = LivenessLoader(list_filename='/media/dj/dj_502/train_liveness.txt', shuffle=True, validation_ratio=0.05,
    #                                test_)

    dataloader_lv = pt.DataLoader.ImageLoader(get_path_label_dj502_train, data_root='', image_size=(1, 112, 96),
                                           dtype=P.float32,
                                           list_filename='/media/dj/DJ_Backups/3D_FR_Data/train_3DLN.txt',
                                           Aug_Function=Aug_Function, shuffle=True, validation_ratio=0.05,
                                           test_ratio=0.01)
                                           # test_data_root='',
                                           # test_list_filename='')

    dataloader = MultiDataLoader([dataloader_fr, dataloader_lv], [1, 1])
    # dl_himax_indoor2 = FRLoader(test_data_root='/media/dj/dj_502/3D_FR_Data/TestData/',
    #                             test_list_filename='/media/dj/dj_502/3D_FR_Data/TestData/himax_indoor2_clean/test.txt')
    # dl_himax_indoor3 = FRLoader(test_data_root='/home/dj/PycharmProjects/3DFaceRecognition/depth_map/himax_indoor2/',
    #                             test_list_filename='/home/dj/PycharmProjects/3DFaceRecognition/depth_map/himax_indoor2/test.txt')

    trainer = FRTrainer(lr=0.1, n_labels=n_labels, dataloader=dataloader, model=model)
    trainer.resume('model.pkl', version_name='model_best', ignore=[trainer.optimizer])
    # trainer.checkpoint['best_eval_score'] = 0
    # print(trainer.__dict__)
    # print((dataloader._summary()))
    # print(trainer.evaluate(128, 'cuda', n_labels=1200, dataloader=dl_himax_indoor2))
    # P.save(model.state_dict(), 'fr_model_new_insert_method_0.45.pkl')
    trainer.fit(epochs=(10, 10), batch_size=128, save_path='model.pkl', device='cuda', eval_per_step=50,
                n_labels=1200)
    # print(trainer.evaluate(128, 'cuda', n_labels=1200, dataloader=None))
