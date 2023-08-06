import sys
sys.path.append('..')

from functools import partial
import torch.nn.functional as F
import torch.nn as nn
from torch.nn import init
from torch import optim
import matplotlib.pyplot as plt
import bijou.callbacks as cbks
import bijou.hook as hook
from bijou.learner import Learner
from bijou.metrics import accuracy
from bijou.modules import Lambda
from bijou.data import DataProcess as dp, Dataset, DataBunch
from datasets import mnist_data


def conv2d(ni, nf, ks=3, stride=2):
    return nn.Sequential(
        nn.Conv2d(ni, nf, ks, padding=ks//2, stride=stride), nn.ReLU())


def get_cnn_layers(out_dim, nfs):
    nfs = [1] + nfs
    return [
        conv2d(nfs[i], nfs[i+1], 5 if i == 0 else 3)
        for i in range(len(nfs)-1)
    ] + [nn.AdaptiveAvgPool2d(1), Lambda(dp.flatten), nn.Linear(nfs[-1], out_dim)]


def get_cnn_model(out_dim, nfs):
    return nn.Sequential(*get_cnn_layers(out_dim, nfs))


def view_tfm(*size):
    def _inner(x):
        return x.view(*((-1,)+size))
    return _inner


if __name__ == '__main__':
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
    model = get_cnn_model(out_dim, nfs)

    for l in model:  # 模型参数初始化
        if isinstance(l, nn.Sequential):
            init.kaiming_normal_(l[0].weight)
            l[0].bias.data.zero_()

    opt = optim.SGD(model.parameters(), lr=0.4)


    # ------ learner
    cbfs = [partial(cbks.AvgStatsCallback, accuracy)]
    mnist_view = view_tfm(1, 28, 28)
    cbfs.append(partial(cbks.BatchTransformXCallback, mnist_view))
    learner = Learner(model, opt, loss_func, data, callback_classes=cbfs)


    # ------ hooks
    def append_stats(hook_, mod, inp, outp):   # pylint: disable=unused-argument
        if not hasattr(hook_, 'stats'):
            hook_.stats = ([], [])
        means, stds = hook_.stats
        means.append(outp.data.mean())
        stds .append(outp.data.std())


    # ------ fit
    with hook.Hooks(model, append_stats) as hooks:
        learner.fit(2)


    # ------ plot
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(10, 4))
    for h in hooks:
        ms, ss = h.stats
        ax0.plot(ms[:10])
        ax1.plot(ss[:10])
    plt.legend(range(6))

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(10, 4))
    for h in hooks:
        ms, ss = h.stats
        ax0.plot(ms)
        ax1.plot(ss)
    plt.legend(range(6))

    plt.show()
