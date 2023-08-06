import sys
sys.path.append('..')

from functools import partial
import torch
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
    for l in model: # 模型参数初始化
        if isinstance(l, nn.Sequential):
            init.kaiming_normal_(l[0].weight)
            l[0].bias.data.zero_()

    opt = optim.SGD(model.parameters(), lr=0.4)


    # ------ learner
    mnist_view = view_tfm(1, 28, 28)
    cbfs = [partial(cbks.BatchTransformXCallback, mnist_view)]

    def accuracy1(*p):
        return accuracy(*p)
    learner = Learner(model, opt, loss_func, data, metrics=[accuracy, accuracy1], callbacks=cbfs)


    #  ------ hooks
    def append_stats(hook_, mod, inp, outp):   # pylint: disable=unused-argument
        if not hasattr(hook_, 'stats'):
            hook_.stats = ([], [], [])
        means, stds, hists = hook_.stats
        means.append(outp.data.mean().cpu())
        stds .append(outp.data.std().cpu())
        hists.append(outp.data.cpu().histc(40, 0, 10))  # histc isn't implemented on the GPU


    # ------ fit
    with hook.Hooks(model, append_stats) as hooks:
        learner.fit(3)


    # ------ plot
    def get_hist(h):
        return torch.stack(h.stats[2]).t().float().log1p()

    fig, axes = plt.subplots(2, 2, figsize=(15, 6))
    for ax, h in zip(axes.flatten(), hooks[:4]):
        ax.imshow(get_hist(h), origin='lower')
        ax.axis('off')
    plt.tight_layout()

    def get_min(h):
        h1 = torch.stack(h.stats[2]).t().float()
        return h1[:2].sum(0)/h1.sum(0)

    fig, axes = plt.subplots(2, 2, figsize=(15, 6))
    for ax, h in zip(axes.flatten(), hooks[:4]):
        ax.plot(get_min(h))
        ax.set_ylim(0, 1)
    plt.tight_layout()

    learner.recorder.plot_metrics()
    plt.show()
