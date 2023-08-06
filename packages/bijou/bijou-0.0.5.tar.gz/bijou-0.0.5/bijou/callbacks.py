import torch
import torch.nn as nn
import re
import math
from functools import partial
import matplotlib.pyplot as plt
from bijou.utils import ToolBox as tbox
from tqdm import tqdm
from bijou.hook import Hooks
from math import ceil
import numpy as np
import itertools


class CancelTrainException(Exception):
    pass


class CancelEpochException(Exception):
    pass


class CancelBatchException(Exception):
    pass


def camel2snake(name):
    """
    生成callback的名字
    """
    _camel_re1 = re.compile('(.)([A-Z][a-z]+)')
    _camel_re2 = re.compile('([a-z0-9])([A-Z])')

    s1 = re.sub(_camel_re1, r'\1_\2', name)
    return re.sub(_camel_re2, r'\1_\2', s1).lower()


def dictformat(dic):
    return str({k: f'{v:0.6f}' for k, v in dic.items()})


class Callback():
    """
    Callback的基类
    """
    _order = 0
    _name = None

    def __init__(self, as_attr=False, learner=None):
        """
        Args:
            as_attr: 是否将callback对象作为learner的属性
            learner: callback所属的Learner，若为空则后续可调用set_learner设置
        """
        self.as_attr = as_attr
        self.learner = learner

    def set_learner(self, learner):
        self.learner = learner

    def __getattr__(self, k):
        return getattr(self.learner, k)

    @property
    def name(self):
        if self._name is None:
            name = re.sub(r'Callback$', '', self.__class__.__name__)
            self._name = camel2snake(name or 'callback')
        return self._name

    def __call__(self, cb_name):
        f = getattr(self, cb_name, None)
        if f and f():
            return True
        return False


class AvgStats:
    def __init__(self, metrics, state):
        self.metrics, self.state = tbox.listify(metrics), state
        self.metric_names = ['loss'] + [m.__name__ for m in self.metrics]  # 构造metrics 名称

    def reset(self):
        self.tot_loss, self.count = 0., 0
        self.tot_mets = [0.] * len(self.metrics)

    @property
    def all_stats(self):
        return [self.tot_loss.item()] + self.tot_mets

    @property
    def avg_stats(self):
        if self.count > 0:
            return dict(zip(self.metric_names, [o/self.count for o in self.all_stats]))
        else:
            return {}

    def __repr__(self):
        if not self.count:
            return ""
        return f"{self.state}: {self.avg_stats}"

    def accumulate(self, learner):
        bn = len(learner.xb)  # .shape[0]
        self.tot_loss += learner.loss * bn
        self.count += bn
        for i, m in enumerate(self.metrics):
            self.tot_mets[i] += m(learner.predb, learner.yb).item() * bn


class AvgStatsCallback(Callback):
    """
    该类型的回调最后只用一个，如果需要多个指标，则将多个指标组成列表，传到metrics参数即可
    """
    _order = 1

    def __init__(self, metrics, **kwargs):
        super().__init__(**kwargs)
        self.train_stats = AvgStats(metrics, 'train')
        self.val_stats = AvgStats(metrics, 'val')
        self.test_stats = AvgStats(metrics, 'test')

    def begin_fit(self):
        self.learner.messages['metric_values_batch'] = {'train': None, 'val': None, 'test': None}
        self.learner.messages['metric_values_epoch'] = {}

    def begin_epoch(self):
        self.train_stats.reset()
        self.val_stats.reset()

    def after_epoch(self):
        self.learner.messages['metric_values_epoch']['train'] = self.train_stats.avg_stats
        self.learner.messages['metric_values_epoch']['val'] = self.val_stats.avg_stats

        # update best loss
        loss = self.messages['metric_values_epoch']['train']['loss']
        if loss < self.best_loss:
            self.learner.best_loss = loss

    def begin_test(self):
        self.test_stats.reset()

    def after_loss(self):
        stats = getattr(self, f'{self.state}_stats')
        with torch.no_grad():
            stats.accumulate(self.learner)

    def after_batch(self):
        self.learner.messages['metric_values_batch'][self.state] = getattr(self, f'{self.state}_stats').avg_stats


class ProgressBarCallback(Callback):
    _order = 0
    train_message = ''
    val_message = ''
    test_message = ''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def begin_epoch(self):
        batch_num = len(self.data.train_dl)
        self.pbar = tqdm(total=batch_num,
                         bar_format=f'E {self.epoch + 1:<4} ' + 'B {n_fmt} {l_bar} {rate_fmt} | {postfix[0]}',
                         unit=' batch', postfix=[''])

    def begin_validate(self):
        self.pbar.reset(total=len(self.data.valid_dl))

    def begin_test(self):
        self.pbar = tqdm(total=len(self.test_dl),
                         bar_format=f'TEST   ' + 'B {n_fmt} {l_bar} {rate_fmt} | {postfix[0]}',
                         unit=' batch', postfix=[''])

    def after_batch(self):
        if self.learner.messages['metric_values_batch'][self.state]:
            message = f'{self.state}-'
            message += str(dictformat(self.messages['metric_values_batch'][self.state])).replace("'", '')
            setattr(self, f'{self.state}_message', message)
            self.learner.messages['metric_values_batch'][self.state] = None

        if self.state == 'train':
            self.pbar.postfix[0] = self.train_message
        elif self.state == 'val':
            self.pbar.postfix[0] = self.train_message + '  ' + self.val_message
        elif self.state == 'test':
            self.pbar.postfix[0] = self.test_message
        self.pbar.update()

    def after_epoch(self):
        self.pbar.close()

    def after_test(self):
        self.pbar.close()


class TrainEvalCallback(Callback):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def begin_fit(self):
        self.learner.p_epochs = 0.
        self.learner.n_iter = 0

    def after_batch(self):
        if self.state != 'train':
            return
        self.learner.p_epochs += 1./self.iters
        self.learner.n_iter += 1

    def begin_epoch(self):
        self.learner.p_epochs = self.epoch
        self.model.train()
        self.learner.state = 'train'

    def begin_validate(self):
        self.model.eval()
        self.learner.state = 'val'


class TestCallback(Callback):
    _order = 2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def begin_test(self):
        self.model.eval()
        self.learner.state = 'test'


class Recorder(Callback):
    metric_of_epochs = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def begin_fit(self):
        self.lrs = [[] for _ in self.opt.param_groups]
        self.losses = []

    def after_batch(self):
        if self.state != 'train':
            return
        for pg, lr in zip(self.opt.param_groups, self.lrs):
            lr.append(pg['lr'])
        self.losses.append(self.loss.detach().cpu())

    def after_epoch(self):
        self.metric_of_epochs.append(self.messages['metric_values_epoch'].copy())

    def plot_lr(self, pgid=-1):
        plt.plot(self.lrs[pgid])

    def plot_loss(self, skip_last=0):
        plt.plot(self.losses[:len(self.losses)-skip_last], c='r')

    def plot(self):
        """
        plot learning and losses
        """
        fig = plt.figure(figsize=[10, 4])

        plt.subplot(121)
        self.plot_lr()
        plt.xlabel('n iter')
        plt.ylabel('learning rate')

        plt.subplot(122)
        self.plot_loss()
        plt.xlabel('n iter')
        plt.ylabel('loss')
        fig.subplots_adjust(wspace=0.3, bottom=0.18)

    def plot_lr_loss(self, skip_last=0, pgid=-1):
        losses = [o.item() for o in self.losses]
        lrs = self.lrs[pgid]
        n = len(losses)-skip_last
        plt.xscale('log')
        plt.plot(lrs[:n], losses[:n])

    def plot_metrics(self):
        trains_vals = ld2dl(self.metric_of_epochs)
        trains = ld2dl(trains_vals['train'])
        vals = trains_vals.get('val')  # 可能无验证集
        if vals:
            vals = ld2dl(vals)
        plt.figure(figsize=[len(trains) * 5, 4])
        for i, m in enumerate(trains):
            plt.subplot(1, len(trains), i + 1)
            plt.plot(trains[m], label='train')
            if vals:
                plt.plot(vals[m], label='val')
            plt.title(m, y=-0.2)
            plt.legend()
        plt.subplots_adjust(bottom=0.2)


def ld2dl(ld):
    dl = {}
    for d in ld:
        for k, v in d.items():
            if k not in dl:
                dl[k] = []
            dl[k].append(v)
    return dl


class LR_Find(Callback):
    _order = 1

    def __init__(self, max_iter=100, min_lr=1e-6, max_lr=10, **kwargs):
        super().__init__(**kwargs)
        self.max_iter, self.min_lr, self.max_lr = max_iter, min_lr, max_lr
        self.best_loss = 1e9

    def begin_batch(self):
        if self.state != 'train':
            return
        pos = self.n_iter/self.max_iter
        lr = self.min_lr * (self.max_lr/self.min_lr) ** pos
        for pg in self.opt.param_groups:
            pg['lr'] = lr

    def after_step(self):
        if self.n_iter >= self.max_iter or self.loss > self.best_loss*10:
            raise CancelTrainException()
        if self.loss < self.best_loss:
            self.best_loss = self.loss


class CudaCallback(Callback):
    _order = 0

    def __init__(self, device, **kwargs):
        super().__init__(**kwargs)
        if device is None:
            device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.device = device

    def begin_fit(self):
        self.model.to(self.device)

    def begin_batch(self):
        self.learner.xb, self.learner.yb = self.xb.to(self.device), self.yb.to(self.device)

    def begin_predict(self):
        self.model.to(self.device)
        self.learner.pred_data_tensor = self.pred_data_tensor.to(self.device)


class BatchTransformXCallback(Callback):
    _order = 2

    def __init__(self, tfm, **kwargs):
        super().__init__(**kwargs)
        self.tfm = tfm

    def begin_batch(self):
        self.learner.xb = self.tfm(self.xb)


class ParamScheduler(Callback):
    _order = 1

    def __init__(self, pname, sched_funcs, **kwargs):
        super().__init__(**kwargs)
        self.pname, self.sched_funcs = pname, sched_funcs

    def begin_fit(self):
        if not isinstance(self.sched_funcs, (list, tuple)):
            self.sched_funcs = [self.sched_funcs] * len(self.opt.param_groups)

    def set_param(self):
        assert len(self.opt.param_groups) == len(self.sched_funcs)
        for pg, f in zip(self.opt.param_groups, self.sched_funcs):
            pg[self.pname] = f(self.p_epochs/self.epochs)

    def begin_batch(self):
        if self.state == 'train':
            self.set_param()


def annealer(f):
    def _inner(start, end):
        return partial(f, start, end)
    return _inner


@annealer
def sched_linear(start, end, pos):
    return start + pos*(end-start)


@annealer
def sched_cos(start, end, pos):
    return start + (1 + math.cos(math.pi*(1-pos))) * (end-start) / 2


@annealer
def sched_no(start, end, pos):  # pylint: disable=unused-argument
    return start


@annealer
def sched_exp(start, end, pos):
    return start * (end/start) ** pos


def cos_1cycle_anneal(start, high, end):
    return [sched_cos(start, high), sched_cos(high, end)]  # pylint: disable=no-value-for-parameter


def combine_scheds(pcts, scheds):
    assert sum(pcts) == 1.
    pcts = torch.tensor([0] + tbox.listify(pcts))
    assert torch.all(pcts >= 0)
    pcts = torch.cumsum(pcts, 0)

    def _inner(pos):
        idx = (pos >= pcts).nonzero().max()
        actual_pos = (pos-pcts[idx]) / (pcts[idx+1]-pcts[idx])
        return scheds[idx](actual_pos)
    return _inner


class LayerAnalysisCallback(Callback):
    _order = 3

    def __init__(self, forward=True, hist_span=10, **kwargs):
        """
        forward: True, 各层forward输出分析; False, 各层backward输出梯度分析
        hist_span: histgram的分析范围。前向分析时应当大一些，例如10；后向分析时应当小一些，例如0.1。
        """
        super().__init__(**kwargs)
        self.forward = forward
        self.hist_span = [-hist_span, hist_span]

    def begin_fit(self):
        def append_stats(hook, module, inputs, outputs):  # pylint: disable=unused-argument
            if not hasattr(hook, 'stats'):
                hook.stats = ([], [], [])
            if isinstance(outputs, tuple):  # backward hook
                outputs = outputs[0]
            means, stds, hists = hook.stats
            means.append(outputs[0].data.mean().cpu())
            stds .append(outputs[0].data.std().cpu())
            hists.append(outputs[0].data.cpu().histc(40, *self.hist_span))

        self.hooks = Hooks(self.model, append_stats, self.forward)

    def after_fit(self):
        self.hooks.remove()
        self.plot()

    def plot(self):
        mode = 'FORWARD' if self.forward else 'BACKWARD'
        # 均值与标准差
        fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(12, 4))
        for h in self.hooks:
            ms, ss, _ = h.stats
            ax0.plot(ms, label=h.name)
            ax1.plot(ss, label=h.name)
        ax0.legend(prop={'size': 6})
        ax0.set_title(f"{mode}: Mean", fontsize=16)
        ax1.legend(prop={'size': 6})
        ax1.set_title(f"{mode}: Standard deviation", fontsize=16)

        # 各层输出值的分布
        figsize = (15, int(len(self.hooks)*0.7))
        fig, axes = plt.subplots(int(ceil(len(self.hooks)/3)), 3, figsize=figsize)
        [ax.axis('off') for ax in axes.flatten()]  # pylint:disable=expression-not-assigned
        for ax, h in zip(axes.flatten(), self.hooks):
            ax.axis('on')
            hist_matrix = torch.stack(h.stats[2]).t().float().log1p()
            extent = [0, hist_matrix.size()[1], *self.hist_span]
            im = ax.imshow(hist_matrix, origin='lower', extent=extent, aspect='auto')
            ax.set_title(h.name)
            fig.colorbar(im, ax=ax, shrink=1.0)
        fig.subplots_adjust(hspace=0.6, top=1-0.75/figsize[1])
        fig.suptitle(f'{mode}: Histogram of values by "log(1+x)"', fontsize=16)
        # plt.tight_layout()

        # 各层输出值中接近0的值的比例
        figsize = (15, int(len(self.hooks)*0.7))
        fig, axes = plt.subplots(int(ceil(len(self.hooks)/3)), 3, figsize=figsize)
        [ax.axis('off') for ax in axes.flatten()]  # pylint:disable=expression-not-assigned
        for ax, h in zip(axes.flatten(), self.hooks):
            ax.axis('on')
            hist_matrix = torch.stack(h.stats[2]).t().float()
            tiny_ratio = hist_matrix[19:22].sum(0)/hist_matrix.sum(0)
            ax.plot(tiny_ratio)
            ax.set_ylim(0, 1.02)
            ax.set_title(h.name)
        fig.subplots_adjust(hspace=0.6, top=1-0.75/figsize[1])
        fig.suptitle(f'{mode}: Fraction of tiny values', fontsize=16)


LayerOutputAnalysisHookCallback = LayerAnalysisCallback


class Checkpoints(Callback):
    _order = -1

    def __init__(self, epochs=1, path='./checkpoints', skip_worse=False, **kwargs):
        """
        Args:
            epochs: save checkpoint each 'epochs' epochs.
            path: path
            skip_worse: skip at worse loss epoch
        """
        super().__init__(**kwargs)
        self.per_epochs = epochs
        self.path = path
        self.skip_worse = skip_worse
        self.best_check_loss = float('inf')

    def after_epoch(self):
        if (self.epoch+1) % self.per_epochs == 0:
            if self.skip_worse:
                epoch_loss = self.messages['metric_values_epoch']['train']['loss']
                if epoch_loss < self.best_check_loss:
                    self.checkpoint(path=self.path)
                    self.best_check_loss = epoch_loss
            else:
                self.checkpoint(path=self.path)


class EarlyStopping(Callback):
    _order = -10000  # 保证最后执行

    def __init__(self, monitor='train', patience=10, min_delta=0., **kwargs):
        """
        Args:
            monitor: train loss or val loss
            patience: max patience epochs of getting worse
            min_delta: 小于 min_delta 的提升被认为没有变化
        """
        super().__init__(**kwargs)
        assert monitor in ['train', 'val'], '"monitor" must be "train" or "val"'
        self.monitor = monitor
        self.patience = patience
        self.min_delta = min_delta
        self.patience_num = 0

    def after_epoch(self):
        loss = self.messages['metric_values_epoch'][self.monitor]['loss']
        if loss > self.best_loss - self.min_delta:
            self.patience_num += 1
        else:
            self.patience_num = 0
        if self.patience_num >= self.patience:
            print('\n ... Early stopping is triggered!')
            raise CancelTrainException()


class GradientClipping(Callback):
    def __init__(self, max_norm=0., **kwargs):
        super().__init__(**kwargs)
        self.max_norm = max_norm

    def after_backward(self):
        if self.max_norm:
            nn.utils.clip_grad_norm_(self.model.parameters(), self.max_norm)


class InterpreterBase(Callback):
    _name = 'interpreter'

    def __init__(self, task_type, learner, multi_out):
        """
        Args:
            task_type: type of leaning task
            learner: learner
            multi_out: is the model have multi output
        """
        super().__init__(as_attr=True, learner=learner)
        assert task_type in ['classify', 'regress']  # 分类、回归任务
        self.task_type = task_type
        self.multi_out = multi_out
        self.cpu = torch.device('cpu')

        self._xbs_train = []
        self._xbs_val = []
        self._xbs_test = []
        self._ybs_train = []
        self._ybs_val = []
        self._ybs_test = []
        self._predbs_train = []
        self._predbs_val = []
        self._predbs_test = []

    def begin_fit(self):
        self.epoch_th = 0
        if self.task_type == 'classify':
            self.c_matrix_train = None
            self.c_matrix_val = None
            self.c_matrix_test = None
            self.c_dict_train = None
            self.c_dict_val = None
            self.c_dict_test = None

    def begin_epoch(self):
        self.epoch_th += 1

    def after_pred(self):
        if self.epoch_th == self.epochs or self.state == 'test':  # last epoch or test epoch
            getattr(self, f'_predbs_{self.state}').append(self.predb)
            getattr(self, f'_ybs_{self.state}').append(self.yb)
            getattr(self, f'_xbs_{self.state}').append(self.xb.to(self.cpu))  # 放入CPU中避免占用GPU存储

    def cat(self, target):
        raise Exception("To be rewrited!!!")

    def top_data(self, metric, target='train', largest=True, k=0):
        """
        返回metric指标最大（largest=True）或最小（largest=False）的k个数据。
        Args:
            metric: 计算指标
            target: 分析对象，'train', 'val' 或 'test'分别表示训练数据、验证数据或测试数据
            largest: 返回最大还是最小的k个数据
        Return: (top_scores, top_xs, top_ys, top_preds, top_index)即
                (metric最大值, 最大值对应的x, 最大值对应的y, 最大值对应的pred, {最大值所在batch及在batch中的位置})
        """
        assert target in ['train', 'val', 'test'], '"target" must be "train", "val" or "test"'
        self.cat(target)
        scores = []
        with torch.no_grad():
            for preb, yb in zip(getattr(self, f'_predbs_{target}'), getattr(self, f'_ybs_{target}')):
                scores.append(metric(preb, yb).detach().cpu())
        scores = torch.cat(scores)
        if k == 0:
            k = len(scores)
        top_k = scores.topk(k, largest=largest)
        top_indices = top_k.indices.numpy()

        batch_size = len(getattr(self, f'_ybs_{target}')[0])
        top_index = {
            'batch': [i // batch_size for i in top_indices],
            'index': [i % batch_size for i in top_indices]
        }

        top_scores = top_k.values.numpy()
        # top_xs = getattr(self, f'_x_{target}')[top_indices]
        top_xs = [getattr(self, f'_x_{target}')[i] for i in top_indices]
        top_ys = getattr(self, f'_y_{target}')[top_indices].numpy()
        top_preds = getattr(self, f'_pred_{target}')[top_indices].numpy()

        return top_scores, top_xs, top_ys, top_preds, top_index

    def confusion_matrix(self, target='train', return_dict=False):
        if self.task_type != 'classify':
            raise Exception('Confusion matrix only in "classify" tasks!')
        assert target in ['train', 'val', 'test']

        # 若已存在，不必再计算
        if return_dict:
            c_dict = getattr(self, f'c_dict_{target}')
            if c_dict is not None:
                return c_dict
        else:
            c_matrix = getattr(self, f'c_matrix_{target}')
            if c_matrix is not None:
                return c_matrix

        self.cat(target)

        pred_size = getattr(self, f'_pred_{target}').size()
        if len(pred_size) == 1:  # for sigmoid output classification
            self.class_num = 2
        else:
            self.class_num = pred_size[1]

        c_dict = {}
        for x, y, pred in zip(getattr(self, f'_x_{target}'),
                              getattr(self, f'_y_{target}'),
                              getattr(self, f'_pred_{target}')):
            if len(pred_size) == 1:
                key = (int(y.numpy().tolist()), pred.round().int().numpy().tolist())
            else:
                key = (int(y.numpy().tolist()), int(pred.argmax().numpy().tolist()))
            if key not in c_dict:
                c_dict[key] = []
            c_dict[key].append(x)

        c_matrix = np.zeros([self.class_num, self.class_num], dtype=int)
        for key, item in c_dict.items():
            c_matrix[key[0], key[1]] = len(item)

        setattr(self, f'c_dict_{target}', c_dict)
        setattr(self, f'c_matrix_{target}', c_matrix)

        if return_dict:
            return c_dict
        else:
            return c_matrix

    def plot_confusion(self, target='train', title='Confusion matrix', class_names=None,
                       normalize=False, norm_dec=2, cmap='Blues', **kwargs):
        if self.task_type != 'classify':
            raise Exception('Confusion matrix only in "classify" tasks!')
        assert target in ['train', 'val', 'test']

        c_matrix = self.confusion_matrix(target)

        if normalize:
            c_matrix = c_matrix.astype('float') / c_matrix.sum(axis=1)[:, np.newaxis]

        fig = plt.figure(**kwargs)

        plt.imshow(c_matrix, interpolation='nearest', cmap=cmap)
        plt.title(title)
        if class_names and len(tbox.listify(class_names)) == self.class_num:
            tick_marks = np.arange(self.class_num)
            plt.xticks(tick_marks, class_names, rotation=90)
            plt.yticks(tick_marks, class_names, rotation=0)

        thresh = c_matrix.max() / 2.
        for i, j in itertools.product(range(c_matrix.shape[0]), range(c_matrix.shape[1])):
            coeff = f'{c_matrix[i, j]:.{norm_dec}f}' if normalize else f'{c_matrix[i, j]}'
            plt.text(j, i, coeff, horizontalalignment="center", verticalalignment="center",
                     color="white" if c_matrix[i, j] > thresh else "black")

        ax = fig.gca()
        ax.set_ylim(self.class_num-.5, -.5)

        plt.tight_layout()
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.grid(False)
        fig.subplots_adjust(bottom=0.1)
        return fig

    def most_confused(self, target='train', k=5):
        if self.task_type != 'classify':
            raise Exception('Confusion matrix only in "classify" tasks!')
        assert target in ['train', 'dev']
        c_dict = self.confusion_matrix(target, return_dict=True)
        c_items = [c for c in c_dict.items() if c[0][0]!=c[0][1]]
        return sorted(c_items, key=lambda e: len(e[1]), reverse=True)[:k]


class InterpreterCallback(InterpreterBase):
    def __init__(self, task_type='classify', learner=None, multi_out=False):
        """
        Args:
            task_type: type of leaning task
            learner: learner
            multi_out: is the model have multi output
        """
        super().__init__(task_type, learner, multi_out)

    def cat(self, target):
        if getattr(self, f'_x_{target}', None) is None:
            setattr(self, f'_x_{target}', torch.cat(getattr(self, f'_xbs_{target}')))
        if getattr(self, f'_y_{target}', None) is None:
            setattr(self, f'_y_{target}', torch.cat(getattr(self, f'_ybs_{target}')).detach().cpu())
        if getattr(self, f'_pred_{target}', None) is None:
            if not self.multi_out:
                setattr(self, f'_pred_{target}', torch.cat(getattr(self, f'_predbs_{target}')).detach().cpu())
            else:
                predbs = getattr(self, f'_predbs_{target}')
                predbs = [torch.cat(predb, 1) for predb in predbs]
                setattr(self, f'_pred_{target}', torch.cat(predbs).detach().cpu())


class GraphSetInterpreterCallback(InterpreterBase):
    def __init__(self, task_type='classify', learner=None, multi_out=False):
        """
        Args:
            task_type: type of leaning task
            learner: learner
            multi_out: is the model have multi output
        """
        super().__init__(task_type, learner, multi_out)

    def cat(self, target):
        if getattr(self, f'_x_{target}', None) is None:
            databs = getattr(self, f'_xbs_{target}')
            data_list = []
            for b in databs:
                data_list.extend(b.to_data_list())
            setattr(self, f'_x_{target}', data_list)
        if getattr(self, f'_y_{target}', None) is None:
            setattr(self, f'_y_{target}', torch.cat(getattr(self, f'_ybs_{target}')).detach().cpu())
        if getattr(self, f'_pred_{target}', None) is None:
            if not self.multi_out:
                setattr(self, f'_pred_{target}', torch.cat(getattr(self, f'_predbs_{target}')).detach().cpu())
            else:
                predbs = getattr(self, f'_predbs_{target}')
                predbs = [torch.cat(predb, 1) for predb in predbs]
                setattr(self, f'_pred_{target}', torch.cat(predbs).detach().cpu())



class GraphInterpreterCallback(InterpreterBase):
    def __init__(self, task_type='classify', learner=None, multi_out=False):
        """
        Args:
            task_type: type of leaning task
            learner: learner
            multi_out: is the model have multi output
        """
        super().__init__(task_type, learner, multi_out)

    def cat(self, target):
        if getattr(self, f'_x_{target}', None) is None:
            data = getattr(self, f'_xbs_{target}')[0]
            setattr(self, f'_x_{target}', data.x)
        if getattr(self, f'_y_{target}', None) is None:
            ys = getattr(self, f'_ybs_{target}')[0].data
            setattr(self, f'_y_{target}', ys.detach().cpu())
        if getattr(self, f'_pred_{target}', None) is None:
            if not self.multi_out:
                setattr(self, f'_pred_{target}', torch.cat(getattr(self, f'_predbs_{target}')).detach().cpu())
            else:
                predbs = getattr(self, f'_predbs_{target}')
                predbs = [torch.cat(predb, 1) for predb in predbs]
                setattr(self, f'_pred_{target}', torch.cat(predbs).detach().cpu())


if __name__ == '__main__':
    pass
    # a = torch.arange(0, 100)
    # p = torch.linspace(0.01, 1, 100)

    # annealings = "NO LINEAR COS EXP".split()
    # fns = [sched_no, sched_lin, sched_cos, sched_exp]
    # for fn, t in zip(fns, annealings):
    #     f = fn(2, 1e-2)
    #     plt.plot(a, [f(o) for o in p], label=t)
    # plt.legend()
    # plt.show()

    # sched = combine_scheds([0.3, 0.7], [sched_cos(0.3, 0.6), sched_cos(0.6, 0.2)])  # pylint: disable=no-value-for-parameter
    # plt.plot(a, [sched(o) for o in p])
    # plt.show()
