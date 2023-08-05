from pixtalks.DataLoader import DataLoader
import torch as P
import os
import pixtalks as pt
import numpy as np
import random


class MultiDataLoader(DataLoader):

    def __init__(self, dataloaders, weights, **kwargs):
        assert len(dataloaders) == len(weights)

        self.step = 0

        self.weight = np.array(weights, dtype=np.float32)
        self.weight /= np.sum(self.weight)

        self.dataloaders = dataloaders


    def __call__(self, batch, device, epochs=None, **kwargs):
        mode = kwargs.get('mode')

        if mode == 'train':
            data_name = 'train_data'
            data_mode = 'train'
        elif mode == 'test':
            self.index_test = 0
            data_name = 'test_data'
            data_mode = 'test'
        else:
            assert False, 'mode must be train or test'

        batches = (self.weight * batch).astype(np.int)
        run = np.ones(len(self.dataloaders))

        while True:

            if np.sum(run) == 0:
                break

            train_data = {i: {} for i in range(len(self.dataloaders)) if run[i]}
            progresses = []

            total_index = 0
            for i, dataloader in enumerate(self.dataloaders):

                if run[i]:
                    for key, value in dataloader._get_batch(data_mode, batches[i]).items():
                        train_data[i][key] = value.to(device)

                    dataloader_index = dataloader._mode_2_index(mode)

                    if mode is 'train':
                        if dataloader.epoch + 1 > epochs[i]:
                            run[i] = 0
                    else:
                        if dataloader_index == 0:
                            run[i] = 0

                    total_index += dataloader_index
                    progresses.append(float(dataloader_index + 1) / len(dataloader._mode_2_lines(mode))
                                      if dataloader_index != 0 else 1.0)
                else:
                    progresses.append(1.0)

            if mode == 'train':
                self.step += 1

                valid_data = {i: {} for i in range(len(self.dataloaders)) if run[i]}
                for i, dataloader in enumerate(self.dataloaders):
                    for key, value in dataloader._get_batch('valid', batches[i]).items():
                        valid_data[i][key] = value.to(device)
            else:
                valid_data = None

            package = dict()
            package[data_name] = train_data
            package['valid_data'] = valid_data

            if mode == 'train':
                print_infos = [f'[Epoch {self.dataloaders[i].epoch + 1}/{epochs[i]}][{pt.ProgressBar.SimpleBar(progress)}]'
                               for i, progress in enumerate(progresses)]

                package['print_info'] = '\r' + ''.join(print_infos)
            else:
                print_infos = [f'[{pt.ProgressBar.SimpleBar(progress)}]' for progress in progresses]
                package['print_info'] = '\r[Evaluating]' + ''.join(print_infos)

            yield package


    def state_dict(self):
        state_dict = {'step': self.step}
        for i, dataloader in enumerate(self.dataloaders):
            state_dict[i] = dataloader.state_dict()

        return state_dict

    def load_state_dict(self, state_dict):
        for i, dataloader in enumerate(self.dataloaders):
            dataloader.load_state_dict(state_dict[i])

        self.step = state_dict['step']

    def summary(self):
        return '\n'.join([dl.summary() for dl in self.dataloaders])

