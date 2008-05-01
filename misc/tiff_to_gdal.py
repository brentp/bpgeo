

from tempfile import NamedTemporaryFile
from osgeo import gdal, gdal_array
from osgeo.gdalconst import GDT_Float64

def array_to_tiff(arr, bbox, fn=None):
    d = gdal.GetDriverByName("GTiff")
    if fn is None:
        fn = NamedTemporaryFile(suffix=".tiff",dir="/var/www/ms_tmp/")
        fn.close()
        fn = fn.name
    dst = d.Create(fn, arr.shape[0], arr.shape[1], 1, gdal.GDT_Float32)
    dst.SetGeoTransform([bbox[0]
                   ,(bbox[2] - bbox[0])/z.shape[0]
                   , 0 
                   , bbox[1]
                   , 0
                   ,(bbox[3] - bbox[1])/z.shape[1]
                ])
    
    gdal_array.BandWriteArray(dst.GetRasterBand(1),z)
    return fn


def arr_to_tiff(a, fn, xmin, ymin, xmax, ymax):
    """ a: numpy array
        fn: a file name to write the tiff
        xmin, ymin, xmax, ymax: the geographical extents of the array
    """
    driver = gdal.GetDriverByName('GTiff')
    out = driver.Create(fn, a.shape[0], a.shape[1], 1, GDT_Float64)

    out.SetGeoTransform([xmin
                    , (xmax - xmin)/a.shape[0]
                    , 0
                    , ymin
                    , 0
                    , (ymax - ymin)/a.shape[1]])

    gdal_array.BandWriteArray(out.GetRasterBand(1), a)


if __name__ == "__main__":

    import numpy
    xsize, ysize = 10, 10
    a = numpy.random.random((xsize, ysize)).astype(numpy.float64)

    xmin, xmax = -121., -119.
    ymin, ymax = 41., 43.
      
    arr_to_tiff(a, 'a.tiff', xmin, ymin, xmax, ymax)
