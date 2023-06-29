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



Calculation of Cross-Section Properties
---------------------------------------

Many properties used to compute strain-stress from forces and momentum are given bellow.

As we don't integrate over the domain, we transform the integrals into boundary and integrate them by using the `Green's Theorem <https://en.wikipedia.org/wiki/Green%27s_theorem>`_. 

.. math::
  \iint_D \left(\dfrac{\partial M}{\partial x}-\dfrac{\partial L}{\partial y}\right) \ dx \, dy = \oint_C \left(L, \ M\right) \cdot \left(dx, \ dy\right)

By the domain D being a polygon, we integrate over the jordan curve which defines the region D.

.. math::
  \oint_{C} \left(L, \ M\right) \cdot \left(dx, \ dy\right) = \sum_{i} \int_{0}^{1} \left(L(t), \ M(t)\right) \cdot \left(\vec{p}_{i+1}-\vec{p}_i\right) \ dt


Cross-Sectional Area
^^^^^^^^^^^^^^^^^^^^

The area :math:`A` of the cross-section of domain :math:`D` is given by:

.. math::
  A = \int_D dx \, dy

We transform this integral over the boundary by setting :math:`L=0` and :math:`M=x`:

.. math::
  A = \oint_{C} \dfrac{1}{2}x^2 \ dy 
  
Since the path :math:`C` is a polygon, by getting the points :math:`\vec{p}_{i}` and :math:`\vec{p}_{i+1}` at the segment :math:`i`:

.. math::
  A = \sum_{i} \dfrac{1}{2}\left(x_i +x_{i+1}\right)\cdot \left(y_{i+1}-y_{i}\right)


First Moments of Area
^^^^^^^^^^^^^^^^^^^^^

The first moments of area are defined by:

.. math::
  Q_x & = \int_D y \ dx \ dy \\
  Q_y & = \int_D x \ dx \ dy


Picking specific :math:`L` and :math:`M`:

.. math::
  Q_x & = \oint_C -\dfrac{1}{2}y^2 \ dx \\
  Q_y & = \oint_C \dfrac{1}{2}x^2 \ dy

Since the path :math:`C` is a polygon,

.. math::
  Q_x & = \dfrac{1}{6}\sum_{i} \left(x_{i}-x_{i+1}\right)\left(y_{i}^2+y_{i}y_{i+1}+y_{i+1}^2\right) \\
  Q_y & = \dfrac{1}{6}\sum_{i} \left(x_{i}^2+x_{i}x_{i+1}+x_{i+1}^2\right)\left(y_{i+1}-y_{i}\right)


Second Moments of Area
^^^^^^^^^^^^^^^^^^^^^^

The second moments of area are defined by:

.. math::
  I_{xx} &= \oint_C y^2 \ dx \ dy \\
  I_{xy} &= \oint_C xy \ dx \ dy \\
  I_{yy} &= \oint_C x^2 \ dx \ dy


By picking specific :math:`L` and :math:`M`:

.. math::
  I_{xx} &= \oint_C -\dfrac{1}{3}y^3 \ dx \\
  I_{xy} &= \oint_C -xy^2 \ dx + x^2 y \ dy  \\
  I_{yy} &= \oint_C \dfrac{1}{3}x^3 \ dy 


Since the path :math:`C` is a polygon,

.. math::
  I_{xx} &=  \dfrac{1}{12}\sum_{i} \left(x_{i}-x_{i+1}\right)\left(y_{i}^3+y_{i}^2y_{i+1}+y_{i}y_{i+1}^2+y_{i+1}^3\right) \\
  I_{xy} &= \dfrac{1}{24}\sum_{i} \left(x_{i}\cdot y_{i+1} - x_{i+1}\cdot y_{i}\right)\left(2x_{i}y_{i}+x_{i}y_{i+1}+x_{i+1}y_{i}+x_{i+1}y_{i+1}\right) \\
  I_{yy} &= \dfrac{1}{12}\sum_{i} \left(x_{i}^3+x_{i}^2 x_{i+1}+x_{i}x_{i+1}^2+x_{i+1}^3\right)\left(y_{i+1}-y_{i}\right) 
