# Standard Library
import math

# Third Party Library
import networkx as nx
import numpy as np
import scipy
import torch

# First Party Library
import config

device = config.select_device


class Env:
    def __init__(self, edges, feature, temper, alpha, beta) -> None:
        self.edges = edges
        self.feature = feature.to(device)
        self.temper = temper
        self.alpha = alpha
        self.beta = beta
        # 特徴量の正規化
        norm = self.feature.norm(dim=1)[:, None] + 1e-8
        self.feature = self.feature.div_(norm)
        self.feature_t = self.feature.t()

        return

    def reset(self, edges, attributes):
        self.edges = edges
        self.feature = attributes
        # 特徴量の正規化
        norm = self.feature.norm(dim=1)[:, None] + 1e-8
        self.feature = self.feature.div(norm)
        self.feature_t = self.feature.t()

    def step(self, actions):
        next_mat = actions.bernoulli()
        dot_product = torch.mm(self.feature, self.feature_t)
        reward = next_mat.mul(dot_product).mul(self.alpha)
        costs = next_mat.mul(self.beta)
        reward = reward.sub(costs)
        return reward.sum()

    def update_attributes(self, attributes):
        self.feature = attributes
        # 特徴量の正規化
        norm = self.feature.norm(dim=1)[:, None] + 1e-8
        self.feature = self.feature.div(norm)

        self.feature_t = self.feature.t()

    def state(self):
        neighbor_mat = torch.mul(self.edges, self.edges)
        return neighbor_mat, self.feature
