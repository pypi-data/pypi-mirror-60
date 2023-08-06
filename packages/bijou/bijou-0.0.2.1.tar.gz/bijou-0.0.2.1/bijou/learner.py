"""
模型保存与加载
结果解解
各种计算指标
每层使用不同的学习率
各种优化技术：早停...
"""

import torch
from bijou.utils import ToolBox as tbox
import bijou.callbacks as cbks
from functools import partial
import matplotlib.pyplot as plt


class Learner():
    def __init__(self, model, opt, loss_func, data, metrics=None, cbs=None, cb_attrs=None, device=None):
        """
        Args:
            model: pytorch 模型
            opt: 优化器
            loss_func: 损失函数
            data: DataBunch
            metrics: 性能评价指标或评价指标列表
            cbs: callbacks对象列表
            cb_attrs: callbacks类列表，其中的每个callback会被作为 learner 的属性，
                以便于在fit后通过learner属性访问callback，例如Recorder
            device: cpu or gpu device
        """

        self.model, self.opt, self.data, self.loss_func = model, opt, data, loss_func
        self.state = 'train'  # 'train', 'val', 'test'
        self.messages = {}  # 存放callbacks之间共享的信息

        cbs = tbox.listify(cbs)
        cb_attrs = tbox.listify(cb_attrs) + [cbks.Recorder]
        # if metrics:
        cb_attrs += [partial(cbks.AvgStatsCallback, metrics)]
        for cbf in cb_attrs:
            cb = cbf()
            setattr(self, cb.name, cb)
            cbs.append(cb)

        self.cbs = [cbks.TrainEvalCallback(),
                    cbks.CudaCallback(device),
                    cbks.ProgressBarCallback()] + cbs

    def __call__(self, cb_name, reverse=False):
        res = False
        cb_list = sorted(self.cbs, key=lambda x: x._order)  # pylint: disable=protected-access
        if reverse:
            cb_list = reversed(cb_list)
        for cb in cb_list:
            res = cb(cb_name) or res
        return res

    def one_batch(self, xb, yb):
        try:
            self.xb, self.yb = xb, yb
            self('begin_batch', reverse=False)
            self.pred = self.model(self.xb)
            self('after_pred', reverse=True)
            self.loss = self.loss_func(self.pred, self.yb)
            self('after_loss', reverse=True)
            if self.state != 'train':  # 若不是训练状态，则结束batch
                return
            self.loss.backward()
            self('after_backward', reverse=True)
            self.opt.step()
            self('after_step', reverse=True)
            self.opt.zero_grad()
        except cbks.CancelBatchException:
            self('after_cancel_batch', reverse=True)
        finally:
            self('after_batch', reverse=True)

    def all_batches(self, dl):
        self.iters = len(dl)
        try:
            for xb, yb in dl:
                self.one_batch(xb, yb)
        except cbks.CancelEpochException:
            self('after_cancel_epoch', reverse=True)

    def run_fit(self, epochs):
        self.epochs, self.loss = epochs, torch.tensor(0.)

        try:
            for cb in self.cbs:
                cb.set_learner(self)
            self('begin_fit', reverse=False)
            for epoch in range(epochs):
                self.epoch = epoch
                if not self('begin_epoch', reverse=False):
                    self.all_batches(self.data.train_dl)

                if self.data.valid_dl is not None:
                    with torch.no_grad():
                        if not self('begin_validate', reverse=False):
                            self.all_batches(self.data.valid_dl)
                self('after_epoch', reverse=True)

        except cbks.CancelTrainException:
            self('after_cancel_train', reverse=True)
        finally:
            self('after_fit', reverse=True)
            # self.model, self.opt, self.loss_func, self.data = None, None, None, None

    def test(self, test_dl):
        test_cb = cbks.TestCallback()
        test_cb.set_learner(self)
        self.cbs += [test_cb]
        if not self('begin_test', reverse=False):
            with torch.no_grad():
                self.all_batches(test_dl)
        self('after_test', reverse=True)
        self.cbs.remove(test_cb)

    def predict(self, data_tensor):
        self.pred_data_tensor = data_tensor
        for cb in self.cbs:
            cb.set_learner(self)
        self('begin_predict', reverse=False)
        with torch.no_grad():
            pred = self.model(self.pred_data_tensor)
        return pred

    def fit(self, epochs):
        self.run_fit(epochs)

    def fit_one_cycle(self, epochs, stage=(0.3, 0.7), start_lr=0.01, high_lr=0.5, end_lr=0.01):
        sched = cbks.combine_scheds(stage,
                                    cbks.cos_1cycle_anneal(start_lr, high_lr, end_lr)
                                    )  # pylint: disable=no-value-for-parameter
        lr_shed_cb = cbks.ParamScheduler('lr', sched)
        self.cbs += [lr_shed_cb]
        self.run_fit(epochs)

        self.cbs.remove(lr_shed_cb)

    def find_lr(self, max_iter=100, min_lr=1e-6, max_lr=10, skip_last=5):
        lr_find_cbk = cbks.LR_Find(max_iter, min_lr, max_lr)
        self.cbs += [lr_find_cbk]
        self.run_fit(max_iter)

        self.recorder.plot_lr_loss(skip_last=skip_last)
        plt.xlabel('learning rate')
        plt.ylabel('loss')

        self.cbs.remove(lr_find_cbk)
