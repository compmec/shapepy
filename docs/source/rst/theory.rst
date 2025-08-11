.. _theory:

This page contains all the theory used to develop this packaged.
It can be resumed as a mix of set theory, analitic and parametric geometry on the plane :math:`\mathbb{R}^2`.

Hereafter we describe the main objects used in this study (`EmptyShape`, `WholeShape`, `Point`, `Curve` and `Shape`),
and how they interact with each other.


* :ref:`theory_point`
* :ref:`theory_curve`
    * :ref:`theory_curve_jordan`
* :ref:`theory_shape`
    * :ref:`theory_shape_simple`
    * :ref:`theory_shape_connected`
    * :ref:`theory_shape_disjoint`
* :ref:`theory_integral`
    * :ref:`theory_integral_curve`
    * :ref:`theory_integral_shape`
    * :ref:`theory_integral_polygonal`
    * :ref:`theory_integral_polynomial`
* :ref:`theory_contains`
    * :ref:`theory_contains_pinp`
    * :ref:`theory_contains_pinc`
    * :ref:`theory_contains_pins`
    * :ref:`theory_contains_cinc`
    * :ref:`theory_contains_cins`
    * :ref:`theory_contains_sins`
    * :ref:`theory_contains_simp`
* :ref:`theory_boolean`
    * :ref:`theory_bool_single`
    * :ref:`theory_bool_not`
    * :ref:`theory_bool_or`
    * :ref:`theory_bool_and`
    * :ref:`theory_bool_sub`
    * :ref:`theory_bool_xor`
* :ref:`theory_generalities`
    * :ref:`onedimen_integration`
    * :ref:`winding_function`

-----------------------------------------------------------------------------

.. _theory_point:

=====
Point
=====

Point is a 0-dimensional object defined by only a pair of real values :math:`(x, \ y)`.

It can also be understood as a mathematical set of a single element, meaning  :math:`\{(x, \ y)\}`

Let :math:`p_0 = \left(x_0, \ y_0\right)` and :math:`p_1 = \left(x_1, \ y_1\right)` be two points.
The operations between then are:

* Inner product :

.. math::
    \langle p_0, \ p_1 \rangle = x_0 \cdot x_1 + y_0 \cdot y_1

* Cross product :

.. math::
    p_0 \times p_1 = x_0 \cdot y_1 - x_1 \cdot y_0

* Norm L2 of a point :

.. math::
    \|p_0\| = \sqrt{x_0^2 + y_0^2}



.. _theory_curve:

=====
Curve
=====

Curves are one-dimensional objects, that contains a infinite number of connected points.
    
A curve can be defined as **implicit** or **parametrized** by one variable.

Examples:

* Implicit:

    * Circle

    .. math::
        C = \left\{\left(x, \ y\right) \in \mathbb{R}^2 : x^2 + y^2 = 1\right\}

    * Straight line

    .. math::
        C = \left\{\left(x, \ y\right) \in \mathbb{R}^2 : 2\cdot x + 5 \cdot y = 10\right\}

    * Hyperbola

    .. math::
        C = \left\{\left(x, \ \dfrac{1}{x}\right) \in \mathbb{R}^2 : x \in \mathbb{R}^{+}\right\}

* Parametrized:

    * Circle 

    .. math::
        C = \left\{\left(\cos t, \ \sin t\right) \in \mathbb{R}^2 : t \in \left[0, \ 2\pi\right] \subset \mathbb{R}\right\}

    * Straight line

    .. math::
        C = \left\{\left(2+t, \ 4+t\right) \in \mathbb{R}^2 : t \in \mathbb{R}\right\}

    * Hyperbola

    .. math::
        C = \left\{\left(\exp -t, \ \exp t\right) \in \mathbb{R}^2 : t \in \mathbb{R}\right\}

For this package
* **Segment** is a :math:`C^{1}` parametrized curve :math:`p(t)` defined on a interval :math:`\left[0, \ 1\right]`

* **PiecewiseCurve** is a parametrized curve that is a sequence of segments. 

The curve contains :math:`n` segments, that are described by using **knots** :math:`\left[t_0, \ t_1, \ \cdots, \ t_n\right]`.

.. math::
    p(t) = \begin{cases}p_{0}(t) \ \ \ \ \ \text{if} \ t_{0} \le t \le t_{1} \\ p_{1}(t) \ \ \ \ \ \text{if} \ t_{1} \le t \le t_{2} \\ \vdots \\ p_{n-1}(t) \ \ \ \ \ \text{if} \ t_{n-1} \le t \le t_{n} \end{cases}

* **JordanCurve** is also a piecewise curve, but it's continuous, closed and does not intersect itself.


.. _theory_curve_jordan:

Jordan curve
------------

The jordan curve used in this package:

* Is a **Closed Curve** that doesn't intersect itself.
* Is oriented, either counter-clockwise (positive) or clockwise (negative)
* Divides the plane in two regions: Interior and exterior
* Is either bounded, or can go to infinity only once.
* Can be parametrized by piecewise analitic curves

Examples:

* Counter-clockwise circle:

.. math::
    C = \left\{\left(\cos 2\pi t, \ \sin 2\pi t\right) \in \mathbb{R}^2 : t \in \left[0, \ 1\right]\right\}

* Straight line:

.. math::
    C = \left\{\left(2+3t, \ 3-4t\right) \in \mathbb{R}^2 : t \in \mathbb{R}\right\}

* Right hand of an Hyperbola

.. math::
    C = \left\{\left(\cosh t, \ \sinh t\right) \in \mathbb{R}^2 : t \in \mathbb{R}\right\}

.. note::
    Although the jordan curve can go to the infinity once, the current implementation doesn't allow it yet.


.. _theory_shape:

=====
Shape
=====

Shape is bi-dimensional object that can be obtained from union and intersection
of the internal regions of some **Jordan Curves**.

For this package, the shapes are classified in three types:

* **SimpleShape**: Defined by only one **JordanCurve**. It's the interior area if the jordan is counter-clockwise, otherwise it's the exterior area
* **ConnectedShape**: It's the intersection of some **SimpleShape**
* **DisjointShape**: It's the union of **SimpleShape** and **ConnectedShape**

.. _theory_shape_simple:

Simple Shape
------------

If the oriented jordan curve is counter-clockwise, the shape is positive.
If it's clockwise, then we say the shape is negative.

An integral is made to compute the absolute value of the area,
and the sign is accordingly with the jordan curve orientation.

.. _theory_shape_connected:

Connected Shape
---------------

Is similar to a simple shape but has holes.

It can be described as the intersection of some **Simple** shapes

.. math::
    C = \bigcup_{i} S_i

From construction, max of only one of :math:`S_i` is positive.
The order used is:

1. Simple shape with positive area comes first
2. Then order the rest in increasing order


.. _theory_shape_disjoint:

Disjoint Shape
--------------

It's the union of some disjoint **Simple** and **Connected** shapes.

It can be described as the union

.. math::
    D = \bigcup_{i} C_i

From construction, max of only one of :math:`C_i` is negative
The order used is:

1. Connected/Simple shape with negative area comes first
2. Then order the rest in decreasing order


.. _theory_integral:

========
Integral
========

One of the main uses of `shapepy` is to compute integrals.
It can assume two forms:

* Line integrals : When the integration occurs over a curve, one-dimensional integral

.. math::
    I = \int_{C} f(x, \ y) \ ds

.. math::
    I = \int_{C} \langle g(x, \ y) , \ ds\rangle

.. math::
    I = \int_{C} g(x, \ y) \times \ ds

* Shape integrals : Bidimensional

.. math::
    I = \int_{S} f(x, \ y) \ dx \ dy

The computation of the integral can change depending on the function and on the curve/shape.
Here we show how we compute 


.. _theory_integral_curve:

Curve integrals
---------------

Three types of line integrals were given.

.. math::
    I = \int_{C} f(x, \ y) \ ds = \sum_{k=0}^{n-1} \int_{t_k}^{t_{k+1}} f(x(t), \ y(t)) \ \|p'(t)\| \ dt

.. math::
    I = \int_{C} \langle g(x, \ y) , \ ds\rangle = \sum_{k=0}^{n-1} \int_{t_k}^{t_{k+1}} \langle g(x(t), \ y(t)), \  p'(t) \rangle \ dt

.. math::
    I = \int_{C} g(x, \ y) \times \ ds = \sum_{k=0}^{n-1} \int_{t_k}^{t_{k+1}} g(x(t), \ y(t)) \times  p'(t) \ dt



.. _theory_integral_shape:

Shape integrals
---------------

The shapes are classified in **Simple**, **Connected** and **Disjoint**.

* If :math:`S` is disjoint, then it's the union of subshapes :math:`S_i`, it's transformed

.. math::
    I = \int_{\cup_i S_{i}} f(x, \ y) \ dS = \sum_{i} \int_{S_i} f(x, \ y) \ dS

* If :math:`S` is connected, then it's the intersection of simple shapes :math:`S_i`, it's transformed

.. math::
    I = \int_{\cup_i S_{i}} f(x, \ y) \ dS = \sum_{i} \int_{S_i} f(x, \ y) \ dS

Meaning, the integral over **Connected** or **Disjoint** are transformed into integrals over **Simple** shapes.

The strategy to integrate over a simple shape is transform the integral over the area, into a integral over
the jordan curve (its boundary) by using Green's theorem

.. math::
    \int_{S} \left(\dfrac{\partial Q}{\partial x} - \dfrac{\partial P}{\partial y} \right) dx \ dy = \int_{C} P \ dx + Q \ dy

Without loss of generality, take :math:`\alpha \in \mathbb{R}` a constant, and set

.. math::
    P(x, \ y) = \left(\alpha - 1 \right) \int f(x, \ y) \ dy

.. math::
    Q(x, \ y) = \alpha \cdot \int f(x, \ y) \ dx

If :math:`f(x, \ y)` is polynomial then

.. math::
    f(x, \ y) = x^{a} \cdot y^{b}

Hence

.. math::
    P = \dfrac{\alpha-1}{b+1} \cdot x^{a} \cdot y^{b+1}
.. math::
    Q = \dfrac{\alpha}{a+1} \cdot x^{a+1} \cdot y^{b}

In special, take :math:`\alpha = (a+1)/(a+b+2)` and the integral is transformed

.. math::
    P \ dx + Q \ dy = \dfrac{x^{a} \cdot y^{b}}{a+b+2} \cdot \left(x \ dy - y \ dx\right)

.. math::
    I = \int_{S} x^{a} y_{b} \ dx \ dy = \dfrac{1}{a+b+2} \int_{C} x^{a} y^{b} \cdot \left(x \ dy - y \ dx\right)

Since every parametric curve is divided in :math:`n` intervals, it's written

.. math::
    I = \dfrac{1}{a+b+2} \sum_{k=0}^{n-1} \int_{t_k}^{t_{k+1}} x(t)^a \cdot y(t)^2 \cdot p(t) \times p'(t) \ dt

This integral is easier computed by using :ref:`onedimen_integration`.


.. _theory_integral_polygonal:

Polygonal
---------

In special, if :math:`S` is a polygon, the integrals can be simplified even more.
The curve can be divided into :math:`n` segments that connects two vertices :math:`V_k` and :math:`V_{k+1}`.

.. math::
    p(t) = (1-t) \cdot V_{k} + t \cdot V_{k+1}

.. math::
    x \ dy - y \ dx = p \times p' = V_{k} \times V_{k+1}

.. math::
    I = \int_{S} x^a y^b \ dx \ dy = \sum_{k=0}^{n-1} \dfrac{V_{k} \times V_{k+1}}{a+b+2} \underbrace{\int_{0}^{1} x^{a} y^{b} dt}_{I_{a,b,k}}

The right integral can be expanded and then use the integral of beta function

.. math::
    \int_{0}^{1} \left(1-t\right)^{a} \cdot t^b \ dt = \dfrac{1}{a+b+1} \cdot \dfrac{1}{\binom{a+b}{a}}

.. math::
    (a+b+1) \binom{a+b}{a} \cdot I_{a,b,k} = \sum_{i=0}^{a}\sum_{j=0}^{b}\binom{i+j}{j}\binom{a+b-i-j}{b-j}x_{k}^{a-i}x_{k+1}^{i}y_{k}^{b-j}y_{k+1}^{j}

.. math::
    \dfrac{(a+b+2)!}{a! \cdot b!} \cdot I = \sum_{k=0}^{n-1} \left(x_{k}y_{k+1}-x_{k+1}y_{k}\right)\sum_{i=0}^{a}\sum_{j=0}^{b} X_{k,i} \cdot M_{ij} \cdot Y_{k,j}

With

.. math::
    M_{ij} = \binom{i+j}{j}\binom{a+b-i-j}{b-j}; \ \ \ \ X_{k,i} = x_{k}^{a-i} \cdot x_{k+1}^{i}; \ \ \ \ Y_{k, j} = y_{k}^{b-j}y_{k+1}^{j}

.. code-block:: python

    def integrate(vertices: np.ndarray, a: int, b: int) -> float:
        vertices = np.array(vertices)
        if vertices.ndim != 2 or vertices.shape[1] != 2:
            raise ValueError(f"Invalid vertices! {vertices.shape}")
        matrix = np.zeros((a + 1, b + 1), dtype="int64")
        for i in range(a + 1):
            for j in range(b + 1):
                matrix[i, j] = sp.binomial(i + j, i) * sp.binomial(a + b - i - j, b - j)
        shiverts = np.roll(vertices, shift=-1, axis=0)
        cross = vertices[:, 0] * shiverts[:, 1] - vertices[:, 1] * shiverts[:, 0]
        xvand0 = np.vander(vertices[:, 0], a + 1)
        xvand1 = np.vander(shiverts[:, 0], a + 1, True)
        yvand0 = np.vander(vertices[:, 1], b + 1)
        yvand1 = np.vander(shiverts[:, 1], b + 1, True)
        soma = np.einsum("k,ki,ki,ij,kj,kj", cross, xvand0, xvand1, matrix, yvand0, yvand1)
        denom = (a + b + 2) * (a + b + 1) * sp.binomial(a + b, a)
        return soma / denom



.. _theory_integral_polynomial:

Polynomial
----------

If :math:`S` is a polygonomial by parts, then for an interval :math:`\left[t_k, \ t_{k+1}\right]`

.. math::
    x_{k}(t) = x_0 + x_1 \cdot t + \cdots + x_q \cdot t^q
.. math::
    y_{k}(t) = y_0 + y_1 \cdot t + \cdots + y_q \cdot t^q



.. _theory_contains:

========
Contains
========

Deciding if a set :math:`A` is (or not) a subset of :math:`B` is not a trivial.
This section describes the algorithms to decide it.

Basically either :math:`A` and :math:`B` can assume the forms of **EmptyShape**, **Point**, **Curve**, **Shape**, **WholeShape**

That means, :math:`5 \times 5 = 25` possibilities.
The table here after reduces the quantity of verifications to 6, 
which are represented by the empty spaces

.. table::
    :align: center

    +-------+-------+-------+-------+-------+-------+
    |       | EmptyShape | Point | Curve | Shape | WholeShape |
    +=======+=======+=======+=======+=======+=======+
    | EmptyShape |   T   |   T   |   T   |   T   |   T   |
    +-------+-------+-------+-------+-------+-------+
    | Point |   F   |       |       |       |   T   |
    +-------+-------+-------+-------+-------+-------+
    | Curve |   F   |   F   |       |       |   T   |
    +-------+-------+-------+-------+-------+-------+
    | Shape |   F   |   F   |   F   |       |   T   |
    +-------+-------+-------+-------+-------+-------+
    | WholeShape |   F   |   F   |   F   |   F   |   T   |
    +-------+-------+-------+-------+-------+-------+

The next sections verifies these 6 missing verifications.


.. _theory_contains_pinp:

Point in Point
--------------

Point is a 0-dimensional object, and contains only one element : the point itself.
Therefore, a point contains another point if, and only if the points are equal.

.. math::
    A \subset B \Leftrightarrow A = B


.. _theory_contains_pinc:

Point in Curve
--------------

To verify if a curve contains a point :math:`q`, we compute the projection of this point in the curve.

The projection is computed by finding :math:`t^{\star}` such minimizes the distance square:

.. math::
    D^2(t) = \|p(t) - q\|^2

It's a positive convex function and therefore there is at least one minimum of this function.
Its minimum can occurs at the nodes :math:`t_k` or when the derivative is zero:

.. math::
    \dfrac{d}{dt} D^2 = 0 \Leftrightarrow \langle p(t)-q, \ p'(t)\rangle = 0

This equation has at least one solution, but it may have infinite (take a circle as example).

Once the solutions are found, one can compute the distance between the point and the projected point.
If this projected point is equal to the point itself, then the point is on the curve.


.. _theory_contains_pins:

Point in Shape
--------------

The :ref:`winding_function` is used to determine if the shape contains the point.

Basically this function tells if a point is inside the shape, or outside, or at the boundary:

* If :math:`(x, \ y)` is at the interior, then :math:`w(x, \ y) = 1`
* If :math:`(x, \ y)` is at the exterior, then :math:`w(x, \ y) = 0`
* If :math:`(x, \ y)` is at the boundary,:math:`0 < w(x, \ y) < 1`

Hence, the verification happens as:

* If shape is simple:
    * If :math:`w = 0`, then shape doesn't contain the point
    * If :math:`w > 0` and shape is closed, then 
    * If :math:`w = 1`, then shape contains the point
    * If :math:`0 < w < 1`, then 

.. note::
    The possibility of using the ray-casting algorithm was considered, but it's
    Arguments against it are : depending on the direction of the ray, the result can vary.
    If it touches a vertex, etc.

    Also, having a mesure of how acute an angle is very useful. 


.. _theory_contains_cinc:

Curve in Curve
--------------

Check if a curve is inside another curve can be done by parts

* Check if the vertices of A's curve are inside the B's curve.
    That uses **Point in Curve**
* Check if the basis functions are the same.

.. _theory_contains_cins:

Curve in Shape
--------------

Checking if a curve is inside a shape is made by parts.

* If shape is disjoint: Check if the curve is inside any subshape
* If shape is connected: Check if the curve is inside all subshapes
* If shape is simple: 
    1. Checks if all vertices are inside the shape.
        The vertices are the curve evaluated at knots.
        This uses the **Point in Shape**.
    2. Find the intersection between the curve and the shape's curve.
        If they don't intersect, the curve is inside the shape.
        If they do intersect, continue
    3. Find the parameters where the two curves intersect.
        Compute the midpoints.
        For each midpoint, check if the midpoint is inside the shape.

.. _theory_contains_sins:

Shape in Shape
--------------

There are three shape classifications: **Simple**, **Connected** and **Disjoint**.
Checking `A in B` have 9 possibilities, which is reduced:

* If :math:`A` is disjoint, then
    .. math::
        \bigcup_i A_i \subset B \Leftrightarrow \text{all}_{i}\left(A_i \subset B\right)
* If :math:`A` is simple or connected, and :math:`B` is disjoint, then
    .. math::
        A \subset \bigcup_{i} B_i \Leftrightarrow \text{any}_{i}\left(A \subset B_i\right)
* If :math:`A` is simple or connected, and :math:`B` is connected, then
    .. math::
        A \subset \bigcap_{i} B_i \Leftrightarrow \text{all}_{i}\left(A \subset B_i\right)
* If :math:`A` is connected, and :math:`B` is simple, then
    .. math::
        \bigcap_i A_i \subset B \Leftrightarrow \text{all}_i\left(\text{jordan}\left(A_i\right) in B\right) \ \text{and}

For **Simple in Simple**, follows as bellow.


.. _theory_contains_simp:

Simple in simple
----------------

This part describes how to compare cases when :math:`A` and :math:`B` are simple shapes.
The following statements must be satisfied to :math:`A \subset B`.

1. A unbounded shape is not is not contained in a bounded shape

    Translated as: If `A.area < 0` and `B.area > 0`, then `A not in B`

2. The boundary of :math:`A` must be inside of :math:`B`

    Translated as: If the `A.jordan` is not inside `B`, then `A not in B`

3. The area from :math:`A` must not be greater than the area of :math:`B` 

    Translated as: If `A.area > B.area`, then `A not in B`

    * This consider the cases such, if `A.area > 0` and `B.area > 0`, then it's 

4. 



-------------------
Table simple shapes
-------------------

.. list-table:: List of geometric cases
    :widths: 20 20 20 20 20
    :header-rows: 1
    :align: center

    * - Case 1
      - Case 2
      - Case 3
      - Case 4
      - Case 5
    * - .. image:: ../img/contains/case-1.svg
            :width: 100%
      - .. image:: ../img/contains/case-2.svg
            :width: 100%
      - .. image:: ../img/contains/case-3.svg
            :width: 100%
      - .. image:: ../img/contains/case-4.svg
            :width: 100%
      - .. image:: ../img/contains/case-5.svg
            :width: 100%

.. table::
    :align: center

    +-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
    |        Case       | :math:`A`  | :math:`B` | :math:`A` in :math:`B` | :math:`J_A` in :math:`B` | :math:`J_B` in :math:`A` | :math:`a_A ? a_B` |
    +===================+============+===========+========================+==========================+==========================+===================+
    |                   |            | :math:`+` | .. centered:: F        | .. centered:: F          |                          | .. centered:: ?   |
    |                   | :math:`+`  +-----------+------------------------+--------------------------+ .. centered:: F          +-------------------+
    |                   |            | :math:`-` | .. centered:: T        | .. centered:: T          |                          | .. centered:: >   |
    | .. centered::  1  +------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
    |                   |            | :math:`+` |                        | .. centered:: F          |                          | .. centered:: <   |
    |                   | :math:`-`  +-----------+ .. centered:: F        +--------------------------+ .. centered:: T          +-------------------+
    |                   |            | :math:`-` |                        | .. centered:: T          |                          | .. centered:: ?   |
    +-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
    |                   |            | :math:`+` | .. centered:: T        | .. centered:: T          |                          | .. centered:: <   |
    |                   | :math:`+`  +-----------+------------------------+--------------------------+ .. centered:: F          +-------------------+
    |                   |            | :math:`-` |                        | .. centered:: F          |                          | .. centered:: >   |
    | .. centered::  2  +------------+-----------+                        +--------------------------+--------------------------+-------------------+
    |                   |            | :math:`+` | .. centered:: F        | .. centered:: T          |                          | .. centered:: <   |
    |                   | :math:`-`  +-----------+                        +--------------------------+ .. centered:: T          +-------------------+
    |                   |            | :math:`-` |                        | .. centered:: F          |                          | .. centered:: >   |
    +-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
    |                   |            | :math:`+` |                        | .. centered:: F          |                          |                   |
    |                   | :math:`+`  +-----------+                        +--------------------------+ .. centered:: T          | .. centered:: <   |
    |                   |            | :math:`-` | .. centered:: F        | .. centered:: T          |                          |                   |
    | .. centered::  3  +------------+-----------+                        +--------------------------+--------------------------+-------------------+
    |                   |            | :math:`+` |                        | .. centered:: F          |                          |                   |
    |                   | :math:`-`  +-----------+------------------------+--------------------------+ .. centered:: F          | .. centered:: >   |
    |                   |            | :math:`-` | .. centered:: T        | .. centered:: T          |                          |                   |
    +-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
    |                   |            | :math:`+` | .. centered:: T        |                          |                          | .. centered:: =   |
    |                   | :math:`+`  +-----------+------------------------+                          |                          +-------------------+
    |                   |            | :math:`-` |                        |                          |                          | .. centered:: >   |
    | .. centered::  4  +------------+-----------+ .. centered:: F        | .. centered:: T          | .. centered:: T          +-------------------+
    |                   |            | :math:`+` |                        |                          |                          | .. centered:: <   |
    |                   | :math:`-`  +-----------+------------------------+                          |                          +-------------------+
    |                   |            | :math:`-` | .. centered:: T        |                          |                          | .. centered:: =   |
    +-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
    |                   |            | :math:`+` |                        |                          |                          | .. centered:: ?   |
    |                   | :math:`+`  +-----------+                        |                          |                          +-------------------+
    |                   |            | :math:`-` |                        |                          |                          | .. centered:: <   |
    | .. centered::  5  +------------+-----------+ .. centered:: F        | .. centered:: F          | .. centered:: F          +-------------------+
    |                   |            | :math:`+` |                        |                          |                          | .. centered:: >   |
    |                   | :math:`-`  +-----------+                        |                          |                          +-------------------+
    |                   |            | :math:`-` |                        |                          |                          | .. centered:: ?   |
    +-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+




This table is translated to an algorithm.
Unfortunatelly we don't know which case the simples shapes are,
so we will test by using some caracteristics.

For example, the first good information from the table is given by: 


+-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
|        Case       | :math:`A`  | :math:`B` | :math:`A` in :math:`B` | :math:`J_A` in :math:`B` | :math:`J_B` in :math:`A` | :math:`a_A ? a_B` |
+===================+============+===========+========================+==========================+==========================+===================+
| .. centered::  1  | :math:`-`  | :math:`+` | .. centered:: F        |  .. centered:: F         |   .. centered:: T        | .. centered:: <   |
+-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
| .. centered::  2  | :math:`-`  | :math:`+` | .. centered:: F        |  .. centered:: T         |   .. centered:: T        | .. centered:: <   |
+-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
| .. centered::  3  | :math:`-`  | :math:`+` | .. centered:: F        |  .. centered:: F         |   .. centered:: F        | .. centered:: <   |
+-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
| .. centered::  4  | :math:`-`  | :math:`+` | .. centered:: F        |  .. centered:: T         |   .. centered:: T        | .. centered:: <   |
+-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
| .. centered::  5  | :math:`-`  | :math:`+` | .. centered:: F        |  .. centered:: F         |   .. centered:: F        | .. centered:: <   |
+-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+



.. code-block:: python

    # ...
    shapea = SimpleShape(jordana)
    shapeb = SimpleShape(jordanb) 
    # Decide if shapea in shapeb
    if float(shapea) < 0 and float(shapeb) > 0:
        # For any presented cases it happens
        return False
    # continue ...


+-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
|        Case       | :math:`A`  | :math:`B` | :math:`A` in :math:`B` | :math:`J_A` in :math:`B` | :math:`J_B` in :math:`A` | :math:`a_A ? a_B` |
+===================+============+===========+========================+==========================+==========================+===================+
| .. centered::  1  | :math:`+`  | :math:`-` | .. centered:: T        |  .. centered:: T         |   .. centered:: F        | .. centered:: >   |
+-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
| .. centered::  2  | :math:`+`  | :math:`-` | .. centered:: F        |  .. centered:: F         |   .. centered:: F        | .. centered:: >   |
+-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
| .. centered::  3  | :math:`+`  | :math:`-` | .. centered:: F        |  .. centered:: T         |   .. centered:: T        | .. centered:: >   |
+-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
| .. centered::  4  | :math:`+`  | :math:`-` | .. centered:: F        |  .. centered:: T         |   .. centered:: T        | .. centered:: >   |
+-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+
| .. centered::  5  | :math:`+`  | :math:`-` | .. centered:: F        |  .. centered:: F         |   .. centered:: F        | .. centered:: >   |
+-------------------+------------+-----------+------------------------+--------------------------+--------------------------+-------------------+




.. code-block:: python

    # ... continue
    if float(shapea) > 0 and float(shapeb) < 0:
        # Only for case 1
        return (jordana in shapeb) and (jordanb not in shapea)
    # continue ...

Taking out the already extracted values, and separating by when ``areaA > areaB``:



+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
|        Case       | :math:`A`  | :math:`B` | :math:`A` in :math:`B` | :math:`J_A` in :math:`B` | :math:`a_A ? a_B` |
+===================+============+===========+========================+==========================+===================+
|                   | :math:`+`  | :math:`+` |                        |  .. centered:: F         |                   |
| .. centered::  1  +------------+-----------+ .. centered:: F        +--------------------------+ .. centered:: >   |
|                   | :math:`-`  | :math:`-` |                        |  .. centered:: T         |                   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
| .. centered::  2  | :math:`-`  | :math:`-` | .. centered:: F        |  .. centered:: F         | .. centered:: >   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
| .. centered::  3  | :math:`+`  | :math:`+` | .. centered:: F        |  .. centered:: F         | .. centered:: >   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
|                   | :math:`+`  | :math:`+` |                        |                          |                   |
| .. centered::  5  +------------+-----------+ .. centered:: F        |  .. centered:: F         | .. centered:: >   |
|                   | :math:`-`  | :math:`-` |                        |                          |                   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+



+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
|        Case       | :math:`A`  | :math:`B` | :math:`A` in :math:`B` | :math:`J_A` in :math:`B` | :math:`a_A ? a_B` |
+===================+============+===========+========================+==========================+===================+
|                   | :math:`+`  | :math:`+` |                        |  .. centered:: F         |                   |
| .. centered::  1  +------------+-----------+ .. centered:: F        +--------------------------+ .. centered:: <=  |
|                   | :math:`-`  | :math:`-` |                        |  .. centered:: T         |                   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
| .. centered::  2  | :math:`+`  | :math:`+` | .. centered:: T        |  .. centered:: T         | .. centered:: <   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
| .. centered::  3  | :math:`-`  | :math:`-` | .. centered:: T        |  .. centered:: T         | .. centered:: <   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
|                   | :math:`+`  | :math:`+` |                        |                          |                   |
| .. centered::  4  +------------+-----------+ .. centered:: T        |  .. centered:: T         | .. centered:: =   |
|                   | :math:`-`  | :math:`-` |                        |                          |                   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
|                   | :math:`+`  | :math:`+` |                        |                          |                   |
| .. centered::  5  +------------+-----------+ .. centered:: F        |  .. centered:: F         | .. centered:: <=  |
|                   | :math:`-`  | :math:`-` |                        |                          |                   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+

.. code-block:: python

    # ... continue
    if float(shapea) > float(shapeb):
        return False
    # continue ...


We see that when :math:`J_A \ \text{in} \ B` gives :math:`F`, the :math:`A \ \text{in} \ B` is also :math:`F`

.. code-block:: python

    # ... continue
    if jordana not in shapeb:
        return False
    # continue ...

Rewriting the table we get


+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
|        Case       | :math:`A`  | :math:`B` | :math:`A` in :math:`B` | :math:`J_A` in :math:`B` | :math:`a_A ? a_B` |
+===================+============+===========+========================+==========================+===================+
| .. centered::  1  | :math:`-`  | :math:`-` | .. centered:: F        |  .. centered:: T         | .. centered:: <=  |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
| .. centered::  2  | :math:`+`  | :math:`+` | .. centered:: T        |  .. centered:: T         | .. centered:: <   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
| .. centered::  3  | :math:`-`  | :math:`-` | .. centered:: T        |  .. centered:: T         | .. centered:: <   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
|                   | :math:`+`  | :math:`+` |                        |                          |                   |
| .. centered::  4  +------------+-----------+ .. centered:: T        |  .. centered:: T         | .. centered:: =   |
|                   | :math:`-`  | :math:`-` |                        |                          |                   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+

Taking out when ``areaA > 0`` we get

+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
|        Case       | :math:`A`  | :math:`B` | :math:`A` in :math:`B` | :math:`J_A` in :math:`B` | :math:`a_A ? a_B` |
+===================+============+===========+========================+==========================+===================+
| .. centered::  1  | :math:`-`  | :math:`-` | .. centered:: F        |  .. centered:: T         | .. centered:: <=  |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
| .. centered::  3  | :math:`-`  | :math:`-` | .. centered:: T        |  .. centered:: T         | .. centered:: <   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+
| .. centered::  4  | :math:`-`  | :math:`-` | .. centered:: T        |  .. centered:: T         | .. centered:: =   |
+-------------------+------------+-----------+------------------------+--------------------------+-------------------+

.. _theory_boolean:

==================
Boolean operations
==================

The boolean operations are the main objective of this package.
The following operations are available:

.. list-table:: 
    :widths: 30 20 20 20
    :header-rows: 1
    :align: center

    * - Name
      - Logic
      - Math
      - Python
    * - Inversion
      - NOT
      - :math:`\overline{A}`
      - `~A`
    * - Union
      - OR
      - :math:`A \cup B`
      - `A | B`
    * - Intersection
      - AND
      - :math:`A \cap B`
      - `A & B`
    * - Subtraction
      - SUB
      - :math:`A - B`
      - `A - B`
    * - Exclusive or
      - XOR
      - :math:`A \otimes B`
      - `A ^ B`

From these operations above, only three of them are basic: **NOT**, **OR** and **AND**.

The others are decomposed as follows:

* SUB: `A - B = A & (~B)`
* XOR: `A ^ B = (A - B) | (B - A)`

To recall, De Morgan's law

* `~(A & B) = (~A) | (~B)`
* `~(A | B) = (~A) & (~B)`

.. math::
    \overline{A \cap B} = \overline{A} \cup \overline{B}
.. math::
    \overline{A \cup B} = \overline{A} \cap \overline{B}


A general table with all the operations

.. image:: ../img/primitive/all_bool_operations.svg
   :width: 100 %
   :alt: Operations between two positives simple shapes
   :align: center

.. _theory_bool_single:

True and False entities
-----------------------

For this package, to represent the quantities :

* **EmptyShape**: False, void set
* **WholeShape**: True, whole plane

.. _theory_bool_not:


Inversion / logic NOT
---------------------

.. _theory_bool_or:

Union / logic OR
----------------

The union between two python boolean objects

.. code-block:: python

   from shapepy import Primitive
   # Create two simple shapes
   circle = Primitive.circle()
   square = Primitive.square()
   # Union
   newshape = circle | square

.. figure:: ../img/primitive/setAorB.svg
   :width: 40%
   :alt: Schema of adding sets :math:`A` and :math:`B`
   :align: center

.. figure:: ../img/primitive/or_table.svg
   :width: 80%
   :alt: Table of union between two positive circles
   :align: center


.. _theory_bool_and:

Intersection / logic AND
------------------------

The intersection between two python boolean objects

.. code-block:: python

   # Create two positive shapes
   circle = section.shape.primitive.circle()
   square = section.shape.primitive.square()
   # Intersection
   newshape = circle & square

.. figure:: ../img/primitive/setAandB.svg
   :width: 40%
   :alt: Example of multiplication between two positive shapes
   :align: center


.. figure:: ../img/primitive/and_table.svg
   :width: 80%
   :alt: Table of intersection between two positive circles
   :align: center


.. _theory_bool_sub:

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


.. _theory_bool_xor:

Exclusive union / logic XOR
---------------------------

The xor between two shapes. For this operator, we use the symbol ``^``.

.. code-block:: python

   # Create two positive shapes
   circle = section.shape.primitive.circle()
   square = section.shape.primitive.square()
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





-----------------------------------------------------------------

.. _theory_generalities:

============
Generalities
============


.. _onedimen_integration:

One-dimensional integration
---------------------------

In the :ref:`integral` section, the computation of the integral is needed:

.. math::
    I = \int_{a}^{b} f(t) \ dt

When analitic integration is not used, then numerical integration takes place

.. math::
    \tilde{I} = (b-a) \cdot \sum_{j=0}^{m-1} w_{j} \cdot f(t_j)

The values of :math:`t_j` and :math:`w_j` are the nodes and weights of the quadrature schema.
There are available schemas are bellow, with some nodes/weights depending on :math:`m`

1. Closed Newton-Cotes
2. Open Newton-Cotes
3. Chebyshev
4. Gauss-Legendre

.. dropdown:: Closed Newton Cotes Quadrature 

    .. list-table:: 
        :widths: 20 40 40
        :header-rows: 1
        :align: center

        * - :math:`n`
          - :math:`x_i`
          - :math:`w_i`
        * - 2
          - 0
          - 1/2
        * - 
          - 1
          - 1/2
        * - 
          - 
          - 
        * - 3
          - 0
          - 1/6
        * - 
          - 0.5
          - 4/6
        * - 
          - 1
          - 1/6

.. dropdown:: Open Newton cotes Quadrature 

    .. list-table:: 
        :widths: 20 40 40
        :header-rows: 1
        :align: center

        * - :math:`n`
          - :math:`x_i`
          - :math:`w_i`
        * - 1
          - 1/2
          - 1
        * - 
          - 
          - 
        * - 2
          - 0
          - 1/2
        * - 
          - 1
          - 1/2
        * - 
          - 
          - 
        * - 3
          - 1/4
          - 2/3
        * - 
          - 2/4
          - -1/3
        * - 
          - 3/4
          - 2/3

.. dropdown:: Gaussian Quadrature 

    .. list-table:: 
        :widths: 20 40 40
        :header-rows: 1
        :align: center

        * - :math:`n`
          - :math:`x_i`
          - :math:`w_i`
        * - 1
          - 1/2
          - 1

.. dropdown:: Chebyshev Quadrature 

    .. list-table:: 
        :widths: 20 40 40
        :header-rows: 1
        :align: center

        * - :math:`n`
          - :math:`x_i`
          - :math:`w_i`
        * - 1
          - 1/2
          - 1

.. _winding_function:

Winding function
----------------

The **Winding function** is a function on the plane, based on the a shape :math:`S`, that

* Is equal to :math:`1` for interior points
* Is equal to :math:`0` for exterior points
* Is between :math:`0` and :math:`1` at the boundary

At the boundary, this function measures how much 'convex' the boundary is.

* For smooth boundaries, like a straight line or the edges of a polygon, it is equal to :math:`0.5`.
* At the corners of a square, it's equal to :math:`0.25`, cause only 25% of the neighborhood is inside the square.

The formal definition is given by 

.. math::
    w_{S}(x, y) = \lim_{\varepsilon \to 0^{+}} \dfrac{\text{area}\left(S \cap D\left(x, y, \ \varepsilon\right)\right)}{\pi \varepsilon^2}

If :math:`(x, \ y)` lies on the boundary,
that means there's a :math:`t^{\star}` for a curve :math:`p`,
and therefore

.. math::
    w_{S}(x, \ y) = \dfrac{1}{2\pi} \arg\left(\langle v_0, \ v_1\rangle + i \cdot v_0 \times v_1\right)
.. math::
    v_0 = -\lim_{\delta \to 0^{+}} p'(t^{\star}-\delta)
.. math::
    v_1 = \lim_{\delta \to 0^{+}} p'(t^{\star}+\delta)

For smooth boundaries, :math:`p'` is continuous at :math:`t^{\star}`.
Meaning :math:`v_0 + v_1 = 0` and then :math:`w_{S}(x, \ y) = 0.5`
