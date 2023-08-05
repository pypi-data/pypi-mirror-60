import torch
import re
import math
from functools import partial
import matplotlib.pyplot as plt
from bijou.utils import ToolBox as tbox
from tqdm import tqdm


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
        return dict(zip(self.metric_names, [o/self.count for o in self.all_stats]))

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

    def begin_epoch(self):
        self.train_stats.reset()
        self.valid_stats.reset()

    def after_epoch(self):
        self.learner.metric_values = {'train': self.train_stats.avg_stats,
                                      'val': self.valid_stats.avg_stats}

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
            self.learner.infos['train'] = self.train_stats.avg_stats
        elif self.state == 'val':
            self.learner.infos['val'] = self.valid_stats.avg_stats

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
            if self.learner.infos['train']:
                self.train_str = 'train-' + str(dictformat(self.infos['train']))
            self.learner.infos['train'] = []
        elif self.state == 'val':
            if self.learner.infos['val']:
                self.val_str = 'val-' + str(dictformat(self.infos['val']))
            self.learner.infos['val'] = []
        else:
            return

        if self.state == 'train':
            self.pbar.postfix[0] = self.train_str.replace("'", '')
            self.pbar.update()

        elif self.state == 'val':
            self.pbar.postfix[0] = self.train_str.replace("'", '') + '  ' + self.val_str.replace("'", '')
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
        self.metric_of_epochs.append(self.metric_values)
        self.learner.metric_values = {}

    def plot_lr(self, pgid=-1):
        plt.plot(self.lrs[pgid])

    def plot_loss(self, skip_last=0):
        plt.plot(self.losses[:len(self.losses)-skip_last], c='r')

    def plot_lr_loss(self, skip_last=0, pgid=-1):
        losses = [o.item() for o in self.losses]
        lrs = self.lrs[pgid]
        n = len(losses)-skip_last
        plt.xscale('log')
        plt.plot(lrs[:n], losses[:n])

    def plot_metrics(self):
        trains_vals = ld2dl(self.metric_of_epochs)
        trains = ld2dl(trains_vals['train'])
        vals = ld2dl(trains_vals['val'])
        plt.figure(figsize=[len(trains) * 5, 5])
        for i, m in enumerate(trains):
            plt.subplot(1, len(trains), i + 1)
            plt.plot(trains[m], label='train')
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
