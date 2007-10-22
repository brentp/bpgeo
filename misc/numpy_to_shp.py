#!/usr/bin/env python

from pylab import contour, show
import cPickle
import ogr
import os
import tempfile

def numpy_to_shape(x, y, z, shpname=None, epsg=26910, group='', levels=None):
    """turn a numpy grid array into a shapefile. 
    x, y, z are grids (likely from meshgrid (x, y) and interpolation (z)
    of the original data. 
    shpname: the name of a shapefile to add data to. if none, a new
    temporary file is created.
    epsg: the projection.
    group: to add a new group (likely a new shpname merits a group indication
    levels: same as for pylab.contour 
    """
    FIELD_NAME = 'contour' # the field name for the z contour level.
    GROUP_NAME = 'group'   # the name for different groups of contours.
    
    if not shpname:
        # could have problems because not using mkstemp...
        shpname = tempfile.mktemp(dir='/tmp/shps', suffix='.shp')

    # pylab.contour does the work of figuring out the contours.
    cont = contour(x, y, z, levels=levels, colors='k')
    shp = ogr.GetDriverByName('ESRI Shapefile')


    # ogr setup, create that datasource, layer, fields for the .shp 
    if os.path.exists(shpname):
        data_source = shp.Open(shpname,update=1)
        layer = data_source.GetLayerByIndex(0)
    else: 
        data_source = shp.CreateDataSource(shpname)
        layer = data_source.CreateLayer('', geom_type=ogr.wkbLineString)

        field = ogr.FieldDefn(FIELD_NAME, ogr.OFTReal)
        field.SetPrecision(2)
        layer.CreateField(field)
        if group:
            group_field = ogr.FieldDefn(GROUP_NAME, ogr.OFTString)
            layer.CreateField(group_field)


    # iterate through the contours created by pylab.contour and 
    # create wkt to add to a shapefile. 
    line_str = 'LINESTRING(%s)'
    for i,c in enumerate(cont.collections):
        f = ogr.Feature(feature_def=layer.GetLayerDefn())

        pts = ",".join(["%f %f" % (x, y) for x,y in c.get_verts()])
        geom = ogr.CreateGeometryFromWkt(line_str % pts)

        f.SetField(FIELD_NAME, cont.levels[i])
        if group:
            f.SetField(GROUP_NAME, group)

        f.SetGeometryDirectly(geom)
        layer.CreateFeature(f)
        f.Destroy()
    data_source.Destroy()

    # write the projection file. as ogr wont do it for us.
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
