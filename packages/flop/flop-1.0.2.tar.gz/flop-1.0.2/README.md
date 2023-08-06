# FLOP

Pytorch Library for L0 based pruning, as proposed in the paper:
[Structured Pruning of Large Language Models](https://arxiv.org/abs/1910.04732)

## Install

`pip install -U flop`

## Usage

Create a hard concrete mask of size N:

```python
from flop import HardConrete

N = 100
hardconcrete = HardConcrete(n_in=N)
```

You can then sample masks on the fly with:

```python
mask = hardconcrete()
```

Note that during evaluation, a mask is compiled and fixed.

You may also find these other objects useful:

- ``ProjectedLinear``: replaces a linear layer to include an intermediate projection.
- ``HardConreteProjectedLinear``: the hard conrete version of the ``ProjectedLinear`` module.

You may instantiate the HardConcrete objects directly, or you can choose to first train with
a ``ProjectedLinear`` module, and introduce the hardconcrete mask with:

```python
module = ProjectedLinear(...)
# Perform training

# ...

# Start pruning
pruning_module = HardConcreteProjectedLinear.from_module(module)
```

We also provide some utily functions to replace all ProjectedLinear modules in a model:

```python
from flop import make_hard_concrete

model = make_hard_concrete(model)
```

## Usage in Flambe

If you are using Flambe to train your models, then you could simply use the provided
``HardConcreteTrainer``, which will apply the ``make_hard_concrete`` method on your input
module, and perform training.

## Replicate results from the paper

To replicate the SRU numbers, please look at the script ``examples/train_enwik8.py``.

## Cite

```sh
@article{wang2019structured,
  title={Structured Pruning of Large Language Models},
  author={Wang, Ziheng and Wohlwend, Jeremy and Lei, Tao},
  journal={arXiv preprint arXiv:1910.04732},
  year={2019}
}
```
