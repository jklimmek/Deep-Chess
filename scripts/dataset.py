import torch
from torch.utils.data import Dataset

from .utils import *


class DeepChessDataset(Dataset):
    """A dataset for training DeepChess engine.

    Training exmaple is constructed by randomly choosing one of the white positions and one of the black positions 
    and the side where to put white. Hence, the pair is either (W, L) or (L, W) where W is the position where
    white won and L is the position where white lost.
    """

    def __init__(self, white_positions, black_positions, poses_per_epoch=1000000):
        super().__init__()
        self.white_positions = white_positions
        self.black_positions = black_positions
        self.poses_per_epoch = poses_per_epoch

    def __len__(self):
        return self.poses_per_epoch
    
    def __getitem__(self, index):
        white_index = torch.randint(len(self.white_positions), (1,)).item()
        black_index = torch.randint(len(self.black_positions), (1,)).item()
        white_position = fen_to_array(self.white_positions[white_index])
        black_position = fen_to_array(self.black_positions[black_index])

        side = torch.randint(2, (1,)).item()

        if side == 0:
            return white_position, black_position, torch.tensor([1., 0.], dtype=torch.float32)
        else:
            return black_position, white_position, torch.tensor([0., 1.], dtype=torch.float32)


class AEDataset(Dataset):
    """A dataset for training autoencoder."""

    def __init__(self, positions):
        super().__init__()
        self.positions = positions

    def __len__(self):
        return len(self.positions)
    
    def __getitem__(self, index):
        return fen_to_array(self.positions[index])