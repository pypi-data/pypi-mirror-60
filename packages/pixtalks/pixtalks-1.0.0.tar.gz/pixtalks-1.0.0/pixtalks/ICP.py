import torch as P
import pixtalks as pt
from pixtalks import ICP_Transorm_Matrix

def GetPathFromN(n, l2):
    return n // l2, n % l2

def Cal_Distance(pc1, pc2):

    exp_pc1 = pc1.repeat(1, len(pc2)).view(-1, 3)
    exp_pc2 = pc2.repeat(len(pc1), 1)

    return P.sum(P.pow(exp_pc1 - exp_pc2, 2), dim=1)

def GetNearestPointCloud(origin_pc, target_pc):
    l1 = origin_pc.size(0)
    l2 = target_pc.size(0)
    dist = Cal_Distance(origin_pc, target_pc)
    ret_index = P.empty(l1).to(target_pc.device)
    count = 0
    for point in range(0, l1*l2, l2):
        ds = dist[point: point + l2]
        index = P.argmin(ds, dim=0)
        # index = index[0]
        ret_index[count] = index
        count += 1
    ret_index = ret_index.long()
    return P.index_select(target_pc, 0, ret_index[:count])

def ICP(origin_pc, target_pc, max_iter, iter_loss, **kwargs):
    o_pc = origin_pc.clone()
    loss = iter_loss + 1
    iter_time = 0
    with P.no_grad():
        while loss >= iter_loss and iter_time < max_iter:
            nearest = GetNearestPointCloud(o_pc, target_pc)
            R, T = ICP_Transorm_Matrix(o_pc, nearest)
            # print(R.device, T.device)
            o_pc = P.matmul(o_pc, R) + T
            loss = P.mean(P.sqrt(P.sum(P.pow(o_pc - nearest, 2), dim=1)))
            print((loss.item()))
            iter_time += 1

    if kwargs.get('return_index') is True:
        return o_pc, loss, iter_time

    return o_pc
