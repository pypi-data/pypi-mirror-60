import torch
from pixtalks.DataLoader import DataLoader
import pixtalks.ProgressBar
import os
import numpy as np
import torch.nn as nn
import torch.optim as op
from matplotlib import pyplot as plt



class Trainer(object):
    '''
    these methods must be defined:
     - __init__
     - forward
     - evaluate

     - save(choice)
     - load(choice)
     - callback(choice)

    '''
    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.dataloader = kwargs.get('dataloader')

        self.checkpoint = {'step': 0, 'best_eval_score': -np.inf, 'version_names': set()}
        self._basic_names = list(self.checkpoint.keys())

        self._training = True
        self._validing = False
        self._testing = False

    def resume(self, model_filename, version_name=None, ignore=None):
        self.checkpoint = torch.load(model_filename)
        # print(self.checkpoint.keys())
        self._load(version_name, ignore)


    def update(self, optimizer, loss, retain_graph=False):
        if self._training:
            optimizer.zero_grad()
            if torch.isnan(loss).item() == 0:
                loss.backward(retain_graph=retain_graph)
                optimizer.step()
            else:
                assert False, 'WARN: the optimising tensor is nan'

    def clean_grad(self, optimizer):
        optimizer.zero_grad()

    def forward(self, data, forward_mode, **kwargs):
        assert False, 'The method "forward" must be defined'

    def _to_train(self):
        for model in self.models:
            self.__dict__[model].train()

    def _to_eval(self):
        for model in self.models:
            self.__dict__[model].eval()

    def _get_models(self):
        self.models = []
        for name, value in self.__dict__.items():
            if issubclass(type(value), nn.Module):
                self.models.append(name)

    def _fit(self, epochs, batch_size, device, **kwargs):
        self._get_models()

        eval_per_step = kwargs.get('eval_per_step')
        eval_per_epoch = kwargs.get('eval_per_epoch')
        save_per_step = kwargs.get('save_per_step')
        save_per_epoch = kwargs.get('save_per_epoch')
        save_path = kwargs.get('save_path')

        kwargs['mode'] = 'train'

        for data_package in self.dataloader(batch_size, device, epochs, **kwargs):
            print_info = data_package['print_info']

            self._to_train()
            self._training = True
            ret_train = self.forward(data_package['train_data'], 'train', **kwargs)

            with torch.no_grad():
                valid_data = data_package['valid_data']
                self._training = False
                ret_valid = self.forward(valid_data, 'train', **kwargs) if valid_data is not None else None
                self._training = True

            yield ret_train, ret_valid, print_info

            if (eval_per_step is not None and (self.dataloader.step + 1) % eval_per_step == 0) or \
               (eval_per_epoch is not None and (self.dataloader.epoch + 1) % eval_per_epoch == 0):
                eval_batch_size = kwargs.get('eval_batch_size')
                if eval_batch_size is None:
                    eval_batch_size = batch_size

                self.dataloader.index_test = 0
                eval_score = self.evaluate(eval_batch_size, device, **kwargs)

                if eval_score is not None:
                    if eval_score >= self.checkpoint['best_eval_score']:
                        self.checkpoint['best_eval_score'] = eval_score
                        self._save('model_best', save_path)
                    print(('Evaluate Result: %s, Best: %s' % (eval_score, self.checkpoint['best_eval_score'])))

            if save_per_step is not None and (self.dataloader.step + 1) % save_per_step == 0:
                self._save('model_step:%s' % self.dataloader.step, save_path)

            if save_per_epoch is not None and (self.dataloader.epoch + 1) % save_per_epoch == 0:
                self._save('model_epoch:%s' % self.dataloader.epoch, save_path)

        if save_per_epoch is None and save_per_step is None:
            self._save('model_epoch:%s' % self.dataloader.epoch, save_path)
        print('\n')

    def callback(self, forward_train, forward_valid, print_info):
        train_info = 'train:'
        for name, value in list(forward_train.items()):
            train_info += '{name}: {value}, '.format(name=name, value=value)

        valid_info = 'valid:'
        if forward_valid is not None and len(forward_valid) > 0:
            for name, value in list(forward_valid.items()):
                valid_info += '{name}: {value}, '.format(name=name, value=value)

        self.print_log(print_info + train_info + valid_info)

    def fit(self, epochs, batch_size, save_path, device=pixtalks.default_device, **kwargs):

        eps = kwargs.get('eval_per_step')
        epe = kwargs.get('eval_per_epoch')
        sps = kwargs.get('save_per_step')
        spe = kwargs.get('save_per_epoch')
        kwargs['save_path'] = save_path

        for forward_train, forward_valid, print_info in self._fit(epochs, batch_size, device, **kwargs):
            self.callback(forward_train, forward_valid, print_info)

    def _evaluate(self, batch_size, device, **kwargs):
        if hasattr(self, '_models') is False:
            self._get_models()

        self._to_eval()
        self._training = False
        kwargs['mode'] = 'test'
        print('\n', end=' ')

        if kwargs.get('dataloader') is not None:
            dataloader = kwargs.get('dataloader')
        else:
            dataloader = self.dataloader

        # self.dataloader.index_test = 0
        for data_package in dataloader(batch_size, device, **kwargs):
            with torch.no_grad():
                ret_test = self.forward(data_package['test_data'], 'test', **kwargs)

            yield ret_test

            print_info = data_package['print_info']

            print(print_info, end=' ')

        self._to_train()
        self._training = True
        print('\r\n', end=' ')


    def evaluate(self, batch_size, device, **kwargs):
        assert False, 'The method "evaluate" must be defined'

    def _save(self, version_name, save_path, **kwargs):
        save_dict = {}
        for name, value in self.__dict__.items():
            if issubclass(type(value), nn.Module) or issubclass(type(value), op.Optimizer) \
                    or issubclass(type(value), DataLoader):
                # if 'dataloader' in name:
                #     print(f'save {name}', value.state_dict())
                save_dict[name] = value.state_dict()

        for key, value in self.save().items():
            if key in save_dict.keys():
                print('WARNING: 变量"{key}"被覆盖保存')
            save_dict[key] = value

        if kwargs.get('save_last_version_only') is True:
            pass

        self.checkpoint['last_version'] = version_name
        self.checkpoint['save_names'] = []

        for key, value in list(save_dict.items()):
            self.checkpoint['[{version_name}]{key}'.format(version_name=version_name, key=key)] = value
            self.checkpoint['save_names'].append(key)
            
        self.checkpoint['version_names'].add(version_name)
        
        try:
            torch.save(self.checkpoint, save_path)
        except:
            print(('ERROR: save unscessful, filename:%s' % save_path))
            # for key, value in self.checkpoint.items():
            #     print(key, type(value))
            #     try:
            #         torch.save({key: value}, key)
            #     except:
            #         pass
            torch.save(self.checkpoint, save_path)

    def save(self):
        return {}

    def save_model(self, version_name, filename):
        state_dict = self.checkpoint['[{version_name}]{key}'.format(version_name=version_name, key='model')]
        torch.save(state_dict, filename)

    def _load(self, version_name, ignore=None):
        if True:
            if version_name is None or version_name is 'last_version':
                version_name = self.checkpoint['last_version']

            # print('version_name', version_name)
            version_dict = {key: self.checkpoint['[{version_name}]{key}'.format(version_name=version_name, key=key)]
                            for key in self.checkpoint['save_names']}

            for name, value in version_dict.items():
                if hasattr(self, name):
                    var = self.__dict__[name]
                    if ignore is not None and var in ignore:
                        continue
                    # print(type(value), DataLoader)
                    if issubclass(type(var), nn.Module) or issubclass(type(var), op.Optimizer)\
                            or issubclass(type(var), DataLoader):

                        # if issubclass(type(value), DataLoader):
                        #     print('loading dataloader')
                        var.load_state_dict(value)

            self.load(version_dict)
        else:
            print('WARNING: load model failed.')

    def load(self, version_dict):
        pass
        # self.model.load_state_dict(version_dict['model'])

    def print_log(self, info):
        #python2
        print(info, end=' ')
        #python3

        # print(info, end='\r')


from .ClassifyTrainer import *
from .GenerativeAdversarialTrainer import *
from .VAETrainer import *
from .AutoEncoderTrainer import *
