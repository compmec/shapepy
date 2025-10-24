


.. _factory:

=======
Factory
=======

------------
Introduction
------------

Complex shapes can be created by operating basic shapes.
You can create simple shapes and then transforming and operating them.

These functions are divided in three groups:

* Create primitives shapes: ``square``, ``circle``, etc
* Transformations: ``move``, ``rotate`` and ``scale``
* Boolean operations: ``invert``, ``add``, ``sub``, ``mult``, etc


-----------------------------------------------------------------------------------------------------------

-----------------------
Create primitive shapes
-----------------------

Circle
------

Creates a circle, a positive ``SimpleShape`` instance from given ``radius`` and ``center``

.. code-block:: python
   
   from shapepy import Primitive
   circle = Primitive.circle(radius = 1, center = (0, 0))

.. figure:: ../img/primitive/positive_circle.svg
   :width: 50%
   :alt: SimpleShape instance circle of radius 1 and center (0, 0)
   :align: center

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

-----------------------------------------------------------------------------------------------------------

---------------
Transformations
---------------


-----------------------------------------------------------------------------------------------------------

------------------
Boolean Operations
------------------

The shapes respond to boolean operations: ``~``, ``|``, ``&``, ``-``, ``^``, ``+``, ``*``:

* Inversion: `~a` or `-a`
* Union: `a | b` or `a + b`
* Intersection: `a & b` or `a * b`
* Subtraction: `a - b`
* Exclusive union: `a ^ b`

.. note::
   Although two symbols can represent the same operation, they may return different objects. 
   For example: while `-a` inverts an object directly, `~a` returns a `LazyNot`.
   As consequence, `-(-a)` inverts an object twice, while `~(~a)` gives `a` directly.
   

-----------------------------------------------------------------------------------------------------------

Invert
------

It's possible to invert the orientation of a shape.

.. code-block:: python

   from shapepy import Primitive
   # Create any shape, positive at counter-clockwise
   circle = Primitive.circle()
   # Change orientation to clockwise, negative
   invcircle = ~circle


|pic1|  |pic2|

.. |pic1| image:: ../img/primitive/positive_circle.svg
   :width: 49 %

.. |pic2| image:: ../img/primitive/negative_circle.svg
   :width: 49 %

.. note::

   The ``invert`` function is available only in ``SimpleShape``. Use ``~shape`` for a inversion as general

Union
-----

The sum between two shapes is mathematically a union of two sets

.. code-block:: python

   from shapepy import Primitive
   # Create two simple shapes
   circle = Primitive.circle()
   square = Primitive.square()
   # Union
   newshape = circle + square

.. figure:: ../img/primitive/setAorB.svg
   :width: 40%
   :alt: Schema of adding sets :math:`A` and :math:`B`
   :align: center

.. figure:: ../img/primitive/or_table.svg
   :width: 80%
   :alt: Table of union between two positive circles
   :align: center


-----------------------------------------------------------------------------------------------------------

Intersection
------------

The intersection between two shapes returns the common region between them.

.. code-block:: python

   # Create two positive shapes
   from shapepy import Primitive
   circle = Primitive.circle()
   square = Primitive.square()
   # Intersection
   newshape = circle * square

.. figure:: ../img/primitive/setAandB.svg
   :width: 40%
   :alt: Example of multiplication between two positive shapes
   :align: center


.. figure:: ../img/primitive/and_table.svg
   :width: 80%
   :alt: Table of intersection between two positive circles
   :align: center


-----------------------------------------------------------------------------------------------------------

Subtraction
-----------

The subtraction between two positive shapes means take out all part of :math:`A` such is inside :math:`B`. 

.. code-block:: python

   from shapepy import Primitive
   # Create two positive shapes
   circle = Primitive.circle()
   square = Primitive.square()
   # Subtract
   newshape = circle - square

.. figure:: ../img/primitive/setAminusB.svg
   :width: 40%
   :alt: Schema of subtraction between sets :math:`A` and :math:`B`
   :align: center


.. figure:: ../img/primitive/sub_table.svg
   :width: 80%
   :alt: Table of subtraction between two positive circles
   :align: center



-----------------------------------------------------------------------------------------------------------

XOR Operator
------------

The xor between two positive shapes. For this operator, we use the symbol ``^``.

.. code-block:: python

   # Create two positive shapes
   from shapepy import Primitive
   circle = Primitive.circle()
   square = Primitive.square()
   # Subtract
   newshape = circle ^ square

.. figure:: ../img/primitive/setAxorB.svg
   :width: 40%
   :alt: Example of XOR between two positive shapes
   :align: center


.. figure:: ../img/primitive/xor_table.svg
   :width: 80%
   :alt: Table of XOR between two positive circles
   :align: center


-----------------------------------------------------------------------------------------------------------

Table with all the operations
-----------------------------

All the sub-operations (``+``, ``-``, ``*``, ``^``) operations are in fact only combinations of ``|``, ``&`` and ``~``. On the background, it works only with these three and the other operations are transformed:

* The ``A + B`` is transformed to ``A | B``
* The ``A * B`` is transformed to ``A & B``
* The ``A - B`` is transformed to ``A & (~B)``
* The ``A ^ B`` is transformed to ``(A - B) | (B - A)``

.. image:: ../img/primitive/all_bool_operations.svg
   :width: 100 %
   :alt: Operations between two positives simple shapes
   :align: center