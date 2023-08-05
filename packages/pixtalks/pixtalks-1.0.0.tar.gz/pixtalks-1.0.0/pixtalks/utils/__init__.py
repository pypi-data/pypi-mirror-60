import os
import shutil
import numpy as np
import pixtalks
import torch as P


def MergeListFile(output_filename, merge_function, data_roots, list_filenames, **kwargs):
    file = open(output_filename, 'w')
    for data_root, list_filename in zip(data_roots, list_filenames):
        for line in open(list_filename, 'r').readlines():
            new_line = merge_function(data_root, line, **kwargs)
            if new_line is not None:
                file.write(new_line.replace('\n', '') + '\n')
    file.close()


def GetDepthMap(pointcloud, insert_method='triangle', H=112, W=96, x_min=-90, x_max=90, y_min=-105, y_max=105, z_min=-60, z_max=60, dtype=P.float32, **kwargs):
    if insert_method == 'triangle':
        assert type(pointcloud) is str, 'you must put a filename to param pointcloud'
        if kwargs.get('triangle_file') is not None:
            return GetDepthMap_Triangle(pointcloud, kwargs.get('triangle_file'), H, W, x_min, x_max, y_min, y_max, z_min, z_max, dtype)
        else:
            return GetDepthMap_triangle(pointcloud, H, W, x_min, x_max, y_min, y_max, z_min, z_max, dtype)
    elif insert_method == 'direct':
        if type(pointcloud) is str:
            pointcloud = pixtalks.loadtxt(pointcloud)
        return GetDepthMap_Direct(pointcloud, H, W, x_min, x_max, y_min, y_max, z_min, z_max, dtype)
    else:
        assert False, 'insert_method must be one of trianle or direct'

def GetDepthMap_Direct(pointcloud, H=112, W=96, x_min=-90, x_max=90, y_min=-105, y_max=105, z_min=-60, z_max=60, dtype=P.float32):
    ret = P.zeros((H, W)).type(dtype) + float(z_min + z_max) / 2
    scale = float(W) / (x_max - x_min)

    x = pointcloud[:, 0]
    y = pointcloud[:, 1]
    z = pointcloud[:, 2]

    v = (-x * scale + W // 2).type(P.long)
    u = (-y * scale + H // 2).type(P.long)

    con = (u >= 0) * (u < H) * (v >= 0) * (v < W) * (z >= z_min) * (z <= z_max)
    u = u[con]
    v = v[con]
    z = z[con]

    ret[u, v] = z

    ret -= z_min
    ret /= z_max - z_min

    # ret = pixtalks.GaussBlur(ret, 3)

    return ret

def GetDepthMap_triangle(pointcloud_file, H=112, W=96, x_min=-90, x_max=90, y_min=-105, y_max=105, z_min=-60, z_max=60, dtype=P.float32):
    f = os.popen("/home/dj/anaconda3/envs/python2/lib/python2.7/site-packages/pixtalks/executable/DJ %s %s %s %s %s %s %s %s %s" % (pointcloud_file,
                                                                        H, W,
                                                                        x_min, x_max,
                                                                        y_min, y_max,
                                                                        z_min, z_max))
    data = f.readlines()
    data = np.array(data, dtype=np.float32)
    # print(data.shape)
    try:
        data = data.reshape(H, W)
    except:
        print(("Get Depth Map fail, Error filename :", pointcloud_file))
        return P.zeros((H, W)).type(dtype)

    return pixtalks.Tensor(data).type(dtype)



def GetDepthMap_Triangle(pointcloud_file, triangle_file, H=112, W=96, x_min=-90, x_max=90, y_min=-105, y_max=105, z_min=-60, z_max=60, dtype=P.float32):
    f = os.popen("/home/dj/anaconda3/envs/python2/lib/python2.7/site-packages/pixtalks/executable/DJ_triangle %s %s %s %s %s %s %s %s %s %s" % (pointcloud_file, triangle_file,
                                                                                    H, W,
                                                                                    x_min, x_max,
                                                                                    y_min, y_max,
                                                                                    z_min, z_max))
    data = f.readlines()
    data = np.array(data, dtype=np.float32)
    # print(data.shape)
    try:
        data = data.reshape(H, W)
    except:
        print(("Get Depth Map fail, Error filename :", pointcloud_file))
        return P.zeros((H, W)).type(dtype)
    # data = data[::-1]
    return pixtalks.Tensor(data).type(dtype)