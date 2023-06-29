Theoretical Background
======================

Introduction
------------

Shape Generation
----------------

Jordan Curve
^^^^^^^^^^^^

`Jordan Curve <https://mathworld.wolfram.com/JordanCurve.html>`_ is a continuous closed curve which doesn't intersect itself.

.. figure:: ../img/theory/jordan_curve.svg
   :width: 70%
   :alt: Example of jordan curves 
   :align: center

For our purpose, we use oriented jordan curve by setting a **positive** direction: **counter-clockwise**.

A jordan curve defines a `simply connected <https://mathworld.wolfram.com/SimplyConnected.html>`_ regions. By adding and subtracting regions, it's possible to more complex shapes as **not simply connected**.

.. figure:: ../img/theory/simple_connected.svg
   :width: 90%
   :alt: Simple connected curves
   :align: center

Although a jordan curve is more general, we discretize it to get a polygon.
More points used in discretization, more realiable the final results will be, by also increasing the computational cost.

.. figure:: ../img/shape/sum_red_blue_mesh.svg
   :width: 70%
   :alt: Desired subtraction of original curves
   :align: center
.. figure:: ../img/shape/sum_red_blue_disc_border.svg
   :width: 70%
   :alt: Discretized subtraction with original border
   :align: center
.. figure:: ../img/shape/sum_red_blue_disc_noborder.svg
   :width: 70%
   :alt: Discretized subtraction
   :align: center


.. note::
   Even if your original jordan curve is already a polygon, maybe it's needed to discretize the edges due to the boundary elements, which we will see further. 
