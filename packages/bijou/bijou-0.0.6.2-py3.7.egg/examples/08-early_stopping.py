import sys
sys.path.append('..')

import torch.nn as nn
import torch.nn.functional as F
from torch import optim
from bijou.learner import Learner
from bijou.data import Dataset, DataLoader, DataBunch
from bijou.metrics import accuracy
from bijou.callbacks import EarlyStopping
from datasets import mnist_data

# 1. ------ 数据
x_train, y_train, x_valid, y_valid = mnist_data()
train_ds, valid_ds = Dataset(x_train, y_train), Dataset(x_valid, y_valid)
bs = 128
train_dl = DataLoader(train_ds, batch_size=bs, shuffle=True)
valid_dl = DataLoader(valid_ds, batch_size=bs, shuffle=True)
data = DataBunch(train_dl, valid_dl)

# 2. ------ 模型和优化器
in_dim = data.train_ds.x.shape[1]
out_dim = y_train.max().item()+1
h_dim = 50
model = nn.Sequential(nn.Linear(in_dim, h_dim), nn.ReLU(), nn.Linear(h_dim, out_dim))
opt = optim.SGD(model.parameters(), lr=1.3)


# 3. ------ learner
loss_func = F.cross_entropy
learner = Learner(model, opt, loss_func, data, metrics=[accuracy], callbacks=EarlyStopping(patience=3))

# 4. ------ fit
learner.fit(500)
