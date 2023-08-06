import sys
sys.path.append('..')

from functools import partial
import torch.nn.functional as F
import torch.nn as nn
from torch import optim
import matplotlib.pyplot as plt
import bijou.callbacks as cbks
from bijou.learner import Learner
from bijou.metrics import accuracy
from bijou.modules import Lambda
from bijou.data import DataProcess as dp, Dataset, DataBunch
from datasets import mnist_data


class SequentialModel(nn.Module):  # pylint: disable=abstract-method
    def __init__(self, *layers):
        super().__init__()
        self.layers = nn.ModuleList(layers)
        self.act_means = [[] for _ in layers]
        self.act_stds = [[] for _ in layers]

    def __call__(self, x):
        for i, l in enumerate(self.layers):
            x = l(x)
            self.act_means[i].append(x.data.mean())
            self.act_stds[i].append(x.data.std())
        return x

    def __iter__(self):
        return iter(self.layers)


def conv2d(ni, nf, ks=3, stride=2):
    return nn.Sequential(
        nn.Conv2d(ni, nf, ks, padding=ks//2, stride=stride), nn.ReLU())


def get_cnn_layers(out_dim, nfs):
    nfs = [1] + nfs
    return [
        conv2d(nfs[i], nfs[i+1], 5 if i == 0 else 3)
        for i in range(len(nfs)-1)
    ] + [nn.AdaptiveAvgPool2d(1), Lambda(dp.flatten), nn.Linear(nfs[-1], out_dim)]


def view_tfm(*size):
    def _inner(x):
        return x.view(*((-1,)+size))
    return _inner


# ------ 获取数据
x_train, y_train, x_valid, y_valid = mnist_data()
x_train, x_valid = dp.normalize_to(x_train, x_valid)
train_ds, valid_ds = Dataset(x_train, y_train), Dataset(x_valid, y_valid)
bs = 512
loss_func = F.cross_entropy
data = DataBunch(*dp.get_dls(train_ds, valid_ds, bs))

# ------ 模型、优化器
nfs = [8, 16, 32, 32]
out_dim = y_train.max().item()+1
model = SequentialModel(*get_cnn_layers(out_dim, nfs))
opt = optim.SGD(model.parameters(), lr=0.9)

# ------ learner
cbfs = [partial(cbks.AvgStatsCallback, accuracy)]
mnist_view = view_tfm(1, 28, 28)
cbfs.append(partial(cbks.BatchTransformXCallback, mnist_view))
learner = Learner(model, opt, loss_func, data, callbacks=cbfs)

# ------ fit
learner.fit(2)

# ------ plot
for l in model.act_means:
    plt.plot(l)
plt.legend(range(6))
plt.show()
