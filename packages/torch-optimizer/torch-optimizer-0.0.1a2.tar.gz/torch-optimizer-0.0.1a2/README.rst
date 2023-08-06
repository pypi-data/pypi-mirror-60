torch-optimizer
===============
.. image:: https://travis-ci.com/jettify/pytorch-optimizer.svg?branch=master
    :target: https://travis-ci.com/jettify/pytorch-optimizer
.. image:: https://codecov.io/gh/jettify/pytorch-optimizer/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jettify/pytorch-optimizer
.. image:: https://img.shields.io/pypi/pyversions/torch-optimizer.svg
    :target: https://pypi.org/project/torch-optimizer
.. image:: https://img.shields.io/pypi/v/torch-optimizer.svg
    :target: https://pypi.python.org/pypi/torch-optimizer

**torch-optimizer** -- collection of optimizers for PyTorch_.


Simple example
--------------

.. code:: python

    import torch_optimizer as optim

    # model = ...
    optimizer = optim.DiffGrad(model.parameters(), lr=0.001)
    optimizer.step()


Installation
------------
Installation process is simple, just::

    $ pip install torch_optimizer


Supported Optimizers
====================

AccSGD
------

**Paper**: *On the insufficiency of existing momentum schemes for Stochastic Optimization* (2019) [https://arxiv.org/abs/1803.05591]

**Reference Code**: https://github.com/rahulkidambi/AccSGD


AdaMod
------
AdaMod method restricts the adaptive learning rates with adaptive and momental
upper bounds. The dynamic learning rate bounds are based on the exponential
moving averages of the adaptive learning rates themselves, which smooth out
unexpected large learning rates and stabilize the training of deep neural networks.

**Paper**: *An Adaptive and Momental Bound Method for Stochastic Learning.* (2019) [https://arxiv.org/abs/1910.12249v1]

**Reference Code**: https://github.com/lancopku/AdaMod

DiffGrad
--------
Optimizer based on the difference between the present and the immediate past
gradient, the step size is adjusted for each parameter in such
a way that it should have a larger step size for faster gradient changing
parameters and a lower step size for lower gradient changing parameters.

**Paper**: *diffGrad: An Optimization Method for Convolutional Neural Networks.* (2019) [https://arxiv.org/abs/1909.11015]

**Reference Code**: https://github.com/shivram1987/diffGrad

Lamb
----

**Paper**: *Large Batch Optimization for Deep Learning: Training BERT in 76 minutes* (2019) [https://arxiv.org/abs/1904.00962]

**Reference Code**: https://github.com/cybertronai/pytorch-lamb

RAdam
-----

**Paper**: *On the Variance of the Adaptive Learning Rate and Beyond* (2019) [https://arxiv.org/abs/1908.03265]

**Reference Code**: https://github.com/LiyuanLucasLiu/RAdam

SGDW
----

**Paper**: *SGDR: Stochastic Gradient Descent with Warm Restarts* (2017) [https://arxiv.org/abs/1904.00962]

**Reference Code**: https://arxiv.org/abs/1608.03983

Yogi
----
Yogi is optimization algorithm based on ADAM with more fine grained effective
learning rate control, and has similar theoretical guarantees on convergence as ADAM.

**Paper**: *Adaptive Methods for Nonconvex Optimization* (2018) [https://papers.nips.cc/paper/8186-adaptive-methods-for-nonconvex-optimization]

**Reference Code**: https://github.com/4rtemi5/Yogi-Optimizer_Keras


.. _Python: https://www.python.org
.. _PyTorch: https://github.com/pytorch/pytorch
