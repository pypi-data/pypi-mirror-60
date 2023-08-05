import torch
import numpy as np

def PoissonDistribution(k, sample_num, pix_range=(0, 256)):
    return torch.from_numpy(np.concatenate([np.random.poisson(k*lam, size=(1, sample_num)) for lam in range(*pix_range)], axis=0))

def PoissonAugment(images, distrib):
    '''

    :param images: 0-255
    :param distrib: PoissonDistribution
    :return:
    '''
    sample_num = distrib.size(1)
    device = images.device
    img_size = images.shape

    images = images.view(-1).long()
    pix_num = images.size(0)

    dis_image = torch.index_select(distrib, 0, images).float()
    rand = (torch.rand(pix_num) * sample_num).long().to(device)
    id = torch.arange(pix_num).long().to(device)

    img_noise = dis_image[id, rand].view(img_size)

    sign = torch.rand(img_size).cuda()
    sign[sign < 0.5] = -1
    sign[sign > 0.5] = 1
    sign[sign == 0.5] = 0

    img_noise *= sign
    img_noise += images.view(img_size).float()

    return img_noise
