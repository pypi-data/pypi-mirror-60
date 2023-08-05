from pixtalks import backend as P
from pixtalks.Model.AlignNet import AlignNet
import numpy as np
import pixtalks as pt
import os

dirname = os.path.dirname(pt.__file__)
align_model = AlignNet(128, 1)
checkpoint = P.load(os.path.join(dirname, 'models/FaceAlignModel_best.pkl'), map_location=pt.default_device)
align_model.load_state_dict(checkpoint)
align_model.eval()

def FaceAlign3D(depthmap, model=align_model):
    R, T = model(depthmap.view(1, 1, 112, 96))
    return R[0], T[0]

# def FaceAlign3D_Times(pc, times, triangle_file=None):
#     for time in range(times):
#         # print(pc.shape)
#         pt.savetxt('temp1.txt', pc[0])
#         if triangle_file is None:
#             depth_map = pt.GetDepthMap('temp1.txt', 112, 96, -90, 90, -105, 105, -60, 60)
#         else:
#             depth_map = pt.GetDepthMap_Triangle('temp1.txt', triangle_file, 112, 96, -90, 90, -105, 105, -60, 60)
#         dm = depth_map.float()
#         R, T = FaceAlign3D(dm)
#
#         pc = pc.view(-1, 3)
#         pc = (P.matmul(pc, R) + T).view(1, -1, 3)
#
#     return pc[0]