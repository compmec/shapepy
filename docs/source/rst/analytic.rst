.. _analytic:

========
Analytic
========

This page refers to the submodule ``shapepy.analytic``.

Basically it contains real functions 


Polynomial
==========

You can create polynomial functions with the coefficients :math:`c_i`.

.. math::
    f(t) = \sum_{i=0}^{d} c_i \cdot t^i

Example
-------

Take the coefficients as ``[1, -3, 4]``, then you get

.. math::
    f(t) = 1 - 3 \cdot t + 4 \cdot t^2

.. code-block:: python

    >>> from shapepy.analytic import Polynomial
    >>> poly = Polynomial([1, -3, 4])
    >>> poly
    1 - 3 * x + 4 * x^2
    >>> poly(0)  # Evaluate at t = 0
    1
    >>> poly(1)  # Evaluate at t = 1
    2
    >>> poly(2)  # Evaluate at t = 2
    14

You can get some informations about the polynomial:

.. code-block:: python

    >>> from shapepy.analytic import Polynomial
    >>> poly = Polynomial([1, -3, 4])
    >>> poly.degree
    2
    >>> poly.derivate()
    -3 + 8 * x

Bezier
======

A Bezier basis is obtained from the expansion of the binomial:

.. math::
    1 = ((1-t) + t)^d = \sum_{i=0}^{d} \underbrace{\binom{d}{i} (1-t)^{d-i} \cdot t^i}_{B_{id}(t)} = \sum_{i=0}^{d} B_{id}(t)

Then, you can multiply every basis function :math:`B_{id}(t)` by a weight, also called control point :math:`c_i`.

.. math::
    f(t) = \sum_{i=0}^{d} c_i \cdot B_{id}(t)

Example
-------

Take the coefficients as ``[3, 7]``, then you get

.. math::
    f(t) = 3 \cdot (1-t) + 7 \cdot t

.. code-block:: python

    >>> from shapepy.analytic import Bezier
    >>> bezier = Bezier([3, 7])
    >>> bezier
    3 + 4 * t
    >>> bezier(0)  # Evaluate at t = 0
    3
    >>> bezier(0.5)  # Evaluate at t = 0.5
    5
    >>> bezier(2)  # Evaluate at t = 1
    7