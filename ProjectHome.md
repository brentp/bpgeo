a collection of geo-related python / javascript modules.
  * **geoservice**.py a web.py script that does geocoding, reverse geocoding via javascript or url-base API.

  * **ubuntu\_build**. a shell script that `apt-get install`s all packages needed for a good geo system. also does svn builds of mapserver, GDAL, and numpy/scipy/matplotlib stuff.

  * **google\_wms** an implementation of WMS Layers for google maps. based of John Deck's work. [example](http://bpgeo.googlecode.com/svn/trunk/google_wms/index.html). Also added getFeatureInfo method to allow simple querying of WMS layers.

  * **squiggly** an afternoon project to make the geos functions available in sqlite so you can do things like:
> > `SELECT INTERSECTION('POLYGON((1.34 .....))', 'POLYGON((12.23 .....))`
just as you would in postGIS. uses sean gillies [shapely](http://trac.gispython.org/projects/PCL/wiki/ShapeLy) library.

  * **misc** some miscellaneous decorators for logging/debugging/timing. and scripts to convert numpy arrays to shapefiles (use `numpy_to_shape` over the older `tiff_to_gdal`)