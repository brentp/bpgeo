#!/usr/bin/env python

import os
os.environ['HOME'] = '/tmp/'
import matplotlib
matplotlib.use('Agg')
from pylab import contour, savefig
import cPickle
import ogr
import tempfile

def numpy_to_shape(x, y, z, shpname=None, epsg=None, group='', levels=None, mask_wkt=''):
    """turn a numpy grid array into a shapefile. 
    x, y, z are grids (likely from meshgrid (x, y) and interpolation (z)
    of the original data. 
    shpname: the name of a shapefile to add data to. if none, a new
    temporary file is created.
    epsg: the projection.
    group: to add a new group (likely a new shpname merits a group indication
    levels: same as for pylab.contour 
    mask_wkt: e.g. the watershed to clip on. stops contours from appearing outside the watershed.
    """

    FIELD_NAME = 'contour' # the field name for the z contour level.
    GROUP_NAME = 'group'   # the name for different groups of contours.
    
    if mask_wkt:
        mask_wkt = ogr.CreateGeometryFromWkt(mask_wkt)

    if not shpname:
        # could have problems because not using mkstemp...
        shpname = tempfile.mktemp(dir='/var/www/ms_tmp', suffix='.shp')

    # pylab.contour does the work of figuring out the contours.
    cont = contour(x, y, z, levels=levels, colors='k', origin='lower')
    shp = ogr.GetDriverByName('ESRI Shapefile')
    # see also mapscript: mapscript.shapeObj.fromWKT('POINT(2 2)')

    # ogr setup, create that datasource, layer, fields for the .shp 
    if os.path.exists(shpname):
        data_source = shp.Open(shpname,update=1)
        layer = data_source.GetLayerByIndex(0)
    else: 
        data_source = shp.CreateDataSource(shpname)
        layer = data_source.CreateLayer('', geom_type=ogr.wkbLineString)

        field = ogr.FieldDefn(FIELD_NAME, ogr.OFTReal)
        field.SetWidth(4)
        field.SetPrecision(2)
        layer.CreateField(field)

        group_field = ogr.FieldDefn(GROUP_NAME, ogr.OFTString)
        group_field.SetWidth(12)
        layer.CreateField(group_field)


    # iterate through the contours created by pylab.contour and 
    # create wkt to add to a shapefile. 
    line_str = 'LINESTRING(%s)'
    for i,c in enumerate(cont.collections):
        # using c.get_verts() doesnt separate distinct shapes at the
        # same contour level. so access the segements directly.
        for seg in c._segments:
            f = ogr.Feature(feature_def=layer.GetLayerDefn())
            pts = ",".join(["%f %f" % (x, y) for k,(x,y) in enumerate(seg) if k % 2])
            geom = ogr.CreateGeometryFromWkt(line_str % pts)
            if mask_wkt:
                geom = geom.Intersection(mask_wkt)

            f.SetField(FIELD_NAME, cont.levels[i])
            f.SetField(GROUP_NAME, group)

            f.SetGeometryDirectly(geom)
            layer.CreateFeature(f)
            f.Destroy()
    data_source.Destroy()

    # write the projection file. as ogr wont do it for us.
    if epsg:
        proj = ogr.osr.SpatialReference()
        proj.ImportFromEPSG(epsg)
        proj_file = open(shpname[:-4] + ".prj", 'w')
        proj_file.write(proj.ExportToWkt())
        proj_file.close()

    return shpname


if __name__ == "__main__":
    fh = open('z.pickle','rb')
    x = cPickle.load(fh)
    y = cPickle.load(fh)
    z = cPickle.load(fh)
    print x.min(), x.max()
    print y.min(), y.max()
    print z.min(), z.max()

    shpname = numpy_to_shape(x, y, z, levels=None,group="WILMA")
    assert shpname == numpy_to_shape(x, y, z, shpname=shpname, levels=None,group="FRED")
    print shpname
