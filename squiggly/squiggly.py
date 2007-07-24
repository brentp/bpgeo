"""    
=== Squiggly ===
shapely + sqlite 

>>> import squiggly
>>> conn = squiggly.connect(':memory:')
>>> cur = conn.cursor()

# create a table that looks like one the OGR sqlite driver would create
>>> cur.execute("CREATE TABLE test(OGC_FID INTEGER, WKT_GEOMETRY LineString, some_attribute INTEGER)") #doctest: +ELLIPSIS
<...Cursor object ...>

>>> import numpy as n
>>> pts = n.arange(20).reshape(10,2).astype(n.float)
>>> l = LineString(pts)
>>> print l #doctest: +ELLIPSIS
LINESTRING (0.0000000000000000 1.0000000000000000, 2.0000000000000000 3.0000000000000000, 4.0000000000000000 5.0000000000000000, ... 18.0000000000000000 19.0000000000000000)

>>> cur.execute("INSERT INTO test(WKT_GEOMETRY, some_attribute) VALUES (?,?)", (l,22)) #doctest: +ELLIPSIS
<...Cursor object ...>

>>> row = cur.execute("SELECT WKT_GEOMETRY as '[WKT]', some_attribute FROM test").fetchone() # doctest: +ELLIPSIS
>>> row[0].wkt == l.wkt
True
>>> row[1] == 22
True


>>> result = cur.execute("SELECT BOUNDARY(WKT_GEOMETRY) as '[WKT]' from test").fetchone()[0]
>>> print result.wkt
POLYGON ((0.0000000000000000 1.0000000000000000, 18.0000000000000000 1.0000000000000000, 18.0000000000000000 19.0000000000000000, 0.0000000000000000 19.0000000000000000, 0.0000000000000000 1.0000000000000000))

>>> buffered = cur.execute("SELECT BUFFER('POINT(5 5)', 10) as '[WKT]' from test").fetchone()[0] 
>>> buffered # doctest: +ELLIPSIS
<shapely.geometry.polygon.Polygon object ...>

>>> cur.execute("SELECT CONTAINS(?, 'POINT(5 5)')", (buffered,)).fetchone()[0]
1

>>> cur.execute("SELECT IS_RING(?)", (buffered,)).fetchone()[0]
0


>>> g = cur.execute("SELECT geom_union('POINT(1 1)','POINT(2 2)') as '[WKT]'").fetchone()[0]
>>> print g.wkt
MULTIPOINT (1.0000000000000000 1.0000000000000000, 2.0000000000000000 2.0000000000000000)

>>> cur.execute("SELECT distance('POINT(1 1)','POINT(2 2)')").fetchone()[0] #doctest: +ELLIPSIS
1.414...

>>> cur.execute("SELECT equals('POINT(5 5)','POINT(5 5)')").fetchone()[0]
1

>>> cur.execute("SELECT GEOM_AREA(BUFFER('POINT(5 5)',10))").fetchone()[0] #doctest: +ELLIPSIS
62.806...

"""


try:
    import sqlite3
except:
    from pysqlite2 import dbapi2 as sqlite3

from shapely.geometry import *
from shapely.geometry.base import BaseGeometry
from shapely import wkt
import shapely.iterops

sqlite3.register_adapter(LineString, wkt.dumps)
sqlite3.register_adapter(Point, wkt.dumps)
sqlite3.register_adapter(Polygon, wkt.dumps)
sqlite3.register_adapter(MultiPoint, wkt.dumps)
sqlite3.register_adapter(MultiLineString, wkt.dumps)
sqlite3.register_adapter(GeometryCollection, wkt.dumps)

# now use one convertor for all those shapes [WKT]
sqlite3.register_converter('WKT', wkt.loads)

def connect(dsn, *args, **kwargs):
    """ takes an sqlite connection and registers the aggregate
    functions described by geos so that they can be used via sql.

    """
    kwargs['detect_types'] = sqlite3.PARSE_COLNAMES
    conn = sqlite3.connect(dsn, *args, **kwargs)

    unaries      = ('boundary', 'centroid', 'convex_hull', 'envelope')
    unary_floats = ('area', 'length')
    bools        = ('is_empty', 'is_valid', 'is_ring', 'has_z')

    bins         = ('difference', 'relate', 'symmetric_difference') 
    bin_floats    = ('distance',)
    bin_preds    = ('disjoint', 'within', 'contains', 'overlaps', 'equals')

    # takes a(n) argument(s)
    params = ('buffer',)

    for u in unaries :
        conn.create_function(u, 1 , lambda shp: str(wkt.loads(shp).__getattribute__(u)))

    # these dont seem to work...
    for uf in unary_floats :
        conn.create_function('geom_' + uf, 1 , lambda shp: wkt.loads(shp).__getattribute__(uf))
    
    # return int
    for b in bools :
        conn.create_function(b, 1 , lambda shp: int(wkt.loads(shp).__getattribute__(b)))
    
    for p in params:
        conn.create_function(p, 2, lambda shp, d: str(wkt.loads(shp).__getattribute__(p)(d)))

    # variable number of args... 
    def union(*args):
        a = wkt.loads(args[0])
        for shp in args[1:]:
            a = a.union(wkt.loads(shp))
        return str(a)
    conn.create_function('geom_union', -1, union)

    # more complicated than it's worth...
    def closure(func, returntype):
        def f(a, b):
            a = wkt.loads(a)
            b = wkt.loads(b)
            return returntype(a.__getattribute__(func)(b))
        return f

    for bin in bins:
        f = closure(bin, str) 
        conn.create_function(bin, 2, f)

    # return 1 or 0
    for bp in bin_preds:
        f = closure(bp, int) 
        conn.create_function(bp, 2, f)

    for bp in bin_floats:
        f = closure(bp, float) 
        conn.create_function(bp, 2, f)

    return conn

if __name__ == "__main__":
    import doctest
    doctest.testmod()
