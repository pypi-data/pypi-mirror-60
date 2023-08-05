import pixtalks as pt
import torch as P
import numpy as np


def GetRandomSphereVector(batch=1):
    u = np.random.uniform(0, 1, size=(batch,))
    v = np.random.uniform(0, 1, size=(batch,))
    theta = 2 * np.pi * u
    phi = np.arccos(2 * v - 1)
    x = np.sin(theta) * np.sin(phi)
    y = np.cos(theta) * np.sin(phi)
    z = np.cos(phi)

    return pt.Tensor(np.concatenate([x.reshape(batch, 1), y.reshape(batch, 1), z.reshape(batch, 1)], axis=1)).float()


def GetRotateMatrix(nx, ny, nz, angle):
    rad = angle * np.pi / 180.
    q0 = np.cos(rad/2)
    q1 = nx * np.sin(rad / 2)
    q2 = ny * np.sin(rad / 2)
    q3 = nz * np.sin(rad / 2)

    R = P.FloatTensor([[1 - 2*q2**2 - 2*q3**2, 2*q1*q2 - 2*q0*q3, 2*q1*q3 + 2*q0*q2],
                  [2*q1*q2 + 2*q0*q3, 1 - 2*q1**2 - 2*q3**2, 2*q2*q3 - 2*q0*q1],
                  [2*q1*q3 - 2*q0*q2, 2*q2*q3 + 2*q0*q1, 1 - 2*q1**2 - 2*q2**2]])

    return R