# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/0b_criteria.ipynb (unless otherwise specified).

__all__ = ['Criteria', 'granularities', 'random', 'large_final', 'small_final', 'large_init', 'small_init',
           'large_init_large_final', 'small_init_small_final', 'magnitude_increase', 'movement',
           'updating_magnitude_increase', 'updating_movement', 'grad_crit']

# Cell
import torch
import torch.nn as nn
import torch.nn.functional as F
from fastcore.basics import *
from fastcore.imports import *

# Cell
granularities = {'channel':1, 'vector':2, 'row':3, 'kernel':(2,3), 'filter':(1,2,3)}

class Criteria():
    def __init__(self, f, needs_init=False, needs_update=False, output_f=None, return_init=False):
        store_attr()
        assert (needs_init and needs_update)==False, "The init values will be overwritten by the updating ones."

    def __call__(self, m, granularity):
        if self.needs_update and hasattr(m, '_old_weights') == False:
            m.register_buffer("_old_weights", m._init_weights.clone()) # If the previous value of weights is not known, take the initial value

        if granularity == 'weight':
            wf = self.f(m.weight)
            if self.needs_init: wi = self.f(m._init_weights)
            elif self.needs_update: wi = self.f(m._old_weights)

        elif granularity in granularities:
            dim = granularities[granularity]
            wf = self.f(m.weight).mean(dim=dim, keepdim=True)
            if self.needs_init: wi = self.f(m._init_weights).mean(dim=dim, keepdim=True)
            elif self.needs_update: wi = self.f(m._old_weights).mean(dim=dim, keepdim=True)

        else: raise NameError('Invalid Granularity')

        if self.needs_update: m._old_weights = m.weight.clone() # The current value becomes the old one for the next iteration

        if self.output_f: return self.output_f(wf, wi)
        elif self.return_init: return wi
        else: return wf

# Cell
random = Criteria(torch.randn_like)

# Cell
large_final = Criteria(torch.abs)

# Cell
small_final = Criteria(compose(torch.abs, torch.neg))

# Cell
large_init = Criteria(torch.abs, needs_init=True, return_init=True)

# Cell
small_init = Criteria(compose(torch.abs, torch.neg), needs_init=True, return_init=True)

# Cell
large_init_large_final = Criteria(torch.abs, needs_init=True, output_f=torch.min)

# Cell
small_init_small_final = Criteria(torch.abs, needs_init=True, output_f=lambda x,y: torch.neg(torch.max(x,y)))

# Cell
magnitude_increase = Criteria(torch.abs, needs_init=True, output_f= torch.sub)

# Cell
movement = Criteria(noop, needs_init=True, output_f= lambda x,y: torch.abs(torch.sub(x,y)))

# Cell
updating_magnitude_increase = Criteria(torch.abs, needs_update=True, output_f= torch.sub)

# Cell
updating_movement = Criteria(noop, needs_update=True, output_f= lambda x,y: torch.abs(torch.sub(x,y)))

# Cell
def grad_crit(m, granularity):
    if m.weight.grad is not None:
        if granularity == 'weight':
            w = (m.weight*m.weight.grad).pow(2)

        elif granularity in granularities:
            dim = granularities[granularity]
            w = (m.weight*m.weight.grad).pow(2).mean(dim=dim, keepdim=True)

        else: raise NameError('Invalid Granularity')

        return w