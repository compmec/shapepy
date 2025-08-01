.. _v1.1.3:

======
v1.1.3
======

What has changed
----------------

* Divide package into simpler submodules.


.. _v1.1.2:

======
v1.1.2
======

What has changed
----------------

* Update python versions. It comes from `py3.7-py3.10` to `py3.9-py3.13`
* Increase code quality and style with `black` and `pylint`

.. _v1.1.0:

======
v1.1.0
======

Breaking changes
----------------

The package has been renamed from `compmec-shape` to `shapepy`.
Hence, the import must change from:

```python
from compmec.shape import Primitive
```

to

```python
from shapepy import Primitive
```


.. _v1.0.2:

======
v1.0.2
======

Fixes
-----
* Inversion of Simple Shape
* Split function of `JordanCurve` that separates its segments

What has changed
----------------
* Remove `copy()` methods, to implement them using standard `copy` 
* Refine algorithms of intersection between two `PlanarCurve`


.. _v1.0.0:

======
v1.0.0
======

New features
------------

Classes added:

* `Point2D` represents a point on the plane
* `BezierCurve` a generic bezier evaluator
* `PlanarCurve` a BezierCurve that accepts `Point2D` as control points
* `JordanCurve` a closed curve that does not intersect itself. Concatenation of `PlanarCurves`
* `Primitive` factory class that creates `SimpleShape`
* `EmptyShape` represents a empty set of points on the plane
* `SimpleShape` a bidimensional object that represents a region on a plane
* `ConnectedShape` represents the intersection of `SimpleShapes`
* `DisjointShape` represents a disjoint set of `SimpleShape` and `ConnectedShape`

Functions:

* It's possible to invert a shape with the symbol `~`
* It's possible to unite two shapes with the symbol `|` or `+`
* It's possible to intersect two shapes with the symbol `&` or `*`
* It's possible to make XOR operation between shapes with `^`
