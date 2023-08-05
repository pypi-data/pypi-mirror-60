import cv2 as cv
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def gaussian_2d_kernel(kernel_size=3, sigma=0):
    kernel = np.zeros([kernel_size, kernel_size])
    center = kernel_size // 2

    if sigma == 0:
        sigma = ((kernel_size - 1) * 0.5 - 1) * 0.3 + 0.8

    s = 2 * (sigma ** 2)
    sum_val = 0
    for i in range(0, kernel_size):
        for j in range(0, kernel_size):
            x = i - center
            y = j - center
            kernel[i, j] = np.exp(-(x ** 2 + y ** 2) / s)
            sum_val += kernel[i, j]
            # /(np.pi * s)
    sum_val = 1 / sum_val
    return kernel * sum_val

class GaussianBlur(nn.Module):
    def __init__(self, kernel_size, padding=0, channel=1, channel_first=True):
        super(GaussianBlur, self).__init__()
        kernel = gaussian_2d_kernel(kernel_size)
        kernel = torch.FloatTensor(kernel).unsqueeze(0).unsqueeze(0)
        # print(kernel.shape)
        self.weight = nn.Parameter(data=kernel, requires_grad=False)
        self.padding = padding
        self.channel = channel
        self.channel_first = channel_first

    def forward(self, x):
        if self.channel_first:
            return torch.cat([F.conv2d(x[:, i].unsqueeze(1), self.weight, padding=self.padding) for i in range(self.channel)], dim=1)
        else:
            return torch.cat([F.conv2d(x[..., i].unsqueeze(-1), self.weight, padding=self.padding) for i in range(self.channel)], dim=-1)

def GaussBlur(img, kernel_size, channel=1):
    shape = img.shape
    size = img.shape[-2:]
    ga = GaussianBlur(kernel_size, kernel_size//2, channel, channel_first=True)(img.view(-1, channel, *size))
    return ga.view(shape)

