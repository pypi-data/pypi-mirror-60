import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch import no_grad

if torch.cuda.is_available():
    default_device = torch.device('cuda')
else:
    default_device = torch.device('cpu')

backend = torch


from . import DataLoader
from . import ProgressBar
from . import Trainer
from . import Gradient
from . import Model
from . import utils
from . import Evaluate
from . import Metric
from . import Random
from . import transforms
from . import tools
from . import math
from . import Augmentation
from . import timer
# from . import visualise


from .FaceAlign3D import *
from .GetDepthMap import *
from .Liveness3D import *
from .FaceRecognition import *
from .usual_command import *
from .Fitting import *
from .ICP import *
from .blur import *

def Tensor(x):
    return torch.from_numpy(x)

def Array(x):
    return x.cpu().detach().numpy()

