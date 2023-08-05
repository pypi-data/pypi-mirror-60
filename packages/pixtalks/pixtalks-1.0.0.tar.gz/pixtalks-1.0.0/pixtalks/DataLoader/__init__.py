import torch

def Bar(x):
    return pt.ProgressBar.SimpleBar(x)

def epo_epos(e, es):
    e = min([e + 1, es])
    return f'{e} / {es}'

def to_device(tensor, device):
    return tensor.to(device)


class DataLoader(object):

    dtype2str = {torch.int: 'int',
                 torch.int32: 'int32',
                 torch.int8: 'int8',
                 torch.int16: 'int16',
                 torch.int64: 'int64',
                 torch.long: 'long',
                 torch.short: 'short',
                 torch.float: 'float',
                 torch.float32: 'float32',
                 torch.float64: 'float64',
                 torch.float16: 'float16',
                 torch.double: 'double',
                 torch.uint8: 'uint8',
                 }
    str2dtype = {value: key for key, value in dtype2str.items()}

    @staticmethod
    def save_inputs(inputs):
        ret = {}
        for key, value in inputs.items():
            ret[key] = (DataLoader.dtype2str[value[0]], value[1])

        return ret

    @staticmethod
    def load_inputs(inputs):
        ret = {}
        for key, value in inputs.items():
            ret[key] = (DataLoader.str2dtype[value[0]], value[1])

        return ret

    def __init__(self, **kwargs):

        if len(kwargs) == 0:
            return

        self._inputs = kwargs.get('inputs')
        self._list_filename = kwargs.get('list_filename')
        self._data_root = kwargs.get('data_root')
        self._shuffle = kwargs.get('shuffle')
        self._random_seed = kwargs.get('random_seed')
        self._test_ratio = kwargs.get('test_ratio')
        self._test_data_root = kwargs.get('test_data_root')
        self._test_list_filename = kwargs.get('test_list_filename')
        self._validation_ratio = kwargs.get('validation_ratio')
        self._validation_data_root = kwargs.get('validation_data_root')
        self._validation_list_filename = kwargs.get('validation_list_filename')

        self.index = kwargs.get('index')
        self.index_valid = kwargs.get('index_valid')
        self.epoch = kwargs.get('epoch')
        self.step = kwargs.get('step')

        if self.index is None:
            self.index = 0
        if self.index_valid is None:
            self.index_valid = 0
        if self.epoch is None:
            self.epoch = 0
        if self.step is None:
            self.step = 0
        if self._data_root is None:
            self._data_root = ''
        if self._random_seed is None:
            self._random_seed = 0
        if self._shuffle is None:
            self._shuffle = False

        if self._list_filename is not None:
            self._LINES = self._get_lines(self._list_filename)
        else:
            self._LINES = []

        assert self._test_ratio is None or self._test_data_root is None, 'you can only choose at most one param ' \
                                                             'in test_ratio and test_data.'
        assert self._validation_ratio is None or self._validation_data_root is None, 'you can only choose at most one param ' \
                                                                               'in validation_ratio and validation_data.'

        test_cut_index = int(len(self._LINES) * self._test_ratio) if self._test_ratio is not None else 0
        validation_cut_index = -int(len(self._LINES) * self._validation_ratio) if self._validation_ratio is not None else len(self._LINES)

        self._Train = self._LINES[test_cut_index: validation_cut_index]
        self._Test = self._LINES[:test_cut_index]
        self._Valid = self._LINES[validation_cut_index:]

        if self._test_data_root is not None:
            self._Test = self._get_lines(self._test_list_filename)
        if self._validation_data_root is not None:
            self._Valid = self._get_lines(self._validation_list_filename)

        self.running = False
        self.index_test = 0

    def name(self):
        return self.__class__.__name__

    def state_dict(self):
        state_dict = {
            'name': str(self.__class__.__name__),
            'inputs': DataLoader.save_inputs(self._inputs),
            'list_filename': self._list_filename,
            'data_root': self._data_root,
            'shuffle': self._shuffle,
            'random_seed': self._random_seed,
            'test_ratio': self._test_ratio,
            'test_data_root': self._test_data_root,
            'test_list_filename': self._test_list_filename,
            'validation_ratio': self._validation_ratio,
            'validation_data_root': self._validation_data_root,
            'validation_list_filename': self._validation_list_filename,
            # =====================================================================
            'index': self.index,
            'index_valid': self.index_valid,
            'epoch': self.epoch,
            'step': self.step
        }
        return state_dict

    def load_state_dict(self, state_dict):
        if 'inputs' in state_dict.keys():
            state_dict['inputs'] = DataLoader.load_inputs(state_dict['inputs'])

        if state_dict['name'] != self.name():
            print(f"WARNING: you are loading a state dict with name {state_dict['name']}, but this dataloader's name "
                  f"is {self.name()}")
        super(self.__class__, self).__init__(**state_dict)

    def _get_lines(self, list_filename):

        lines = np.array(list(open(list_filename, 'r').readlines()), dtype=str)

        if self._shuffle:
            random.seed(self._random_seed)
            random.shuffle(lines)

        return lines

    def _summary(self):
        info = '====================================================================================\n' \
               'General Infomation\n' \
               'data_root: {data_root},\n' \
               'list_filename: {list_filename},\n' \
               'shuffle: {shuffle},\n' \
               'Train_Data: {train_len},\n' \
               'Test_Data: {test_len},\n' \
               'Valid_Data: {valid_len}\n' \
               '===================================================================================='
        info = info.format(data_root=self._data_root, list_filename=self._list_filename,
                           shuffle=self._shuffle, train_len=len(self._Train), test_len=len(self._Test),
                           valid_len=len(self._Valid))
        return info

    def summary(self):
        return self._summary()
    
    def __str__(self):
        return self.summary()

    def _get_data(self, data_root, line, **kwargs):
        assert False, 'method "get_data" must be defined'

    def _mode_2_data_root(self, mode):
        if mode == 'train':
            return self._data_root
        elif mode == 'test':
            return self._test_data_root if self._test_data_root is not None else self._data_root
        elif mode == 'valid':
            return self._validation_data_root if self._validation_data_root is not None else self._data_root
        else:
            assert False

    def _mode_2_lines(self, mode):
        if mode == 'train':
            return self._Train
        elif mode == 'test':
            return self._Test
        elif mode == 'valid':
            return self._Valid
        else:
            assert False

    def _mode_2_len(self, mode):
        if mode == 'train':
            return len(self._Train)
        elif mode == 'test':
            return len(self._Test)
        elif mode == 'valid':
            return len(self._Valid)
        else:
            assert False

    def _mode_2_index(self, mode):
        if mode == 'train':
            return self.index
        elif mode == 'test':
            return self.index_test
        elif mode == 'valid':
            return self.index_valid
        else:
            assert False

    def _index_add(self, mode, add):
        mode_len = self._mode_2_len(mode) - 1
        if mode == 'train':
            self.index += add
            self.step += 1
            if self.index >= mode_len:
                self.index = 0
                self.epoch += 1
        elif mode == 'test':
            self.index_test += add
            if self.index_test >= mode_len:
                self.index_test = 0
        elif mode == 'valid':
            self.index_valid += add
            if self.index_valid >= mode_len:
                self.index_valid = 0
        else:
            assert False


    def _get_batch(self, data_mode, batch, **kwargs):
        data_root = self._mode_2_data_root(data_mode)
        Data_Lines = self._mode_2_lines(data_mode)
        start_index = self._mode_2_index(data_mode)

        tensors = {}
        for name, dtype_shape in self._inputs.items():
            dtype, data_shape = dtype_shape
            if data_shape is None:
                tensors[name] = torch.empty(batch,).type(dtype)
            else:
                tensors[name] = torch.empty(batch, *data_shape).type(dtype)

        n = 0
        temp_add_index = 0
        for line in Data_Lines[start_index:]:
            datas = self._get_data(data_root, line, **kwargs)
            temp_add_index += 1
            if datas is None:
                continue
            for name, data in datas.items():
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
            return {name: tensor[:n] for name, tensor in tensors.items()}

    def __call__(self, batch, device, epochs=1, **kwargs):
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

        len_of_lines = self._mode_2_len(mode)

        while True:

            if mode is 'train' and self.epoch + 1 > epochs:
                break

            train_data = {name: value.to(device) for name, value in self._get_batch(data_mode, batch, **kwargs).items()}
            valid_data = {name: value.to(device) for name, value in self._get_batch('valid', batch, **kwargs).items()}

            index = self._mode_2_index(mode)
            # print(index)
            progress = float(index + 1) / len_of_lines if index != 0 else 1.0

            package = dict()
            package[data_name] = train_data
            package['valid_data'] = valid_data
            package['index_train'] = self.index

            if mode == 'train':
                package['print_info'] = f'\r[Epoch {epo_epos(self.epoch, epochs)}][{Bar(progress)}] '
            else:
                package['print_info'] = f'\r[Evaluating][{Bar(progress)}]'

            yield package

            if mode is 'test' and index == 0:
                break


from .ImageLoader import *
from .MultiDataLoader import *
from .MixtureDataLoader import *
from .TensorLoader import *
