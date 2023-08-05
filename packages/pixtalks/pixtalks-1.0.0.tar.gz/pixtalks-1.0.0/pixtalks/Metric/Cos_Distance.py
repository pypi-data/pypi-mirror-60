import torch

def cosine_distance(vector1, vector2):
    len1 = torch.norm(vector1, dim=1)
    len2 = torch.norm(vector2, dim=1)

    return torch.sum(vector1*vector2, dim=1) / (len1 * len2)