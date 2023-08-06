import torch
import pickle
import gzip
from pathlib import Path


def mnist_data():
    path = Path(__file__).parent/'example_datasets'/'mnist.pkl.gz'
    with gzip.open(path, 'rb') as f:
        ((x_train, y_train), (x_valid, y_valid), _) = pickle.load(f, encoding='latin-1')
    return map(torch.tensor, (x_train, y_train, x_valid, y_valid))
