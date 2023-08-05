from pixtalks.Model.FRNet_v2 import FRNet, FRNet_Relu
from pixtalks.Model.ConditionalAutoEncoder import ConditionalAutoEncoder
from pixtalks.Model.AutoEndoder import AutoEncoder
from pixtalks import backend as P
import os
import pixtalks as pt
from pixtalks.Model.FRNet_v1 import Net

dirname = os.path.dirname(pt.__file__)

def cos_dist(f1, f2):
    f1 = f1/P.norm(f1)
    f2 = f2/P.norm(f2)

    return P.dot(f1, f2)

standard_size = (1, 1, 112, 96)

model_v3 = AutoEncoder()
# model_v3.load_state_dict(P.load('/home/dj/anaconda3/envs/python2/lib/python2.7/site-packages/pixtalks/Model/AutoEndoder/face_reconstruct_model_best.pkl'))
# model_v3.load_state_dict(P.load(os.path.join(dirname, 'models/CAE_FR_model_best.pkl')))
model_v3.eval()

model_v2 = FRNet(128, 1700)
# model_v2.load_state_dict(P.load(os.path.join(dirname, 'Model/FRNet_v2/fr_model_clean_0.4878_953.pkl')))
model_v2.load_state_dict(P.load(os.path.join(dirname, 'models/fr_model_new_insert_method_0.45.pkl'), map_location=pt.default_device))
model_v2.eval()

FaceRecognition3D_Threshold = 0.4944

# model_v1 = Net(128, 2666, 85164, '', pretrained=False, width_mult=1.5, channel=1)
# checkpoint = P.load(os.path.join(dirname, 'models/facerecoginition_model_v1.pth.tar'))
model_v1 = Net(128, 2666, 85164, '', pretrained=False, width_mult=1.5, channel=1)
# checkpoint = P.load(os.path.join(dirname, 'models/facerecoginition_model_v1.pth.tar'), map_location=pt.default_device)
# model_v1.load_state_dict(checkpoint['state_dict'])
model_v1.eval()

def FaceRecognition3D(img1, img2, version='v2', **kwargs):
    if kwargs.get('faceclean') is True:
        img1 = pt.FaceClean(img1.view(112, 96), 128 / 255., 255.).view(img1.shape)
        img2 = pt.FaceClean(img2.view(112, 96), 128 / 255., 255.).view(img2.shape)

    if version == 'v1':
        imgs = P.cat([img1.view(standard_size), img2.view(standard_size)], dim=0)
        feature1, feature2 = model_v1.get_feature(imgs)
    elif version == 'v2':
        imgs = P.cat([img1.view(standard_size), img2.view(standard_size)], dim=0)
        feature1, feature2 = model_v2(imgs)
    elif version == 'v3':
        assert False
        (feature1, feature2), (de1, de2) = model_v3.feature_decode(imgs)
    return cos_dist(feature1.view(-1), feature2.view(-1)).item()

def FaceReconstruct(img):
    return model_v3(img.view(-1, 1, 112, 96)).view(*img.shape)

def FaceRecognition3D_FeatureMap(img, model=model_v2):

    imgs = img.view(standard_size)
    featuremap = model.forward_feature_map(imgs).view((512, 7, 6))
    return featuremap

def FaceClean(image, insert_value, scale=256.):
    standard_face = pt.imread(os.path.join(dirname, 'mean_blur_face.png')).view(image.size())/scale
    std_face = pt.loadtensor(os.path.join(dirname, 'std_face.npy')).view(image.size())

    face = image.clone()
    area = face[30:90, 20:80]
    stand_area = standard_face[30:90, 20:80]
    max_value = P.sum(P.where(area != 128/scale, area, P.zeros(1))) / P.sum(P.where(area != 128/scale, P.ones(1), P.zeros(1)))
    stand_value = P.sum(P.where(stand_area != 128 / scale, stand_area, P.zeros(1))) / P.sum(P.where(stand_area != 128/scale, P.ones(1), P.zeros(1)))
    move = P.where(face != 128/scale, P.Tensor([stand_value - max_value]), P.zeros(1))
    face += move

    area = (P.abs(face - standard_face) < std_face).type(P.int8) * (face != 128/scale).type(P.int8)

    face = P.where(area == 1, face, P.Tensor([insert_value]))

    return face

