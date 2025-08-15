.. _v1.1.7:

======
v1.1.7
======

Fixes
-----
* Scaling and shifting Polynomial and Bezier analytics by @carlos-adir in https://github.com/compmec/shapepy/pull/54

Features
--------
* Allow creating points at infinity with polar coordinates by @carlos-adir in https://github.com/compmec/shapepy/pull/46
* Add parameter `derivative` in analytic or parameter curve call by @carlos-adir in https://github.com/compmec/shapepy/pull/47
* Use the `Polynomial` class to speed up computation of  __contains__ from segment by @carlos-adir in https://github.com/compmec/shapepy/pull/49
* Add domain property for Polynomial and Bezier by @carlos-adir in https://github.com/compmec/shapepy/pull/51
* Add `USegment`, which parametrization doesn't matter by @carlos-adir in https://github.com/compmec/shapepy/pull/57
* Add transformation functions to most 2D classes by @carlos-adir in https://github.com/compmec/shapepy/pull/58
* Add CyclicContainer to clean comparation in JordanCurve by @carlos-adir in https://github.com/compmec/shapepy/pull/59


Refactor
--------
* Move concatenation of geometric curves into separate file by @carlos-adir in https://github.com/compmec/shapepy/pull/48
* Divide submodule `bool2d/shape` into more parts to better maintainability by @carlos-adir in https://github.com/compmec/shapepy/pull/50
* Move split method from JordanCurve into PiecewiseCurve by @carlos-adir in https://github.com/compmec/shapepy/pull/52

Breaking changes
----------------
* Remove `^` and `@` operators for `Point2D` and Analytics in general by @carlos-adir in https://github.com/compmec/shapepy/pull/55
* Remove cast operations for bool2d instances by @carlos-adir in https://github.com/compmec/shapepy/pull/56




.. _v1.1.6:

======
v1.1.6
======

Fixes
-----
* Fix sphinx docs error due to bad format and position of staticmethod decorator by @carlos-adir in #38

Features
--------
* Create factory for Jordan Curve by @carlos-adir in #39
* Add base class for Polynomial and Bezier by @carlos-adir in #40

Tests
-----
* Set seed for random module to have reproducible tests by @carlos-adir in #37
* Add new Github Action to speed up check of PR in draft mode by @carlos-adir in #42

Refactor
--------
* Divide responsibilities of Jordan Curve by @carlos-adir in #36
* Refactor intersection of geometric curves by @carlos-adir in #44

Others
------
* Fix github actions triggers and badges by @carlos-adir in #43


.. _v1.1.5:

======
v1.1.5
======

What has changed
----------------

* Reorganize integration methods
    * Remove `IntegrateShape` to use `IntegrateJordan` directly
    * Move `IntegrateJordan` from `jordancurve` to separated file
* Add Direct and Adaptative quadrature methods
    * It's used for computing the length of a curve
* Changed numeric integration for analytic integration in polynomial methods
    * Computing the area and integral over shapes are now faster

.. _v1.1.4:

======
v1.1.4
======

What has changed
----------------

* Added `reals.py` to contains methods of conversion to scalar numbers 
* Added `Is` and `To` containers to help verification and conversion to common types
* Added `Angle` class to wrap float and evaluate angles
* Added `Polynomial` and `Bezier` classes to help evaluation of curves
* Removed `BezierCurve` from `geometry`
* Renamed `PlanarCurve` to `Segment`
* Added `length` property on `Segment` and `JordanCurve`
* Added `area` property on `JordanCurve`


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
