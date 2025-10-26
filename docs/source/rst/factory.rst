


.. _factory:

=======
Factory
=======

Some factories help you creating the objects needed.
All of them are static classes such as ``FactoryXXXX`` that contains static methods to create.

-----------------------------------------------------------------------------------------------------------

Factory Simple
==============

------
Circle
------

Creates a circle, a ``SimpleShape`` instance from given ``radius`` and ``center``

.. code-block:: python
   
   from shapepy import Primitive
   circle = Primitive.circle(radius = 1, center = (0, 0))

.. figure:: ../img/primitive/positive_circle.svg
   :width: 50%
   :alt: SimpleShape instance circle of radius 1 and center (0, 0)
   :align: center

------
Square
------

Creates a square, a positive ``SimpleShape`` instance from given ``side`` and ``center``

.. code-block:: python
   
   from shapepy import Primitive
   square = Primitive.square(side = 1, center = (0, 0))

.. figure:: ../img/primitive/square.svg
   :width: 50%
   :alt: SimpleShape instance square of radius 1 and center (0, 0)
   :align: center

--------
Triangle
--------


Creates a triangle, a positive ``SimpleShape`` instance from given ``side`` and ``center``

.. code-block:: python
   
   from shapepy import Primitive
   triangle = Primitive.triangle(side = 1, center = (0, 0))

.. figure:: ../img/primitive/triangle.svg
   :width: 50%
   :alt: SimpleShape instance square of radius 1 and center (0, 0)
   :align: center

-------
Polygon
-------

Creates a polygon for given ``vertices``

.. code-block:: python
   
   from shapepy import Primitive
   vertices = [(1, 0), (0, 1), (-1, 1), (0, -1)]
   simple = Primitive.polygon(vertices)

.. figure:: ../img/primitive/diamond.svg
   :width: 50%
   :alt: SimpleShape instance square of radius 1 and center (0, 0)
   :align: center

---------------
Regular polygon
---------------

Creates a regular polygon, a positive ``SimpleShape`` instance

.. code-block:: python
   
   from shapepy import Primitive
   triangle = Primitive.regular_polygon(nsides = 3, radius = 1, center = (0, 0))
   square = Primitive.regular_polygon(nsides = 4, radius = 1, center = (0, 0))
   pentagon = Primitive.regular_polygon(nsides = 5, radius = 1, center = (0, 0))

|reg3|  |reg4|  |reg5|

.. |reg3| image:: ../img/primitive/regular3.svg
   :width: 32 %

.. |reg4| image:: ../img/primitive/regular4.svg
   :width: 32 %

.. |reg5| image:: ../img/primitive/regular5.svg
   :width: 32 %
