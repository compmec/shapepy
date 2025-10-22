.. _features:

========
Features
========

.. _integral:

Integral
--------

You can integrate over a line or over an area.

Since we describe the shapes by its boundaries, we transform the integral into a boundary integral by using Green's theorem.

Fortunatelly, the user can use it directly by using the functions.
If you want to know more, check out the Integral Theory.

.. code-block:: python
   
   from shapepy import Primitive, IntegrateShape
   
   # Creates a square of side 2 and centered at origin (0, 0)
   square = Primitive.square(side = 2)
   IntegrateShape.area(square)  # 4
   
   # Creates a circle of radius 1 and centered at origin (0, 0)
   circle = Primitive.circle(radius = 1)
   IntegrateShape.area(circle)  # 3.142221071689924
   
For any polynomial

.. code-block:: python
   
    from shapepy import Primitive, IntegrateShape
   
    square = Primitive.square(side = 2, center = (3, 4))
    area = IntegrateShape.polynomial(square, 0, 0)  # 4
    momentum_x = IntegrateShape.polynomial(square, 1, 0)  # 12
    momentum_y = IntegrateShape.polynomial(square, 0, 1)  # 16
    inertia_xx = IntegrateShape.polynomial(square, 2, 0)  # 112/3
    inertia_xy = IntegrateShape.polynomial(square, 1, 1)  # 48
    inertia_yy = IntegrateShape.polynomial(square, 0, 2)  # 196/3


.. _mesh:

Creating a mesh
---------------

