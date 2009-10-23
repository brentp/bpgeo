Some Title Here
===============


A Slide - Cool
--------------

Intro or something.


Example Code (python)
---------------------

.. sourcecode:: python

    >>> from rtree import Rtree
    >>> r = Rtree() # in memory
    >>> for i in range(1000):
    ...    r.add(i, (i, i, i + 2, i + 2))

    >>> r.intersection((0, 1, 0, 1))


Example Code (bash) 
-------------------
 
.. sourcecode:: bash

    NAME=index
    python rst-directive.py \
        --stylesheet=pygments.css \
        --theme-url=ui/small-black \
        ${NAME}.rst > ${NAME}.html

.. footer:: 2009/11/05

