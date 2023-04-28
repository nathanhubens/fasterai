# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/01_sparse.sparsifier.ipynb.

# %% auto 0
__all__ = ['Sparsifier']

# %% ../../nbs/01_sparse.sparsifier.ipynb 3
import numpy as np
import torch
import torch.nn as nn
import pickle
from itertools import cycle
from fastcore.basics import store_attr, listify, true
from ..core.criteria import *

# %% ../../nbs/01_sparse.sparsifier.ipynb 5
class Sparsifier():
    "Class providing sparsifying capabilities"
    def __init__(self, model, granularity, context, criteria, layer_type=nn.Conv2d):
        store_attr()
        self._save_weights() # Save the original weights

    def prune_layer(self, m, sparsity, round_to=None):
        scores = self.criteria(m)
        setattr(m, '_mask', self._compute_mask(m, scores, sparsity, round_to))
        self._apply(m)
        self.criteria.update_weights(m)

    def prune_model(self, sparsity, round_to=None):
        self.threshold=None
        sparsity_list = listify(sparsity)
        if len(sparsity_list)>1: assert self.context=='local', f"A list of sparsities cannot be passed using: {self.context}"
        sparsities = cycle(sparsity_list) if len(sparsity_list)==1 else iter(sparsity_list)
        mods = list(self.model.modules())
        for k,m in enumerate(self.model.modules()):
            if isinstance(m, self.layer_type): 
                sp = next(sparsities)
                self.prune_layer(m, sp, round_to)
                if isinstance(mods[k+1], nn.modules.batchnorm._BatchNorm): self.prune_batchnorm(m, mods[k+1])
                
    def prune_batchnorm(self, m, bn):
        mask = getattr(m, "_mask", None)
        if self.granularity == 'filter' and mask:
            bn.weight.data.mul_(mask.squeeze())
            bn.bias.data.mul_(mask.squeeze())
            
    def _apply_masks(self):
        for m in self.model.modules():
            if isinstance(m, self.layer_type):
                self._apply(m)
        
    def _apply(self, m):
        mask = getattr(m, "_mask", None)
        if true(mask): m.weight.data.mul_(mask)
        if self.granularity == 'filter' and true(m.bias):
            if true(mask): m.bias.data.mul_(mask.squeeze()) # We want to prune the bias when pruning filters
    
    def _reset_weights(self, model=None):
        model = model or self.model
        for m in model.modules():
            if hasattr(m, 'weight'):
                init_weights = getattr(m, "_init_weights", m.weight)
                init_biases = getattr(m, "_init_biases", m.bias)
                with torch.no_grad():
                    if true(m.weight): m.weight.copy_(init_weights)
                    if true(m.bias): m.bias.copy_(init_biases)
                self._apply(m)
            if isinstance(m, nn.modules.batchnorm._BatchNorm): m.reset_parameters()
                
    def _save_weights(self):
        for m in self.model.modules():
            if hasattr(m, 'weight'):              
                m.register_buffer("_init_weights", m.weight.clone())
                bias = getattr(m, 'bias', None)
                if true(bias): m.register_buffer("_init_biases", bias.clone())
                    
    def save_model(self, path, model=None):
        model = model or self.model
        tmp_model = pickle.loads(pickle.dumps(model))
        self._reset_weights(tmp_model)
        self._clean_buffers(tmp_model)
        torch.save(tmp_model, path)

    def _clean_buffers(self, model=None):
        model = model or self.model
        for m in model.modules():
            if hasattr(m, 'weight'):
                if hasattr(m, '_mask'): del m._buffers["_mask"]
                if hasattr(m, '_init_weights'): del m._buffers["_init_weights"]
                if hasattr(m, '_init_biases'): del m._buffers["_init_biases"]
    
    def _compute_threshold(self, m, scores, sparsity):
        if self.context == 'global':
            if self.threshold is None: 
                global_criteria = torch.cat([self.criteria(m).view(-1) for m in self.model.modules() if isinstance(m, self.layer_type)]) # Get all scores
                global_scores = torch.cat([self.criteria.get_scores(m, self.granularity, True, global_criteria.min()).view(-1) for m in self.model.modules() if isinstance(m, self.layer_type)])
                self.threshold = torch.quantile(global_scores, sparsity/100) # Compute the threshold globally (only once per model pruning)
            scores = self.criteria.get_scores(m, self.granularity, True, self.criteria.min_value) # min_value is computed only once per prune_model
            return self.threshold, scores
        elif self.context == 'local':
            scores = self.criteria.get_scores(m, self.granularity)
            return torch.quantile(scores.view(-1), sparsity/100), scores
        else: raise NameError('Invalid Context')

    def _rounded_sparsity(self, n_to_prune, round_to):
        return max(round_to*torch.ceil(n_to_prune/round_to), round_to)
    
    def _compute_mask(self, m, scores, sparsity, round_to):
        self.threshold, scores = self._compute_threshold(m, scores, sparsity)
        if round_to:
            n_to_keep = sum(scores.ge(self.threshold)).squeeze()
            self.threshold = torch.topk(scores.squeeze(), int(self._rounded_sparsity(n_to_keep, round_to)))[0].min()
        if self.threshold > scores.max(): self.threshold = scores.max() # Make sure we don't remove every weight of a given layer
        return scores.ge(self.threshold).to(dtype=scores.dtype)
    
    def print_sparsity(self):
        for k,m in enumerate(self.model.modules()):
            if isinstance(m, self.layer_type):
                print(f"Sparsity in {m.__class__.__name__} {k}: {100. * float(torch.sum(m.weight == 0))/ float(m.weight.nelement()):.2f}%")
