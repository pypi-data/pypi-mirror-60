import sys
sys.path.append('..')

from bijou.metrics import accuracy
from bijou.learner import Learner
from bijou.data import DataProcess as dp, Dataset, DataBunch
import torch.nn as nn
import torch.nn.functional as F
from torch import optim
from functools import partial
from datasets import mnist_data
import matplotlib.pyplot as plt


def get_model(in_dim, out_dim, lr=0.5, h_dim=50):
    model = nn.Sequential(nn.Linear(in_dim, h_dim), nn.ReLU(), nn.Linear(h_dim, out_dim))
    return model, optim.SGD(model.parameters(), lr=lr)


def get_model_func(lr=0.5):
    return partial(get_model, lr=lr)


# ------ 获取数据
x_train, y_train, x_valid, y_valid = mnist_data()
train_ds, valid_ds = Dataset(x_train, y_train), Dataset(x_valid, y_valid)
bs = 128
loss_func = F.cross_entropy
data = DataBunch(*dp.get_dls(train_ds, valid_ds, bs))

# ------模型、优化器
in_dim = data.train_ds.x.shape[1]
out_dim = y_train.max().item()+1
model, opt = get_model(in_dim, out_dim)

# ------ learner
learner = Learner(model, opt, loss_func, data, metrics=[accuracy])

# ------ fit
learner.fit_one_cycle(5, high_lr=0.35)

# ------ plot
learner.recorder.plot()
learner.recorder.plot_metrics()
plt.show()
