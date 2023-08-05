import torch as P


def shuffle(tensor, dim, **kwargs):
    seed = kwargs.get('seed')
    if seed is not None:
        P.manual_seed(seed)
    permutation = P.randperm(tensor.size(dim))

    return P.index_select(tensor, dim, permutation)