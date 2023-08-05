from tkinter import *

import torch
import torch.nn as nn
import torch.optim as op
import pixtalks as pt
import os
import time
from pixtalks.DataLoader import ImageLoader
import random
from pixtalks.Trainer import ClassifyTrainer

map2 = {0: 'no', 1: 'yes'}

class LabelTool(object):

    def __init__(self, data_root, list_filename, data_shape, model, loss_function,
                 optimizer, fit_each_step, epoch_each_fit, save_name, auto_num, start=-1):
        self.data_root = data_root
        self.list_filename = list_filename
        self.model = model
        self.loss_function = loss_function
        self.optimizer = optimizer
        self.data_shape = data_shape
        self.fit_each_step = fit_each_step
        self.epoch_each_fit = epoch_each_fit
        self.save_name = save_name
        self.auto_num = auto_num

        self.LINES = [line.split()[0] for line in open(self.list_filename, 'r').readlines()]
        random.seed(0)
        random.shuffle(self.LINES)

        self.index = start
        self.len = len(self.LINES)

        self.Labels = []

        self.data_loader = ImageLoader(lambda x: x.split(), data_root=data_root, list_filename=list_filename,
                                       shuffle=False, Aug_Function=lambda x, **kw: x/255.,
                                       image_size=data_shape, dtype=torch.float32)
        self.data_loader.Train = self.Labels
        self.trainer = ClassifyTrainer(2, optimizer, loss_function, model=model, dataloader=self.data_loader,
                                       save_path='model.pkl', resume='model.pkl')

        self.YES = 0
        self.current_label = 0
        self.current_line = ''
        self.Total = 0


    def next(self, photo, label, **kwargs):
        if self.index >= self.len:
            return
        self.index += 1
        self.var_pro.set('%s / %s' % (self.index, self.len))
        if label is not None:
            if self.current_label == map2[label]:
                self.YES += 1
            self.Total += 1

        line = self.LINES[self.index]
        path = os.path.join(self.data_root, line)
        try:
            photo.configure(file=path)
        except:
            self.next(photo, None)
        s = self.current_line + ' ' + str(label)
        if label is not None:
            self.data_loader.Train.append(s)

        file = open(self.save_name, 'a')
        file.write(s + '\n')
        file.close()

        pred = map2[torch.argmax(self.trainer.predict(pt.imread(path).unsqueeze(0)/255.)).item()]

        self.current_label = pred
        self.current_line = line

        self.var_pred.set("model's prediction is: %s" % pred)

        acc = float(self.YES)/self.Total if self.Total > 0 else 0.0
        self.var_acc.set("model's accuracy is: %s" % acc)

        if self.Total == self.fit_each_step:
            self.Total = 0
            self.YES = 0

        if kwargs.get('auto') is not True and (self.index) % self.fit_each_step == 0:
            self.trainer.fit(self.epoch_each_fit, 128, 'cuda', not_show_info=True)
            self.trainer.checkpoint['epoch'] = 0
            self.trainer.checkpoint['step'] = 0

    def auto(self, photo):
        for _ in range(self.auto_num):
            try:
                path = os.path.join(self.data_root, self.current_line)
                pred = torch.argmax(self.trainer.predict(pt.imread(path).unsqueeze(0) / 255.)).item()
                self.next(photo, pred, auto=True)
            except:
                continue

    def start(self):
        root = Tk()
        frame = Frame(root)

        self.imgLabel = Label(frame)
        self.imgLabel.pack(side=TOP)

        var = StringVar()
        var.set('Classify it...')

        self.var_pred = StringVar()
        self.var_pred.set("model's prediction is:")

        self.var_acc = StringVar()
        self.var_acc.set("model's accuracy is:")

        self.var_pro = StringVar()
        self.var_pro.set("/")

        textLabel = Label(frame, textvariable=var)
        textLabel.pack(side=TOP)

        self.accLabel = Label(frame, textvariable=self.var_acc)
        self.accLabel.pack(side=BOTTOM)

        self.predLabel = Label(frame, textvariable=self.var_pred)
        self.predLabel.pack(side=BOTTOM)

        self.proLabel = Label(frame, textvariable=self.var_pro)
        self.proLabel.pack(side=BOTTOM)

        photo = PhotoImage()
        # path = os.path.join(self.data_root, self.LINES[0])
        self.imgLabel.configure(image=photo)
        self.next(photo, None)

        button1 = Button(frame, text='yes', command=lambda: self.next(photo, 1))
        button1.pack(side=LEFT)

        button2 = Button(frame, text='no', command=lambda: self.next(photo, 0))
        button2.pack(side=RIGHT)

        button3 = Button(frame, text='auto', command=lambda: self.auto(photo))
        button3.pack(side=BOTTOM)

        frame.pack(padx=10, pady=50)

        mainloop()


if __name__ == '__main__':
    feature_net = pt.Model.MobileFaceNet(1, 16, 32, 48, 1, (7, 6))
    model = pt.Model.ClassifyNet(feature_net, 48, 2)
    optimizer = op.SGD(model.parameters(), lr=0.1)
    lt = LabelTool('/media/dj/DJ_Backups/3D_FR_Data/FuShi_henan',
                   '/media/dj/DJ_Backups/3D_FR_Data/FuShi_henan/train.txt',
                   data_shape=(1, 112, 96), model=model, loss_function=nn.CrossEntropyLoss(), optimizer=optimizer,
                   fit_each_step=30, epoch_each_fit=5, save_name='labels.txt', auto_num=100000, start=-1)
    # lt.start()
    print((list(lt.trainer.checkpoint.keys())))
    lt.trainer.save_model('model_epoch:5', 'fushi_henan_label_model.pkl')
