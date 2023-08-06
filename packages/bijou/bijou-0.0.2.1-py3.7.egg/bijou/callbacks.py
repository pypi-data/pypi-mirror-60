import torch
import re
import math
from functools import partial
import matplotlib.pyplot as plt
from bijou.utils import ToolBox as tbox
from tqdm import tqdm
from bijou.hook import Hooks
from math import ceil


class CancelTrainException(Exception):
    pass


class CancelEpochException(Exception):
    pass


class CancelBatchException(Exception):
    pass


class StateErrorException(Exception):
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

    def set_learner(self, learner):
        self.learner = learner

    def __getattr__(self, k):
        return getattr(self.learner, k)

    @property
    def name(self):
        name = re.sub(r'Callback$', '', self.__class__.__name__)
        return camel2snake(name or 'callback')

    def __call__(self, cb_name):
        f = getattr(self, cb_name, None)
        if f and f():
            return True
        return False


class AvgStats():
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
            self.tot_mets[i] += m(learner.pred, learner.yb).item() * bn


class AvgStatsCallback(Callback):
    """
    该类型的回调最后只用一个，如果需要多个指标，则将多个指标组成列表，传到metrics参数即可
    """
    _order = 1

    def __init__(self, metrics, name='metrics'):
        self.train_stats = AvgStats(metrics, 'train')
        self.valid_stats = AvgStats(metrics, 'val')
        self.test_stats = AvgStats(metrics, 'test')
        self.name_ = name

    def begin_fit(self):
        self.learner.messages['stats_infos'] = {'train': None, 'val': None, 'test': None}
        self.learner.messages['metric_values'] = {}

    def begin_epoch(self):
        self.train_stats.reset()
        self.valid_stats.reset()

    def after_epoch(self):
        self.learner.messages['metric_values']['train'] = self.train_stats.avg_stats
        self.learner.messages['metric_values']['val'] = self.valid_stats.avg_stats

    def begin_test(self):
        self.test_stats.reset()

    def after_loss(self):
        if self.state == 'train':
            stats = self.train_stats
        elif self.state == 'val':
            stats = self.valid_stats
        elif self.state == 'test':
            stats = self.test_stats
        else:
            raise StateErrorException('Learner STATE must be in ["train", "val", "test"]!')

        with torch.no_grad():
            stats.accumulate(self.learner)

    def after_batch(self):
        if self.state == 'train':
            self.learner.messages['stats_infos']['train'] = self.train_stats.avg_stats
        elif self.state == 'val':
            self.learner.messages['stats_infos']['val'] = self.valid_stats.avg_stats

    def after_test(self):
        print(self.test_stats)


class ProgressBarCallback(Callback):
    _order = 0
    train_str = ''
    val_str = ''

    def begin_epoch(self):
        batch_num = len(self.data.train_dl)
        self.pbar = tqdm(total=batch_num,
                         bar_format=f'E {self.n_epochs + 1:<4} ' + 'B {n_fmt} {l_bar} {rate_fmt} | {postfix[0]}',
                         unit=' batch', postfix=[''])

    def begin_validate(self):
        self.pbar.reset(total=len(self.data.valid_dl))

    def after_batch(self):
        if self.state == 'train':
            if self.learner.messages['stats_infos']['train']:
                self.train_str = 'train-' + str(dictformat(self.messages['stats_infos']['train'])).replace("'", '')
            self.learner.messages['stats_infos']['train'] = None
        elif self.state == 'val':
            if self.learner.messages['stats_infos']['val']:
                self.val_str = 'val-' + str(dictformat(self.messages['stats_infos']['val'])).replace("'", '')
            self.learner.messages['stats_infos']['val'] = None
        else:
            return

        if self.state == 'train':
            self.pbar.postfix[0] = self.train_str
            self.pbar.update()

        elif self.state == 'val':
            self.pbar.postfix[0] = self.train_str + '  ' + self.val_str
            self.pbar.update()

    def after_epoch(self):
        self.pbar.close()

class TrainEvalCallback(Callback):
    def begin_fit(self):
        self.learner.n_epochs = 0.
        self.learner.n_iter = 0

    def after_batch(self):
        if self.state != 'train':
            return
        self.learner.n_epochs += 1./self.iters
        self.learner.n_iter += 1

    def begin_epoch(self):
        self.learner.n_epochs = self.epoch
        self.model.train()
        self.learner.state = 'train'

    def begin_validate(self):
        self.model.eval()
        self.learner.state = 'val'


class TestCallback(Callback):
    _order = 2

    def begin_test(self):
        self.model.eval()
        self.learner.state = 'test'


class Recorder(Callback):
    metric_of_epochs = []

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
        self.metric_of_epochs.append(self.messages['metric_values'])
        self.learner.messages['metric_values'] = {}

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

    def __init__(self, max_iter=100, min_lr=1e-6, max_lr=10):
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

    def __init__(self, device):
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

    def __init__(self, tfm):
        self.tfm = tfm

    def begin_batch(self):
        self.learner.xb = self.tfm(self.xb)


class LayerOutputAnalysisHookCallback(Callback):
    _order = 3

    def __init__(self, hook_mode='unit'):
        self.hook_mode = hook_mode

    def begin_fit(self):
        def append_stats(hook, module, inputs, outputs):  # pylint: disable=unused-argument
            if not hasattr(hook, 'stats'):
                hook.stats = ([], [], [])
            means, stds, hists = hook.stats
            means.append(outputs.data.mean().cpu())
            stds .append(outputs.data.std().cpu())
            hists.append(outputs.data.cpu().histc(40, -10, 10))

        self.hooks = Hooks(self.model, append_stats)

    def after_fit(self):
        self.plot()

    def plot(self):
        # 均值与标准差
        fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(12, 4))
        for h in self.hooks:
            ms, ss, _ = h.stats
            ax0.plot(ms, label=h.name)
            ax1.plot(ss, label=h.name)
            h.remove()
        ax0.legend(prop={'size': 6})
        ax0.set_title("Output feature's mean")
        ax1.legend(prop={'size': 6})
        ax1.set_title("Output feature's std")

        # 各层输出值的分布
        fig, axes = plt.subplots(int(ceil(len(self.hooks))/2), 2, figsize=(12, len(self.hooks)*1))
        for ax, h in zip(axes.flatten(), self.hooks):
            hist_matrix = torch.stack(h.stats[2]).t().float().log1p()
            im = ax.imshow(hist_matrix, origin='lower', extent=[0, hist_matrix.size()[1], -10, 10,], aspect='auto')
            ax.set_title(h.name)
            fig.colorbar(im, ax=ax, shrink=1.0)
        fig.subplots_adjust(hspace=0.5, top=0.85)
        fig.suptitle('Histogram of output feature values by "log(1+x)"')
        # plt.tight_layout()

        # 各层输出值中接近0的值的比例
        fig, axes = plt.subplots(int(ceil(len(self.hooks))/2), 2, figsize=(12, len(self.hooks)*1))
        for ax, h in zip(axes.flatten(), self.hooks):
            hist_matrix = torch.stack(h.stats[2]).t().float()
            tiny_ratio = hist_matrix[19:22].sum(0)/hist_matrix.sum(0)
            ax.plot(tiny_ratio)
            ax.set_ylim(0, 1.02)
            ax.set_title(h.name)
        fig.subplots_adjust(hspace=0.5, top=0.85)
        fig.suptitle('Fraction of tiny values in the output feature')


class ParamScheduler(Callback):
    _order = 1

    def __init__(self, pname, sched_funcs):
        self.pname, self.sched_funcs = pname, sched_funcs

    def begin_fit(self):
        if not isinstance(self.sched_funcs, (list, tuple)):
            self.sched_funcs = [self.sched_funcs] * len(self.opt.param_groups)

    def set_param(self):
        assert len(self.opt.param_groups) == len(self.sched_funcs)
        for pg, f in zip(self.opt.param_groups, self.sched_funcs):
            pg[self.pname] = f(self.n_epochs/self.epochs)

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


if __name__ == '__main__':
    a = torch.arange(0, 100)
    p = torch.linspace(0.01, 1, 100)

    # annealings = "NO LINEAR COS EXP".split()
    # fns = [sched_no, sched_lin, sched_cos, sched_exp]
    # for fn, t in zip(fns, annealings):
    #     f = fn(2, 1e-2)
    #     plt.plot(a, [f(o) for o in p], label=t)
    # plt.legend()
    # plt.show()

    sched = combine_scheds([0.3, 0.7], [sched_cos(0.3, 0.6), sched_cos(0.6, 0.2)])  # pylint: disable=no-value-for-parameter
    plt.plot(a, [sched(o) for o in p])
    plt.show()
