# Fasterai
> A library to make neural networks lighter and smaller


## How to use

You can use fasterai to remove useless parameters in your PyTorch neural network

```python
pruner = Sparsifier(model, granularity, method, criteria)
pruner.prune(sparsitiy)
```

But you can also use it as a fastai `Callback` to prune your model while it is training

```python
sparsifier = SparsifyCallback(sparsity, granularity, method, criteria, sched_func)
learn.fit_one_cycle(epochs, cbs=sparsifier)
```
