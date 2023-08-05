from pixtalks.DataLoader import DataLoader
import torch as P
import os
import pixtalks as pt
import numpy as np
import random


def sum_list(lines):

    ret = []
    for line in lines:
        ret += line
    return ret


class MixtureList():

    def __init__(self, lines):
        # print(len(lines))
        self.index = np.concatenate([i * np.ones(len(lines[i]), dtype=int) for i in range(len(lines))], axis=0)
        self.lines = np.concatenate(lines)

    def shuffle(self, random_seed):
        cc = list(zip(self.index, self.lines))
        random.seed(random_seed)
        random.shuffle(cc)
        self.index[:], self.lines[:] = zip(*cc)

    def __getitem__(self, item):
        return (self.index[item], self.lines[item])

    def __len__(self):
        return len(self.lines)


class MixtureDataLoader(DataLoader):

    def __init__(self, dataloaders, **kwargs):

        self._shuffle = kwargs.get('shuffle')
        self._random_seed = kwargs.get('random_seed')

        if self._random_seed is None:
            self._random_seed = 0
        if self._shuffle is None:
            self._shuffle = False

        self.dataloaders = dataloaders
        self._inputs = dataloaders[0]._inputs

        self._data_roots = [dl._data_root for dl in dataloaders]
        self._Test_data_roots = [dl._Test_data_root for dl in dataloaders]
        self._validation_data_roots = [dl._validation_data_root for dl in dataloaders]

        self._Train = MixtureList([dl._Train for dl in dataloaders])
        self._Test = MixtureList([dl._Test for dl in dataloaders])
        self._Valid = MixtureList([dl._Valid for dl in dataloaders])

        if self._shuffle:
            self._Train.shuffle(self._random_seed)
            self._Test.shuffle(self._random_seed)
            self._Valid.shuffle(self._random_seed)

    def _mode_2_data_root(self, mode, id):
        if mode == 'train':
            return self._data_roots[id]
        elif mode == 'test':
            return self._Test_data_roots[id]
        elif mode == 'valid':
            return self._validation_data_roots[id]
        else:
            assert False

    def _get_batch(self, data_mode, batch, **kwargs):

        Data_Lines = self._mode_2_lines(data_mode)
        start_index = self._mode_2_index(data_mode)

        tensors = {}
        for name, dtype_shape in list(self._inputs.items()):
            dtype, data_shape = dtype_shape

            if data_shape is None:
                tensors[name] = P.empty(batch,).type(dtype)
            else:
                tensors[name] = P.empty(batch, *data_shape).type(dtype)

        n = 0
        temp_add_index = 0
        dl_indexs, lines = Data_Lines[start_index:]

        for dl_index, line in zip(dl_indexs, lines):
            data_root = self._mode_2_data_root(data_mode, dl_index)
            datas = self.dataloaders[dl_index]._get_data(data_root, line, **kwargs)

            temp_add_index += 1
            if datas is None:
                continue
            for name, data in list(datas.items()):
                if data is not None:
                    tensors[name][n] = data
                else:
                    n -= 1
                    break

            n += 1
            if n == batch:
                break

        self._index_add(data_mode, temp_add_index)

        if n == batch:
            return tensors
        else:
            return {name: tensor[:n] for name, tensor in list(tensors.items())}

    def summary(self):
        return '\n'.join([dl.summary() for dl in self.dataloaders])

if __name__ == '__main__':
    mul = MixtureList([[1, 1, 1, 1], [2, 2, 3, 4, 5, 6]])
    mul.shuffle(0)
    print(mul.lines)
    print(mul.index)