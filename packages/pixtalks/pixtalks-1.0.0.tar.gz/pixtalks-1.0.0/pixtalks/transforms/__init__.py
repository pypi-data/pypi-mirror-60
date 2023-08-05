import torch
# import torchvision
# import torchvision.transforms.functional as tf
import pixtalks as pt
import PIL
from PIL import Image
import numpy as np
import cv2 as cv

def r2a(rad):
   return rad * np.pi / 180.

def mul_dot(*matrix):
    ret = np.eye(3)
    for m in matrix:
        ret = np.dot(m, ret)
    return ret

def transform_matrix(u, v):
    return np.array([[1, 0, v],
                     [0, 1, u],
                     [0, 0, 1]], dtype=np.float32)

def rotate_matrix(center_u, center_v, angle):
    angle = -r2a(angle)
    T1 = transform_matrix(-center_u, -center_v)
    R = np.array([[np.cos(angle), -np.sin(angle), 0],
                  [np.sin(angle), np.cos(angle), 0],
                  [0, 0, 1]], dtype=np.float32)
    T2 = transform_matrix(center_u, center_v)

    return mul_dot(T1, R, T2)

def affine(img, M, dsize, borderValue=0):
    size = dsize[::-1]
    return cv.warpAffine(img, M[:2], dsize=size, borderValue=borderValue)

if __name__ == '__main__':
    img = np.array(Image.open('/home/dj/depth.png'))
    M = rotate_matrix(50, 50, 30)
    af_img = affine(img, M, dsize=(112, 96), borderValue=128)

    pt.imshow(torch.Tensor(np.array(img)), torch.Tensor(np.array(af_img)))