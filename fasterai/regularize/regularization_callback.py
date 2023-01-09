# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/05_regularize.regularizer.ipynb.

# %% auto 0
__all__ = ['RegularizationCallback']

# %% ../../nbs/05_regularize.regularizer.ipynb 3
from fastai.callback.all import *
from fastcore.basics import store_attr
from ..core.criteria import *

import torch
import torch.nn as nn
import torch.nn.functional as F

# %% ../../nbs/05_regularize.regularizer.ipynb 4
class RegularizationCallback(Callback):
    "Callback to apply grouped weight decay"
    def __init__(self, granularity, wd=0.01):
        store_attr()

    def after_loss(self):
        reg = self.get_norm()
        self.learn.loss_grad += reg
        self.learn.loss = self.learn.loss_grad.clone()
        
    def get_norm(self):
        return self.wd*torch.stack([large_final.get_scores(m, large_final(m),self.granularity).sum() for m in self.learn.modules() if isinstance(m, nn.Conv2d)]).sum()
