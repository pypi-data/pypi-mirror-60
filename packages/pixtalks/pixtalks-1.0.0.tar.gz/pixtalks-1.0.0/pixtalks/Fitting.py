from pixtalks import backend as P

def PlaneFitting(data):
    '''
    plane fitting
    :param data: data[batch, 3]->x, y, z
    :return: z = a0 * x + a1 * y + a2, and rmse is the fitting error
    '''
    x = data[:, 0]
    y = data[:, 1]
    z = data[:, 2]

    sum_x_2 = P.sum(P.pow(x, 2))
    sum_y_2 = P.sum(P.pow(y, 2))
    sum_x_y = P.sum(x * y)
    sum_x_z = P.sum(x * z)
    sum_y_z = P.sum(y * z)
    sum_x = P.sum(x)
    sum_y = P.sum(y)
    sum_z = P.sum(z)
    n = data.size(0)

    A = P.Tensor([sum_x_2, sum_x_y, sum_x, sum_x_y, sum_y_2, sum_y, sum_x, sum_y, n]).view((3, 3))
    b = P.Tensor([sum_x_z, sum_y_z, sum_z])

    A_1 = P.inverse(A)
    a0, a1, a2 = P.matmul(A_1, b)
    RMSE = P.sqrt((P.sum(P.pow(a0 * x + a1 * y + a2 - z, 2))) / n)
    return a0, a1, a2, RMSE
