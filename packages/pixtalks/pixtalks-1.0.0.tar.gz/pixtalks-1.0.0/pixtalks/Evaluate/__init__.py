import torch as P
import numpy as np
import os
from matplotlib import pyplot as plt
import cv2 as cv
from tqdm import tqdm
from pixtalks.timer import Timer

class ROC_Helper():

    def __init__(self):
        self.far = []
        self.frr = []

        self.sort = False

    def __setitem__(self, key, value):
        assert key is True or key is False
        self.sort = False
        if key:
            self.frr.append(value)
        else:
            self.far.append(value)

    def Sort(self):
        self.temp_far, _ = P.sort(P.Tensor(self.far).float())
        self.temp_frr, _ = P.sort(P.Tensor(self.frr).float())
        self.sort = True

    def __getitem__(self, item):
        if self.sort is not True:
            self.Sort()

        index = min([int(len(self.temp_far) * (1 - item)), len(self.temp_far) - 1])

        thre = self.temp_far[index]
        for i, frr in enumerate(self.temp_frr):
            if frr > thre:
                return 1 - float(i) / len(self.temp_frr), thre, len(self.temp_frr) + len(self.temp_far)

        return 0, thre



class Batch_Calculator(object):

    def __init__(self, function, empty_datas, unfull_return=None):
        self.batch = empty_datas[0].size(0)
        self.current = 0
        self.function = function
        self.empty_datas = empty_datas
        self.unfull_return = unfull_return

    def ret(self):
        current = self.current
        self.current = 0
        return self.function([x[:current] for x in self.empty_datas])

    def __call__(self, *datas, **kwargs):
        if kwargs.get('force') is True:
            return self.ret()

        for emp_data, data in zip(self.empty_datas, datas):
            emp_data[self.current] = data
        self.current += 1

        if self.current == self.batch:
            current = self.current
            self.current = 0
            return self.function([x[:current] for x in self.empty_datas])
        else:
            return self.unfull_return

def cos_distance(a, b):
    len_a = P.sqrt(P.sum(P.pow(a, 2), dim=1))
    len_b = P.sqrt(P.sum(P.pow(b, 2), dim=1))
    dist = P.sum(a*b, dim=1) / (len_a * len_b)
    return dist

def ROC(far, frr, thres):
    sort_far = P.sort(far)[0]
    sort_frr = P.sort(frr)[0]
    far_times = len(sort_far)
    frr_times = len(sort_frr)
    FAR = []
    FRR = []

    for thre in thres:
        FAR.append(P.sum(sort_far > thre).float() / far_times)
        FRR.append(P.sum(sort_frr > thre).float() / frr_times)

    return FAR, FRR, sort_far, sort_frr

def GetPathFromN(n, l2):
    return n // l2, n % l2

def Cal_Feature_Distance(feature1, feature2):

    exp_feature1 = feature1.repeat(1, len(feature2)).view(-1, 128)
    exp_feature2 = feature2.repeat(len(feature1), 1)

    return cos_distance(exp_feature1.cuda(), exp_feature2.cuda())

def Cal_Image_Distance(images1, images2, model):

    # exp_feature1 = image1.repeat(1, len(image2)).view(-1, 128)
    # exp_feature2 = image2.repeat(len(image1), 1)
    score = []
    # print(images2.device)
    for img1 in images1:
        with Timer('repeat'):
            exp_img1 = P.cat([img1.view(1, 1, 112, 96)]*len(images2), dim=0)
        # print(exp_img1.shape, images2.shape)
        with Timer('cal'):
            try:
                pred = model(exp_img1, images2.view((-1, 1, 112, 96)))

                pred = pred.view(-1, 2)
                softmax = P.softmax(pred, dim=1)
                # print(softmax.shape)
                score.append(softmax[:, 0])
            except:
                print((pred.shape, softmax.shape, exp_img1.shape))

    return P.cat(score, dim=0)

def FR_ROC(feature_map):
    far = []
    frr = []
    far_times = 0
    frr_times = 0

    keys = list(feature_map.keys())
    count = 0
    for i in range(len(keys)):
        for j in range(i, len(keys)):
            key_i = keys[i]
            key_j = keys[j]
            features1 = feature_map[key_i]
            features2 = feature_map[key_j]
            if len(features1) * len(features2) == 0:
                continue

            dist = Cal_Feature_Distance(features1, features2)

            if i == j:
                frr.append(dist)
                frr_times += dist.size(0)
            else:
                far.append(dist)
                far_times += dist.size(0)

    frr = P.cat(frr, dim=0)
    far = P.cat(far, dim=0)
    return ROC(far, frr, np.linspace(-1, 1, 200))

def FR_ROC_img(image_map, model):
    far = []
    frr = []
    far_times = 0
    frr_times = 0

    keys = list(image_map.keys())

    with P.no_grad():

        for i in tqdm(list(range(len(keys)))):
            for j in range(i, len(keys)):
                key_i = keys[i]
                key_j = keys[j]
                images1 = image_map[key_i]
                images2 = image_map[key_j]
                if len(images1) * len(images2) == 0:
                    # print('continue', i, j)
                    continue
                dist = Cal_Image_Distance(images1, images2, model)
                # count += len(dist)
                if i == j:
                    frr.append(dist)
                    frr_times += dist.size(0)
                else:
                    far.append(dist)
                    far_times += dist.size(0)
        # print('count', count)
        frr = P.cat(frr, dim=0)
        far = P.cat(far, dim=0)
        return ROC(far, frr, np.linspace(0, 1, 200))

def PCA(data, n_dim):
    from sklearn.decomposition import PCA
    estimator = PCA(n_components=n_dim)
    pca_data = estimator.fit_transform(data)
    return pca_data


def Plot2DPoints(points):
    x = points[:, 0]
    y = points[:, 1]
    plt.scatter(x, y)

