# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/06_quantize.quantizer.ipynb.

# %% auto 0
__all__ = ['Quantizer']

# %% ../../nbs/06_quantize.quantizer.ipynb 2
import torch
import torch.nn as nn
import torch.nn.functional as F

from torch.ao.quantization import get_default_qconfig_mapping
import torch.ao.quantization.quantize_fx as quantize_fx
from torch.ao.quantization.quantize_fx import convert_fx, prepare_fx

# %% ../../nbs/06_quantize.quantizer.ipynb 4
class Quantizer():
    def __init__(self, backend="x86"):
        self.qconfig = get_default_qconfig_mapping(backend)
    
    def quantize(self, model, calibration_dl):
        x, _ = calibration_dl.valid.one_batch()
        model_prepared = prepare_fx(model.eval(), self.qconfig, x)
        _ = [model_prepared(xb.to('cpu')) for xb, _ in calibration_dl.valid]
            
        return convert_fx(model_prepared)
