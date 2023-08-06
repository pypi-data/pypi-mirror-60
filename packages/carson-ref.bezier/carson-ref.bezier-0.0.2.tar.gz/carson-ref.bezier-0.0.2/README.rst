============================
Bezier curve simulation
============================

:Source Code: https://github.com/CarsonSlovoka/carson-ref.bezier/blob/master/Carson/Ref/Bezier/bezier.py
:Compatible: Python >3.6
:Platform: Windows
:License: `Apache 2.0`_
:Author Doc: https://carsonslovoka.github.io/CarsonDoc/

.. sectnum::

Bezier curve simulation (including reductions the dimension from 3 to 2)

.. image:: demo/demo.gif

Install
===============

* ``pip install carson-ref.bezier``

USAGE
===============

.. code-block:: python

    from Carson.Ref.Bezier import bezier_curve_monitor
    bezier_curve_monitor()

.. csv-table:: Event
    :header: KEY, Desc.
    :delim: |

    ESC| exit app
    C| redraw (clear canvas)
    LButton| set point


.. _`Apache 2.0`: https://github.com/CarsonSlovoka/carson-ref.bezier/blob/master/LICENSE