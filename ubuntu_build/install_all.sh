SRCDIR=/opt/src/
sudo apt-get update 
sudo apt-get upgrade
sudo apt-get install vim  \
gfortran python2.5-dev python-tk python-gtk2-dev libwxgtk2.6-dev \
lapack3-dev  libgd2-xpm-dev   \
refblas3-dev tcl8.4-dev tk8.4-dev  \
scalapack-lam-dev \
atlas3-base-dev \
libatlas-cpp-0.6-dev \
fftw3-dev libumfpack4-dev \
swig sqlite3 cvs \
libpng12-dev libpq-dev libgl1-mesa-dev libglu1-mesa-dev \
libboost-dev openssh-server  ssh-askpass \
blitz++ proj imagemagick libagg-dev keychain \
curl libcurl3-dev libtiff4-dev liblzo2-dev \
php5-dev byacc libiconv-hook-dev flex recode \
firefox libxbase2.0-dev python-setuptools libfreetype6-dev \
subversion apache2-utils apache2-threaded-dev apache2 wget libreadline5-dev \
byacc bison rsnapshot postgresql-contrib-8.2 postgresql-server-dev-8.2


# try to move to 2.5
wget http://peak.telecommunity.com/dist/ez_setup.py
sudo python2.5 ez_setup.py
sudo easy_install-2.5 -UZ http://effbot.org/downloads/Imaging-1.1.6.tar.gz

mkdir ${SRCDIR}/
cd ${SRCDIR}/
svn checkout http://modwsgi.googlecode.com/svn/trunk/ modwsgi
cd modwsgi
./configure
make
sudo make install
#echo 'LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so' >> /etc/apache2/apache2.conf
# see the _very_ good docs for modwsgi on it's google project page. 

cd ${SRCDIR}
mkdir geos
cd geos
wget http://geos.refractions.net/geos-3.0.0rc4.tar.bz2
tar xvf geos-3.0.0rc4.tar.bz2
cd geos-3.0.0
./configure;make; 
sudo make install

sudo echo "/usr/local/lib" >> /etc/ld.so.conf
sudo ldconfig

mkdir ${SRCDIR}/gdal
cd ${SRCDIR}/gdal
wget http://download.osgeo.org/gdal/gdal-1.4.2.tar.gz
tar zxvf gdal-1.4.2.tar.gz
cd gdal-1.4.2
./configure --without-python --with-sqlite=/usr/include
make -j2
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
make
cd raster; make; cd ..; cd vector; make; cd ..; cd misc; make; cd ..; cd display; make; cd ..; cd general; make; cd ..; cd imagery; make; cd ..; cd db; make; cd ..; cd ps; make; cd ..; cd gui; make; cd ..; cd visualization; make; cd ..; cd scripts; make; cd ..; cd tools; make; cd ..; cd gem; make; cd ..; cd sites; make; cd ..; 
sudo make install


cd ${SRCDIR}
svn checkout http://svn.refractions.net/postgis/trunk postgis-svn
cd postgis-svn
# these LDFLAGS, prefix seem necessary
LDFLAGS=-lstdc++ ./configure --prefix=/usr/local
make
sudo make install


cd ${SRCDIR}
svn co https://svn.osgeo.org/mapserver/trunk/mapserver mapserver
cd mapserver
./configure \
--with-postgis=/usr/bin/pg_config \
--with-gdal=/usr/local/bin/gdal-config \
--with-ogr=/usr/local/bin/gdal-config \
--with-wmsclient --with-wfs \
--with-geos=/usr/bin/geos-config \
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

#### JAVA
#wget http://www.iki.fi/kuparine/comp/ubuntu/install.sh
#sh install.sh
