#!/usr/bin/env python

import os
os.environ['HOME'] = '/tmp/'
import matplotlib
matplotlib.use('Agg')
from pylab import contour, savefig
import numpy
import cPickle
import ogr
import sys
import tempfile

def rotate(arr, theta):
    R = numpy.array([[numpy.cos(theta),  numpy.sin(theta)]
                ,[-numpy.sin(theta), numpy.cos(theta)]])
    return numpy.dot(arr, R)

def numpy_to_arrow_shape(x, y, z, shpname=None, epsg=None, group='', levels=None, mask_wkt='', **kwargs):
    """ turn a numpy grid into a shape file which can be plotted as a
    quiver plot. same arguments as numpy_to_shape. """

    GROUP_NAME = 'group'   # the name for different groups of contours.
    MAX_PTS = 1000          # the maximum number of arrows to plot.

    gx, gy = numpy.gradient(z)
    angle = -90 + numpy.arctan2(gx, -gy)*180/(-numpy.pi)
    speed = numpy.sqrt(gx**2 + gy**2)

    if z.shape[0] * z.shape[1] > MAX_PTS:
        step = (z.shape[0] * z.shape[1]/ MAX_PTS)/2
        idxs = numpy.arange(0,z.shape[0] * z.shape[1], step)
        x = x.ravel().take(idxs)
        y = y.ravel().take(idxs)
        z = z.ravel().take(idxs)
        speed = speed.ravel().take(idxs)
        angle = angle.ravel().take(idxs)
    if speed.mean() > 10:
        speed = speed / speed.mean() * 3
    speed += 10


    if mask_wkt:
        mask_wkt = ogr.CreateGeometryFromWkt(mask_wkt)

    if not shpname:
        # could have problems because not using mkstemp...
        shpname = tempfile.mktemp(dir='/var/www/ms_tmp', prefix='quiver_', suffix='.shp')
    
    shp = ogr.GetDriverByName('ESRI Shapefile')

    # ogr setup, create that datasource, layer, fields for the .shp 
    if os.path.exists(shpname):
        data_source = shp.Open(shpname,update=1)
        layer = data_source.GetLayerByIndex(0)
    else: 
        data_source = shp.CreateDataSource(shpname)
        layer = data_source.CreateLayer('', geom_type=ogr.wkbPoint)

        field = ogr.FieldDefn('angle', ogr.OFTReal)
        field.SetWidth(6)
        field.SetPrecision(2)
        layer.CreateField(field)

        field = ogr.FieldDefn('speed', ogr.OFTReal)
        field.SetWidth(6)
        field.SetPrecision(2)
        layer.CreateField(field)

        group_field = ogr.FieldDefn(GROUP_NAME, ogr.OFTString)
        group_field.SetWidth(12)
        layer.CreateField(group_field)

    pt_str = "POINT(%f %f)"
    for xp, yp, ap, sp in zip(x.ravel(), y.ravel(), angle.ravel(), speed.ravel()):

        geom = ogr.CreateGeometryFromWkt(pt_str % (xp, yp))
        if mask_wkt:
            if not mask_wkt.Contains(geom): continue
        f = ogr.Feature(feature_def=layer.GetLayerDefn())
        f.SetGeometryDirectly(geom)
        f.SetField('angle', ap) 
        f.SetField('speed', sp)
        f.SetField(GROUP_NAME, group)
        layer.CreateFeature(f)
        f.Destroy()

    data_source.Destroy()

    return shpname


    

def numpy_to_shape(x, y, z, shpname=None, x0=0, y0=0, theta=None, connect=False, epsg=None, group='', levels=None, mask_wkt='', **kwargs):
    """turn a numpy grid array into a shapefile. 
    x, y, z are grids (likely from meshgrid (x, y) and interpolation (z)
    of the original data. 
    shpname: the name of a shapefile to add data to. if none, a new
    temporary file is created.
    connect: if true, then make into a ring by setting ring[-1] = ring[0]
    theta: rotate the array by this degree.
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
        shpname = tempfile.mktemp(dir='/var/www/ms_tmp', prefix='contour_', suffix='.shp')

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
        field.SetWidth(9)
        field.SetPrecision(2)
        layer.CreateField(field)

        group_field = ogr.FieldDefn(GROUP_NAME, ogr.OFTString)
        group_field.SetWidth(12)
        layer.CreateField(group_field)


    # iterate through the contours created by pylab.contour and 
    # create wkt to add to a shapefile. 
    line_str = 'LINESTRING(%s)'
    center = [0,0]
    for i, c in enumerate(cont.collections):


        # using c.get_verts() doesnt separate distinct shapes at the
        # same contour level. so access the segements directly.
        for seg in c._segments:
            if theta is not None: seg = rotate(seg, theta)
            # make it into a ring
            if not i:
                center = numpy.mean(seg,axis=0)
                center[0] += x0
                center[1] += y0

            if connect: seg = list(seg); seg.append(seg[0]); 

            f = ogr.Feature(feature_def=layer.GetLayerDefn())
            pts = ",".join(["%f %f" % (x + x0, y + y0) for k,(x,y) in enumerate(seg)])
            geom = ogr.CreateGeometryFromWkt(line_str % pts)
            if mask_wkt:
                geom = geom.Intersection(mask_wkt)
            f.SetField(FIELD_NAME, cont.levels[i])
            f.SetField(GROUP_NAME, group or str(i) )

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

    return shpname, center


if __name__ == "__main__":
    fh = open('/tmp/zz.pickle','rb')
    x = cPickle.load(fh)
    y = cPickle.load(fh)
    z = cPickle.load(fh)
    print x.min(), x.max()
    print y.min(), y.max()
    print z.min(), z.max()

    shpname = numpy_to_shape(x, y, z, levels=None,group="WILMA")
    assert shpname == numpy_to_shape(x, y, z, shpname=shpname, levels=None,group="FRED")
    print shpname
