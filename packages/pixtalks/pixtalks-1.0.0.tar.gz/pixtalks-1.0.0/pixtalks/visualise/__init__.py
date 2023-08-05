from mayavi import mlab
import torch
import pixtalks as pt


def Plot3D(pc, color, size):
    '''

    :param pc: N * 3
    :param color: (B, G, R)
    :param size: real number
    :return:
    '''
    x, y, z = torch.split(pc, 1, 1)

    x = pt.Array(x)
    y = pt.Array(y)
    z = pt.Array(z)

    mlab.points3d(x, y, z, color=color, scale_factor=size)

def show():
    mlab.show()