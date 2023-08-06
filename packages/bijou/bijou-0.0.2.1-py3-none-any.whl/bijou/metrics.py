import torch
from bijou.utils import rename
import torch.nn.functional as F

@rename('acc')
def accuracy(out, yb):
    return (torch.argmax(out, dim=1) == yb).float().mean()


@rename('acc')
def masked_accuracy(pred, target):
    _, pred = pred.max(dim=1)
    correct = pred[target.mask].eq(target.data[target.mask]).sum()
    acc = correct / target.mask.float().sum()
    return acc

@rename('masked_nll')
def masked_nll_loss(pred, target):
    return F.nll_loss(pred[target.mask], target.data[target.mask])

def masked_mse(pred, target):
    return F.mse_loss(torch.squeeze(pred[target.mask]), target.data[target.mask])

def masked_mae(pred, target):
    pred = torch.squeeze(pred[target.mask])
    target = target.data[target.mask]
    return torch.mean(torch.abs(pred - target))
