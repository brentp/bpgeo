SRCDIR=/opt/src/
sudo apt-get update 
sudo apt-get upgrade
sudo apt-get  -y install vim build-essential \
vim-full gfortran python2.5-dev python-tk python-gtk2-dev libwxgtk2.6-dev \
liblapack-dev  libgd2-xpm-dev   \
libblas-dev tcl8.4-dev tk8.4-dev tk8.3-dev libsvn-perl

sudo locale-gen en_US.UTF-8
sudo /usr/sbin/update-locale LANG="en_US.UTF-8"

# set vim as default
sudo update-alternatives --config editor

sudo apt-get -y install libblas-dev rlwrap \
libatlas-cpp-0.6-dev \
libfftw3-dev  libsuitesparse-dev \
swig sqlite3 cvs libmysqlclient15-dev \
libpng12-dev libpq-dev libgl1-mesa-dev libglu1-mesa-dev \
libboost-dev openssh-server  ssh-askpass \
 proj imagemagick libagg-dev keychain \
curl  libtiff4-dev liblzo2-dev \
byacc libiconv-hook-dev flex recode \
firefox libxbase2.0-dev python-setuptools libfreetype6-dev \
subversion apache2-mpm-worker \
byacc bison rsnapshot postgresql-contrib-8.3 postgresql-server-dev-8.3 \
postgresql-8.3-postgis h5utils
#libcurl4-dev


sudo echo "<900913> +proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs  <>" >> /usr/share/proj/epsg
sudo echo "<54004> +proj=merc +lat_ts=0 +lon_0=0 +k=1.000000 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs <>" >> /usr/share/proj/epsg
# and move common ones to the top for better performance


# INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 900913, 'EPSG', 6, '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs', 'PROJCS["unnamed",GEOGCS["unnamed ellipse",DATUM["unknown",SPHEROID["unnamed",6378137,0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Mercator_2SP"],PARAMETER["standard_parallel_1",0],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"]]');
# INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 54004, 'spatialreference.org', 54004, '+proj=merc +lon_0=0 +k=1.000000 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ', 'PROJCS["World_Mercator",GEOGCS["GCS_WGS_1984",DATUM["WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Mercator_1SP"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["Central_Meridian",0],PARAMETER["Standard_Parallel_1",0],UNIT["Meter",1],AUTHORITY["EPSG","54004"]]');
# INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 96630, 'sr-org', 6630, '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs ', 'PROJCS["NAD_1983_Albers",GEOGCS["NAD83",DATUM["North_American_Datum_1983",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6269"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9108"]],AUTHORITY["EPSG","4269"]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["standard_parallel_1",29.5],PARAMETER["standard_parallel_2",45.5],PARAMETER["latitude_of_center",23],PARAMETER["longitude_of_center",-96],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["meters",1]]');

# sudo apt-get install sun-java6-jdk libmysql-java libpg-java

wget http://peak.telecommunity.com/dist/ez_setup.py
sudo python2.5 ez_setup.py
cd /tmp/; wget http://effbot.org/downloads/Imaging-1.1.7.tar.gz
tar xzvf Imaging-1.1.7.tar.gz
cd Imaging-1*
# edit setup.py and set TCL_ROOT = "/usr/include/tcl8.3"

# git manpages (i always forget how to do this)
# wget "http://kernel.org/pub/software/scm/git/git-manpages-$GIT_VERSION.tar.bz2"
# sudo tar xjv -C /usr/local/share/man        -f "git-manpages-$GIT_VERSION.tar.bz2"
 

mkdir ${SRCDIR}/
cd ${SRCDIR}/
wget http://modwsgi.googlecode.com/files/mod_wsgi-2.4.tar.gz
tar xzvf mod_wsgi-2.4.tar.gz
cd mod_wsgi-2.4
./configure
make -j4
sudo make install
#echo 'LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so' >> /etc/apache2/apache2.conf
# see the _very_ good docs for modwsgi on it's google project page. 


cd ${SRCDIR}
mkdir geos
cd geos
GV=3.1.0 
wget http://download.osgeo.org/geos/geos-${GV}.tar.bz2
bunzip2 geos-${GV}.tar.bz2
tar xvf geos-${GV}.tar
cd geos-${GV}
./configure;make -j4; 
sudo make install

sudo echo "/usr/local/lib" >> /etc/ld.so.conf
sudo ldconfig

mkdir ${SRCDIR}/gdal
cd ${SRCDIR}/gdal
svn checkout https://svn.osgeo.org/gdal/trunk/gdal gdalsvn
cd gdalsvn
# make sure to build with internal to support bigtiff.
./configure --with-libtiff=internal
make -j4
sudo make install

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
PV=1.3.5
mkdir postgis
cd postgis
wget http://postgis.refractions.net/download/postgis-${PV}.tar.gz
tar xzvf postgis-${PV}.tar.gz
cd postgis-${PV}
# these LDFLAGS, prefix seem necessary
LDFLAGS=-lstdc++ ./configure --prefix=/usr/local
make
sudo make install
# and set client_encoding = unicode in postgresql.conf


cd ${SRCDIR}
svn co https://svn.osgeo.org/mapserver/trunk/mapserver mapserversvn
cd mapserversvn
./configure \
--with-postgis=/usr/bin/pg_config \
--with-threads \
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
# to make python mapscript. make clean then re-run above without agg
# or build agg from source with -fPIC
cd mapscript/python
sudo rm -rf build
swig -python -shadow -modern -templatereduce -fastdispatch -fvirtual -fastproxy -modernargs -castmode -dirvtable -fastinit -fastquery -noproxydel -nobuildnone -o mapscript_wrap.c ../mapscript.i
sudo python setup.py install

sudo easy_install -UZ ipython==dev cython
sudo easy_install -UZ mako genshi sqlalchemy==dev simplejson

cd ${SRCDIR}/
svn co http://svn.scipy.org/svn/numpy/trunk numpysvn
cd numpysvn
sudo python2.5 setup.py install
svn co http://svn.scipy.org/svn/scipy/trunk scipysvn
cd scipysvn
sudo python2.5 setup.py install

svn co https://matplotlib.svn.sourceforge.net/svnroot/matplotlib/trunk/matplotlib matplotlib-svn
cd matplotlib-svn
sudo python2.5 setup.py install

sudo easy_install -UZ http://www.initd.org/pub/software/psycopg/PSYCOPG-2-0/psycopg2-2.0.9.tar.gz


sudo easy_install-2.5 -UZ http://superb-west.dl.sourceforge.net/sourceforge/mysql-python/MySQL-python-1.2.3c1.tar.gz

# trac
sudo apt-get install python-clearsilver clearsilver-dev
sudo easy_install-2.5 Trac
