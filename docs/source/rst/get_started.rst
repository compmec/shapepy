.. _get_started:

===========
Get started
===========

This library allows you to operate between **Shapes**, for example, the two shapes bellow can be united or can be intersected:

.. figure:: ../img/bool2d/base.svg
   :width: 50%
   :alt: Superposition of two shapes
   :align: center

|pic1|  |pic2|

.. |pic1| image:: ../img/bool2d/union.svg
   :width: 49 %

.. |pic2| image:: ../img/bool2d/intersect.svg
   :width: 49 %

---------------------------------------------------

First steps
===========

The first step is creating shapes to then operate them.
To create a **circle**, use the **Primitive**:

.. code-block:: python

    from shapepy import Primitive

    circle = Primitive.circle(radius = 1, center = (0, 0))

.. figure:: ../img/logo/logo1.svg
   :width: 50%
   :alt: The created circle with radius 1 and center the origin
   :align: center

Then we create a **square**

.. code-block:: python

    square = Primitive.square(side = 2, center = (-1, 0))

.. figure:: ../img/logo/logo2.svg
   :width: 50%
   :alt: The created square of side 2 and center at (-1, 0)
   :align: center

And hence we unite both shapes to create the *left* shape

.. code-block:: python

    left = square + circle  # Unite

.. figure:: ../img/logo/logo3.svg
   :width: 50%
   :alt: The union between a square and a circle created before
   :align: center

To create the *right* shape we can copy and transform using the functions **rotate** and **move**.

.. code-block:: python

    from copy import deepcopy
    from math import pi
    
    right = deepcopy(left).rotate(pi).move((0, -1))

.. figure:: ../img/logo/logo5.svg
   :width: 50%
   :alt: The superposition of the left shape and the created right shape
   :align: center

Now, we can intersect both the *left* and *right* shape, to obtain

.. code-block:: python

    intersection = left * right  # Intersection

.. figure:: ../img/logo/logo_intersection.svg
   :width: 50%
   :alt: The intersection between the left and the right shape
   :align: center

Visualize the shapes
====================

The shapes don't show by themselves, so se can use the ``matplotlib`` to visualize them.
We create an instance of ``PlotShape`` which was designed to be similar to ``matplotlib.pyplot``:

.. code-block:: python

    from shapepy import PlotShape

    # Create ploter
    plt = PlotShape()
    
    # Plot the left shape
    plt.plot(left, fill_color = "cyan")
    # Plot the right shape
    plt.plot(right, fill_color = "yellow")
    
    # Show images on screen
    plt.show()

Now we unite and intersect the ``left`` and ``right``:

.. code-block:: python

    # Unite left and right
    union = left + right
    
    # Intersect left and right
    intersection = left * right

We finally plot the figure

.. code-block:: python

    # Plot the union shape
    plt = PlotShape()
    plt.plot(union)

    # Plot the intersection shape
    plt = PlotShape()
    plt.plot(intersection)

    # Show images on screen
    plt.show()

-----------------------------------------------------------------------

Calculating integrals
=====================

You can integrate over the a shape or a curve,
that means you can find the area of shape,
its center of mass or the length of a curve.

TODO

-----------------------------------------------------------------------

Creating a mesh
===============

The optional library ``gmsh`` can be used to generate meshes from shapes.

TODO

-----------------------------------------------------------------------

Next steps
==========

Now you know the basics, we let you explore the other points of the package.

* :ref:`factory`: Functions to create shapes and others
* :ref:`features`: What you can do with the shapes
* :ref:`boolean`: How the booleans work, operations and transformations
* :ref:`geometry`: About the curves used under the hood
* :ref:`analytic`: The functions base for geometry
* :ref:`theory`: The fundations, hypothesis and algorithms used.

