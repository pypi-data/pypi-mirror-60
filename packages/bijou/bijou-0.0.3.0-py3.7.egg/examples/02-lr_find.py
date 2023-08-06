import sys
sys.path.append('..')

import torch.nn.functional as F
import torch.nn as nn
from torch import optim
import matplotlib.pyplot as plt
from bijou.learner import Learner
from bijou.data import DataProcess as dp, Dataset, DataBunch
from datasets import mnist_data


# 1. ------ 获取数据
x_train, y_train, x_valid, y_valid = mnist_data()
train_ds, valid_ds = Dataset(x_train, y_train), Dataset(x_valid, y_valid)
bs = 512
data = DataBunch(*dp.get_dls(train_ds, valid_ds, bs))

# 2. ------ 模型和优化器
in_dim = data.train_ds.x.shape[1]
out_dim = y_train.max().item()+1
h_dim = 50
model = nn.Sequential(nn.Linear(in_dim, h_dim), nn.ReLU(), nn.Linear(h_dim, out_dim))
opt = optim.SGD(model.parameters(), lr=0.5)


# 3. ------ learner
loss_func = F.cross_entropy
learner = Learner(model, opt, loss_func, data)

# 4. ------ find lr
learner.find_lr(max_iter=100)

# 5. ------ plot
plt.show()
