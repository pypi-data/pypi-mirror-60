import torch
from bijou.utils import rename

@rename('acc')
def accuracy(out, yb):
    return (torch.argmax(out, dim=1) == yb).float().mean()


@rename('acc')
def masked_accuracy(pred, target):
    _, pred = pred.max(dim=1)
    correct = pred[target.mask].eq(target.data[target.mask]).sum()
    acc = correct / target.mask.float().sum()
    return acc
