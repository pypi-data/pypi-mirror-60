"""
使用了改进的ReLU
"""

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
from bijou.modules import Lambda, GeneralRelu
from bijou.data import DataProcess as dp, Dataset, DataBunch
from datasets import mnist_data


def conv2d(ni, nf, ks=3, stride=2):
    return nn.Sequential(
        nn.Conv2d(ni, nf, ks, padding=ks//2, stride=stride), nn.ReLU())


def get_cnn_layers(out_dim, nfs, layer, **kwargs):
    nfs = [1] + nfs
    return [layer(nfs[i], nfs[i+1], 5 if i == 0 else 3, **kwargs)
            for i in range(len(nfs)-1)] + [
        nn.AdaptiveAvgPool2d(1), Lambda(dp.flatten), nn.Linear(nfs[-1], out_dim)]


def conv_layer(ni, nf, ks=3, stride=2, **kwargs):
    return nn.Sequential(
        nn.Conv2d(ni, nf, ks, padding=ks//2, stride=stride), GeneralRelu(**kwargs))


def init_cnn(m, uniform=False):
    f = init.kaiming_uniform_ if uniform else init.kaiming_normal_
    for l in m:
        if isinstance(l, nn.Sequential):
            f(l[0].weight, a=0.1)
            l[0].bias.data.zero_()


def get_cnn_model(out_dim, nfs, layer, **kwargs):
    return nn.Sequential(*get_cnn_layers(out_dim, nfs, layer, **kwargs))


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
    model = get_cnn_model(out_dim, nfs, conv_layer, leak=0.1, sub=0.4, maxv=6.)
    init_cnn(model)

    opt = optim.SGD(model.parameters(), lr=0.4)


    # ------ learner
    cbfs = [partial(cbks.AvgStatsCallback, accuracy)]
    mnist_view = view_tfm(1, 28, 28)
    cbfs.append(partial(cbks.BatchTransformXCallback, mnist_view))

    sched = cbks.combine_scheds([0.2, 0.8], [cbks.sched_cos(0.2, 1.), cbks.sched_cos(1., 0.1)])  # pylint: disable=no-value-for-parameter
    cbfs = cbfs+[partial(cbks.ParamScheduler, 'lr', sched)]

    learner = Learner(model, opt, loss_func, data, callbacks=cbfs)


    # ------ hooks
    def append_stats(hook, mod, inp, outp):  # pylint: disable=unused-argument
        if not hasattr(hook, 'stats'):
            hook.stats = ([], [], [])
        means, stds, hists = hook.stats
        means.append(outp.data.mean().cpu())
        stds .append(outp.data.std().cpu())
        hists.append(outp.data.cpu().histc(40, -7, 7))


    # ------ fit
    with hook.Hooks(model, append_stats) as hooks:
        learner.fit(3)


    # ------ plot
    learner.recorder.plot_lr()
    # learner.recorder.plot_loss()

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(10, 4))
    for h in hooks:
        ms, ss, hi = h.stats
        ax0.plot(ms[:10])
        ax1.plot(ss[:10])
        h.remove()
    plt.legend(range(5))

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(10, 4))
    for h in hooks:
        ms, ss, hi = h.stats
        ax0.plot(ms)
        ax1.plot(ss)
    plt.legend(range(5))

    def get_hist(h):
        return torch.stack(h.stats[2]).t().float().log1p()
    fig, axes = plt.subplots(2, 2, figsize=(15, 6))
    for ax, h in zip(axes.flatten(), hooks[:4]):
        ax.imshow(get_hist(h), origin='lower')
        ax.axis('off')
    plt.tight_layout()

    def get_min(h):
        h1 = torch.stack(h.stats[2]).t().float()
        return h1[19:22].sum(0)/h1.sum(0)

    fig, axes = plt.subplots(2, 2, figsize=(15, 6))
    for ax, h in zip(axes.flatten(), hooks[:4]):
        ax.plot(get_min(h))
        ax.set_ylim(0, 1)
    plt.tight_layout()

    plt.show()
