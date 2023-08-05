#! /usr/bin/env python3

from .base_miner import BasePostGradientMiner
from ..utils import loss_and_miner_utils as lmu
import torch


class MultiSimilarityMiner(BasePostGradientMiner):
    def __init__(self, epsilon, **kwargs):
        super().__init__(**kwargs)
        self.epsilon = epsilon

    def mine(self, embeddings, labels):
        self.sim_mat = lmu.sim_mat(embeddings)

        a1, p, a2, n = lmu.get_all_pairs_indices(labels)

        if len(a1) == 0 or len(a2) == 0:
            return [], [], [], []

        sim_mat_pos_sorting = self.sim_mat.clone()
        sim_mat_neg_sorting = self.sim_mat.clone()

        sim_mat_pos_sorting[a2, n] = float('inf')
        sim_mat_neg_sorting[a1, p] = -float('inf')
        sim_mat_neg_sorting[range(len(labels)), range(len(labels))] = -float('inf')

        pos_sorted, pos_sorted_idx = torch.sort(sim_mat_pos_sorting, dim=1)
        neg_sorted, neg_sorted_idx = torch.sort(sim_mat_neg_sorting, dim=1)

        hard_pos_idx = (pos_sorted - self.epsilon < neg_sorted[:, -1].unsqueeze(1)).nonzero()
        hard_neg_idx = (neg_sorted + self.epsilon > pos_sorted[:, 0].unsqueeze(1)).nonzero()

        a1 = hard_pos_idx[:,0] 
        p = pos_sorted_idx[a1, hard_pos_idx[:,1]]
        a2 = hard_neg_idx[:,0]
        n = neg_sorted_idx[a2, hard_neg_idx[:,1]]
        
        return a1, p, a2, n
