
# Fasterai



![header](https://capsule-render.vercel.app/api?type=waving&color=008080&height=300&section=header&text=fasterai%20&fontSize=90&animation=fadeIn&fontAlignY=38&desc=A%20Library%20to%20make%20smaller%20and%20faster%20neural%20networks&descAlignY=51&descAlign=62)

`fasterai` is a library created to make neural network smaller and faster. It essentially relies on common compression techniques for networks such as pruning, knowledge distillation, ...

## [Project Documentation](https://nathanhubens.github.io/fasterai/)

Visit [Read The Docs Project Page](https://nathanhubens.github.io/fasterai/) or read following README to know more about using Fasterai

##  Available Methods

### 1. Pruning

Make your model sparse (*i.e.* prune it) according to a:
- <b>Sparsity: </b> the amount of weights that will be replaced by 0
- <b>Granularity: </b> the granularity at which you operate the pruning (removing weights, vectors, kernels, filters)
- <b>Method: </b> prune either each layer independantly (local pruning) or the whole model (global pruning)
- <b>Criteria: </b> the criteria used to select the weights to remove (magnitude, movement, ...)
- <b>Schedule: </b> which schedule you want to use for pruning (one shot, iterative, gradual, ...)

### 2. Knowledge Distillation

Distill the knowledge acquired by a big model into a smaller one.

### 3. Lottery Ticket Hypothesis

Find the winning ticket in you network, *i.e.* the initial subnetwork able to attain at least similar performances than the network as a whole.

##  Quick Start

### 1. Create your model with fastai

```python
learn = cnn_learner(dls, model)
```

### 2. Get you Fasterai Callback

```python
sp_cb=SparsifyCallback(end_sparsity, granularity, method, criteria, sched_func)
```

### 3. Train you model to make it sparse !

```python
learn.fit_one_cycle(n_epochs, cbs=sp_cb)
```

> More about other methods in the [tutorials section](https://nathanhubens.github.io/fasterai/tutorial.schedules.html)

##  Installation


```
pip install git+https://github.com/nathanhubens/fasterai.git
```

or 

```
pip install fasterai
```

##  Citing
```
@misc{Hubens:2020,
  Author = {Nathan Hubens},
  Title = {Fasterai},
  Year = {2020},
  Publisher = {GitHub},
  Journal = {GitHub repository},
  Howpublished = {\url{https://github.com/nathanhubens/fasterai}}
}
```

![footer](https://capsule-render.vercel.app/api?type=waving&color=008080&height=100&section=footer)
