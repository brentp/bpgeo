SRCDIR=/opt/src/
sudo apt-get update 
sudo apt-get upgrade
sudo apt-get install vim build-essential \
gfortran python2.5-dev python-tk python-gtk2-dev libwxgtk2.6-dev \
lapack3-dev  libgd2-xpm-dev   \
refblas3-dev tcl8.4-dev tk8.4-dev  \
scalapack-lam-dev \
atlas3-base-dev \
libatlas-cpp-0.6-dev \
fftw3-dev libumfpack4-dev \
swig sqlite3 cvs libmysqlclient-dev \
libpng12-dev libpq-dev libgl1-mesa-dev libglu1-mesa-dev \
libboost-dev openssh-server  ssh-askpass \
blitz++ proj imagemagick libagg-dev keychain \
curl libcurl3-dev libtiff4-dev liblzo2-dev \
php5-dev byacc libiconv-hook-dev flex recode \
firefox libxbase2.0-dev python-setuptools libfreetype6-dev \
subversion apache2-utils apache2-threaded-dev apache2 wget libreadline5-dev \
byacc bison rsnapshot postgresql-contrib-8.2 postgresql-server-dev-8.2


sudo echo "<900913> +proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs  <>" >> /usr/share/proj/epsg
sudo echo "<54004> +proj=merc +lat_ts=0 +lon_0=0 +k=1.000000 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs <>" >> /usr/share/proj/epsg
# INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 900913, 'EPSG', 6, '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs', 'PROJCS["unnamed",GEOGCS["unnamed ellipse",DATUM["unknown",SPHEROID["unnamed",6378137,0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Mercator_2SP"],PARAMETER["standard_parallel_1",0],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"]]');

# sudo apt-get install sun-java6-jdk libmysql-java libpg-java

# try to move to 2.5
wget http://peak.telecommunity.com/dist/ez_setup.py
sudo python2.5 ez_setup.py
sudo easy_install-2.5 -UZ http://effbot.org/downloads/Imaging-1.1.6.tar.gz

mkdir ${SRCDIR}/
cd ${SRCDIR}/
svn checkout http://modwsgi.googlecode.com/svn/trunk/ modwsgi
cd modwsgi
./configure
make -j4
sudo make install
#echo 'LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so' >> /etc/apache2/apache2.conf
# see the _very_ good docs for modwsgi on it's google project page. 


cd ${SRCDIR}
mkdir geos
cd geos
wget http://geos.refractions.net/geos-3.0.0rc4.tar.bz2
bunzip2 geos-3.0.0rc4.tar.bz2
tar xvf geos-3.0.0rc4.tar
cd geos-3.0.0rc4
./configure;make -j4; 
sudo make install

sudo echo "/usr/local/lib" >> /etc/ld.so.conf
sudo ldconfig

mkdir ${SRCDIR}/gdal
cd ${SRCDIR}/gdal
wget http://download.osgeo.org/gdal/gdal-1.4.2.tar.gz
tar zxvf gdal-1.4.2.tar.gz
cd gdal-1.4.2
./configure --without-python --with-sqlite=/usr/include
make -j4
sudo make install

sudo ldconfig
#######################################################
# GRASS: http://grass.itc.it/download/index.php
#  http://trac.osgeo.org/gdal/wiki/GRASS
#######################################################
cd ${SRCDIR}
export CVSROOT=:pserver:grass-guest@intevation.de:/home/grass/grassrepository
echo "password is 'grass'"
cvs login
cvs -z3 co grass6
cd grass6
cvs up -dP
./configure --with-cxx --with-sqlite \
--with-postgres-libs=/usr/include/postgresql/libpq/ \
--with-postgres-includes=/usr/include/postgresql/ \
--with-freetype --with-freetype-includes=/usr/include/freetype2 \
--with-proj-share=/usr/share/proj \
--with-gdal=/usr/local/bin/gdal-config \
--with-blas --with-lapack --with-python \
--with-tcltk-includes=/usr/include/tcl8.4 \
--with-readline 
make -j4
cd raster; make; cd ..; cd vector; make; cd ..; cd misc; make; cd ..; cd display; make; cd ..; cd general; make; cd ..; cd imagery; make; cd ..; cd db; make; cd ..; cd ps; make; cd ..; cd gui; make; cd ..; cd visualization; make; cd ..; cd scripts; make; cd ..; cd tools; make; cd ..; cd gem; make; cd ..; cd sites; make; cd ..; 
sudo make install


cd ${SRCDIR}
svn checkout http://svn.refractions.net/postgis/trunk postgis-svn
cd postgis-svn
# these LDFLAGS, prefix seem necessary
LDFLAGS=-lstdc++ ./configure --prefix=/usr/local
make
sudo make install
# and set client_encoding = unicode in postgresql.conf


cd ${SRCDIR}
svn co https://svn.osgeo.org/mapserver/trunk/mapserver mapserver
cd mapserver
./configure \
--with-postgis=/usr/bin/pg_config \
--with-gdal=/usr/local/bin/gdal-config \
--with-ogr=/usr/local/bin/gdal-config \
--with-wmsclient --with-wfs \
--with-geos=/usr/local/bin/geos-config \
--with-proj \
--with-httpd=/usr/sbin/apache2 \
--with-agg=/usr \
--with-gd=/usr  \
--with-freetype=/usr/bin/freetype-config
make
sudo mkdir /usr/lib/cgi-bin/
sudo cp mapserv /usr/lib/cgi-bin/

cd ${SRCDIR}
svn co http://svn.scipy.org/svn/numpy/trunk numpy
cd ${SRCDIR}/numpy
sudo python2.5 setup.py install

cd ${SRCDIR}
svn co https://matplotlib.svn.sourceforge.net/svnroot/matplotlib/trunk/matplotlib/ matplotlib
cd ${SRCDIR}/matplotlib/
# set all *BUILD* = 0 except for BUILD_WXAGG = 'auto'
# may need to set BUILD_GTK = 0 in multiple places in setup.py
sudo python2.5 setup.py install

cd ${SRCDIR}/
svn co http://svn.scipy.org/svn/scipy/trunk scipy
cd scipy
echo "numexpr" > Lib/sandbox/enabled_packages.txt
sudo python2.5 setup.py install

cd ${SRCDIR}/
svn co http://ipython.scipy.org/svn/ipython/ipython/trunk ipython
cd ${SRCDIR}/ipython/
sudo python2.5 setup.py install

cd ${SRCDIR}
svn co http://code.djangoproject.com/svn/django/branches/gis geodjango
cd geodjango
sudo python2.5 setup.py install

sudo easy_install-2.5 -UZ http://initd.org/pub/software/psycopg/psycopg2-latest.tar.gz
sudo easy_install-2.5 -UZ cython  # the sage version of pyrex with enhancements

#### JAVA
#wget http://www.iki.fi/kuparine/comp/ubuntu/install.sh
#sh install.sh


