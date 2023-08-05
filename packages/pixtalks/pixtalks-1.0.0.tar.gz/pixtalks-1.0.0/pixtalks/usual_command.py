import cv2 as cv
from pixtalks import backend as P
from matplotlib import pyplot as plt
import numpy as np
import pixtalks
import os


def imread(filename, dtype=np.float32, flag='channel_first', channels=1, type='tensor'):
    img = cv.imread(filename).astype(dtype)
    if flag is 'channel_first':
        img = img.transpose(2, 0, 1)
        img = img[:channels]
    else:
        img = img[..., :channels]

    if type is 'tensor':
        ret = P.from_numpy(img)
    elif type is 'array' or 'numpy':
        ret = img

    return ret


def imshow(*images, **kwargs):

    show_image = P.cat([img.cpu() for img in images], dim=-1).detach().numpy()

    mode = kwargs.get('mode')
    if mode is None:
        mode = 'plt'
    if mode is 'plt':
        plt.imshow(show_image)
        plt.show()
    elif mode is 'cv':
        cv.imshow('pixtalks', show_image)
        cv.waitKey()

    return show_image


def imsave(filename, obj):
    img = pixtalks.Array(obj)
    cv.imwrite(filename, img)

def savetensor(filename, obj):
    array = pixtalks.Array(obj)
    np.save(filename, array)

def loadtensor(filename):
    array = np.load(filename)
    return pixtalks.Tensor(array)

def checkdir(path):
    if os.path.exists(path) == False:
        os.mkdir(path)


def loadtxt(filename, dtype=P.float32, length=None):
    if length is None:
        txt = np.loadtxt(filename)
        return P.from_numpy(txt).type(dtype)
    else:
        lines = open(filename, 'r').readlines()
        output = np.empty((len(lines), length))
        for n, line in enumerate(lines):
            output[n] = np.array(line.split())
        return P.from_numpy(output).type(dtype)


def savetxt(filename, obj):
    array = obj.cpu().detach().numpy()
    np.savetxt(filename, array)


def __GetAllFile(root, postfix='.txt', result=[]):
    if os.path.isdir(root):
        for line in os.listdir(root):
            __GetAllFile(os.path.join(root, line), postfix, result)
    else:
        if root[-len(postfix):] == postfix:
            result.append(root)

def GetAllFiles(root, postfix='.txt'):
    ret = []
    __GetAllFile(root, postfix, ret)
    return ret


def ListWrite(filename, lines):
    with open(filename, 'w') as file:
        for line in lines:
            file.write(line.replace('\n', '') + '\n')


def ICP_Transorm_Matrix(origin_points, target_points):
    assert len(origin_points) == len(target_points), ''
    device = origin_points.device
    origin_center = P.sum(origin_points, dim=0) / origin_points.size(0)
    target_center = P.sum(target_points, dim=0) / target_points.size(0)

    origin_c_points = origin_points - origin_center
    target_c_points = target_points - target_center

    W = P.matmul(origin_c_points.t(), target_c_points)

    # U, _, V = np.linalg.svd(W.cpu().numpy())
    U, _, V = P.svd(W)
    V = V.t()
    # U = P.from_numpy(U)
    # V = P.from_numpy(V)

    if P.det(U) < 0:
        U[:, 2] *= -1
    if P.det(V) < 0:
        V[:, 2] *= -1

    # R = P.Tensor(np.linalg.inv(np.dot(U, V))).to(device)
    R = P.matmul(U, V).to(device)

    RO_points = P.matmul(origin_points, R)

    T = target_points - RO_points

    return R.to(device), (P.sum(T, dim=0) / len(T)).to(device)


def Face_Align_to_StandardFace(pointcloud, keypoints):
    '''

    :param pointcloud: N * 3
    :param keypoints: 5 * 3
    :return: aligned pointcloud
    '''
    dirname = os.path.dirname(pixtalks.__file__)
    standardface = loadtxt(os.path.join(dirname, 'standard_keypoint.txt'))
    R, T = ICP_Transorm_Matrix(keypoints, standardface)
    return P.matmul(pointcloud, R) + T


def Crop_PointCloud(pointcloud, range):
    area = (pointcloud[:, 0] > range[0]) * (pointcloud[:, 0] < range[1]) * \
           (pointcloud[:, 1] > range[2]) * (pointcloud[:, 1] < range[3]) * \
           (pointcloud[:, 2] > range[4]) * (pointcloud[:, 2] < range[5])
    return pointcloud[area]



