from pixtalks.Model.LivenessNet.LivenessNet import LivenessNet
from pixtalks import backend as P
import os
import torch.nn.functional as F
import pixtalks as pt

dirname = os.path.dirname(pt.__file__)

modelfilename = '3d_liveness_model_best.pkl'

livenessnet = LivenessNet(10)
checkpoint = P.load(os.path.join(dirname, 'models', modelfilename), map_location=pt.default_device)

livenessnet.load_state_dict(checkpoint)
livenessnet.eval()
# state = {
#             'epoch': 1,
#             'arch': 0,
#             'state_dict': livenessnet.state_dict(),
#             'best_prec1': 0,
#             'optimizer' : 0,
#         }
# P.save(state, 'models/3d_liveness_model_best.pth.tar')

def Liveness3D(depth_map, model=livenessnet):
    predict, features = model(depth_map.view((1, 1, 112, 96)))
    softmax = F.softmax(predict)
    return softmax[0][0].item()
