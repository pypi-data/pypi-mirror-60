import sys
sys.path.append('..')

from functools import partial
import torch.nn.functional as F
import torch.nn as nn
from torch import optim
import bijou.callbacks as cbks
from bijou.learner import Learner
from bijou.metrics import accuracy
from bijou.modules import Lambda
from bijou.data import DataProcess as dp, Dataset, DataBunch
from datasets import mnist_data


def mnist_resize(x):
    return x.view(-1, 1, 28, 28)


def get_cnn_model(out_dim):
    return nn.Sequential(
        Lambda(mnist_resize),
        nn.Conv2d(1, 8, 5, padding=2, stride=2), nn.ReLU(),  # 14
        nn.Conv2d(8, 16, 3, padding=1, stride=2), nn.ReLU(),  # 7
        nn.Conv2d(16, 32, 3, padding=1, stride=2), nn.ReLU(),  # 4
        nn.Conv2d(32, 32, 3, padding=1, stride=2), nn.ReLU(),  # 2
        nn.AdaptiveAvgPool2d(1),
        Lambda(dp.flatten),
        nn.Linear(32, out_dim)
    )


# ------ 获取数据
x_train, y_train, x_valid, y_valid = mnist_data()
x_train, x_valid = dp.normalize_to(x_train, x_valid)
train_ds, valid_ds = Dataset(x_train, y_train), Dataset(x_valid, y_valid)
bs = 512
loss_func = F.cross_entropy
data = DataBunch(*dp.get_dls(train_ds, valid_ds, bs))

# ------ 模型、优化器
out_dim = y_train.max().item()+1
model = get_cnn_model(out_dim)
opt = optim.SGD(model.parameters(), lr=0.4)

# ------ learner
cbfs = [partial(cbks.AvgStatsCallback, accuracy)]
learner = Learner(model, opt, loss_func, data, callbacks=cbfs)

# ------ fit
learner.fit(2)
