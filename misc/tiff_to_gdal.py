

from tempfile import NamedTemporaryFile
import gdal
import gdal_array

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

if __name__ == "__main__":

    import cPickle

    p = cPickle.load(open('z.pickle'))
    bbox = map(float, p['bbox'])
    z = p['z']

    print array_to_tiff(z, bbox)


