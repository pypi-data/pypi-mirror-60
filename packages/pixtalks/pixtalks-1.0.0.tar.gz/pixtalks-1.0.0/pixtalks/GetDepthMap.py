from pixtalks.utils import GetDepthMap
from pixtalks.utils import GetDepthMap_Triangle
from pixtalks import backend as P
import pixtalks as pt

def DepthMap2PointCloud(depth_map, stride, x_min, x_max, y_min, y_max, z_min, z_max):
    if type(stride) is int:
        stride = (stride, stride)
    H, W = depth_map.shape
    u, v = P.meshgrid(P.arange(H), P.arange(W))
    u = u[::stride[0], ::stride[1]]
    v = v[::stride[0], ::stride[1]]
    scale = float(x_max - x_min) / W
    z = (depth_map[u, v] * (z_max - z_min)).view(-1)
    y = ((u - H//2) * scale).view(-1)
    x = (-(v - W//2) * scale).view(-1)
    area = z != 128.0/255

    return P.cat([x.float().view(-1, 1), y.float().view(-1, 1), z.float().view(-1, 1)], dim=1)[area]


def PC_KP_2_DP(pointcloud, keypoint):
    pointcloud = pt.Face_Align_to_StandardFace(pointcloud, keypoint)
    depth_map = GetDepthMap(pointcloud, 'direct')
    depth_map_align = pt.FaceClean(depth_map, 128/255., scale=255.)

    return depth_map_align


if __name__ == "__main__":
    depth = pt.imread('/home/dj/PycharmProjects/3DFaceRecognition/result/himax_indoor/depth_map/himax_indoor/gengshuai/depth_2019-11-2715-38-06_W1280_H800_FCnt32605.txt671.png')[0]/255.
    pt.imshow(depth)
    pc = DepthMap2PointCloud(depth, 1, -90, 90, -105, 105, -60, 60)
    pt.savetxt('test.txt', pc)
