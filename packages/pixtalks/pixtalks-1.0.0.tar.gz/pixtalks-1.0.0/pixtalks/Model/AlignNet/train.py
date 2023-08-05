from pixtalks import backend as P
import pixtalks as pt
from pixtalks.Trainer import Trainer
from pixtalks.DataLoader import DataLoader
from pixtalks.Model.AlignNet import AlignNet, AlignNet_v2
import torch.nn as nn
import torch.optim as op
import os
import cv2 as cv
import numpy as np

def load_txt(lines, length=6):
    output = np.empty((len(lines), length))
    for n, line in enumerate(lines):
        output[n] = np.array(line.split())
    return output.astype(np.float)

def load_rtpc(filename):
    with open(filename, 'r') as file:
        LINES = list(file.readlines())
        RT = LINES[0].replace('\n', '').split()
        R = np.array(RT[:9], dtype=np.float).reshape(3, 3)
        T = np.array(RT[9:], dtype=np.float)
        # print(LINES[1:])
        PC = load_txt(LINES[1:])
        pc_o = PC[np.random.permutation(len(PC)), :3]
        pc_a = PC[np.random.permutation(len(PC)), 3:]

    return R, T, P.from_numpy(pc_o), P.from_numpy(pc_a)

class AlignLoader(DataLoader):

    def __init__(self, **kwargs):
        super(AlignLoader, self).__init__(**kwargs)

        self._inputs = {'img': (P.float32, (1, 112, 96)),
                        'pc_o': (P.float32, (2048, 3)),
                        'pc_a': (P.float32, (2048, 3)),
                        'length': (P.int, None)}

    def get_data(self, data_root, line, **kwargs):
        # print(line)
        dir_path, name = line.replace('\n', '').split('/')
        depthmap_filename = os.path.join(self.data_root, dir_path, 'DepthMaps', name)
        label_filename = os.path.join(self.data_root, dir_path, 'Labels', name.replace('.png', '.txt'))

        img = cv.imread(depthmap_filename).transpose(2, 0, 1)[0].astype(np.float32)
        img = pt.Tensor(img)/255.
        # print(img)
        with pt.timer.Timer('rtpc'):
            R, T, pc_o, pc_a = load_rtpc(label_filename)
        length = len(pc_o)

        if len(pc_o) < 2048:
            pc_o = P.cat([pc_o, P.zeros((2048 - len(pc_o), 3))])

        if len(pc_a) < 2048:
            pc_a = P.cat([pc_a, P.zeros((2048 - len(pc_a), 3))])
        return {'img': img, 'pc_o': pc_o[:2048], 'pc_a': pc_a[:2048], 'length': length}

class AlignTrainer(Trainer):

    def __init__(self, lr, **kwargs):
        super(AlignTrainer, self).__init__(**kwargs)

        self.loss_function = nn.MSELoss()
        self.optimizer = op.SGD(self.model.parameters(), lr=lr)


    def pretrain(self):
        checkpoint = P.load(
            '/home/dj/anaconda3/envs/python2/lib/python2.7/site-packages/pixtalks/Model/AlignNet/AlignModel_v2.pkl')
        state = checkpoint['[model_best]model']
        current_state = self.model.state_dict()
        for key in current_state.keys():
            if key in state.keys():
                current_state[key] = state[key]
                print(('load key %s succeeful' % key))
            else:
                print(('load key %s unsucceeful' % key))
        self.model.load_state_dict(current_state)


    def forward(self, data, forward_mode, **kwargs):
        img = data['img']
        PC_O = data['pc_o']
        PC_A = data['pc_a']
        length = data['length']
        pc = []
        batch = img.size(0)

        R_pred, T_pred = self.model(img)

        loss_pc = P.zeros((1,)).cuda()
        # print(point_num)
        for loop_i in range(batch):
            pc_pred = P.matmul(PC_O[loop_i, :length[loop_i]], R_pred[loop_i]) + T_pred[loop_i]
            pc.append(pc_pred)
            loss_pc += self.loss_function(PC_A[loop_i, :length[loop_i]], pc_pred)
        loss_pc /= batch
        loss = loss_pc

        self.update(self.optimizer, loss)
        # print('i')
        if forward_mode == 'train':
            return {'loss': loss.item()}
        else:
            return {'loss': loss.item(), 'img': img, 'pc': pc}

    def evaluate(self, batch_size, device, **kwargs):
        loss = 0
        n = 0
        for data in self._evaluate(batch_size, device, **kwargs):
            loss += data['loss']
            n += 1
            # for img, pc in zip(data['img'], data['pc']):
            #     pt.savetxt('temp.txt', pc)
            #     rec_img = pt.GetDepthMap('temp.txt')
            #     R, T = pt.FaceAlign3D(rec_img)
            #     pc = P.matmul(pc, R.cuda()) + T.cuda()
            #     pt.savetxt('temp.txt', pc)
            #     rec_img2 = pt.GetDepthMap('temp.txt')
            #     print(img.shape, rec_img.shape)
            #     pt.imshow(img[0], rec_img, rec_img2)

        loss = loss/n

        return 1000 - loss

if __name__ == '__main__':
    pt.timer.show(False)
    model = AlignNet_v2(feature_dim=128, width_mult=1)
    model.cuda()

    dataloader = AlignLoader(data_root='/media/dj/DJ_Backups/3D_FaceAlign',
                             list_filename='/media/dj/DJ_Backups/3D_FaceAlign/train.txt',
                             shuffle=True, test_ratio=0.05, validation_ratio=0.05)
    trainer = AlignTrainer(lr=0.1, dataloader=dataloader, model=model, save_path='AlignModel_v3.pkl',
                           save_per_step=50, resume='AlignModel_v2.pkl', version_name='model_best')
    # trainer.pretrain()
    # trainer.evaluate(1, 'cuda')
    trainer.fit(epochs=30, batch_size=128, device='cuda', eval_per_step=50)
