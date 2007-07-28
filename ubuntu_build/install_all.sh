SRCDIR=/opt/src/
sudo apt-get update 
sudo apt-get upgrade
sudo apt-get install vim  \
gfortran python2.5-dev python-tk python-gtk2-dev libwxgtk2.6-dev \
lapack3-dev libgd2-noxpm-dev   \
refblas3-dev tcl8.4-dev tk8.4-dev  \
scalapack-lam-dev \
atlas3-base-dev \
libatlas-cpp-0.6-dev \
fftw3-dev libumfpack4-dev \
swig libgeos-dev sqlite3 \
libpng12-dev libpq-dev libgl1-mesa-dev libglu1-mesa-dev \
libboost-dev openssh-server \
blitz++ proj imagemagick \
curl libcurl3-dev libtiff4-dev liblzo2-dev \
php5-dev byacc libiconv-hook-dev flex recode \
firefox libxbase2.0-dev python-setuptools libfreetype6-dev \
subversion apache2-utils wget libreadline5-dev \
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
# need to do some other config for modwsgi, see the _very_ good docs 
# on it's google project page. 

cd ${SRCDIR}
mkdir geos
cd geos
wget http://geos.refractions.net/geos-3.0.0rc4.tar.bz2
tar xvf geos-3.0.0rc4.tar.bz2
cd geos-3.0.0
./configure;make; 
sudo make install

mkdir ${SRCDIR}/gdal
cd ${SRCDIR}/gdal
wget http://download.osgeo.org/gdal/gdal-1.4.2.tar.gz
echo "BUILD GDAL"
# TODO. add my default config stuff.

# GRASS: http://grass.itc.it/download/index.php
#TODO build postgis/postgresql

svn checkout http://svn.refractions.net/postgis/trunk postgis-svn
cd postgis-svn
 LDFLAGS=-lstdc++ ./configure
make
sudo make install


cd ${SRCDIR}/
svn co https://svn.osgeo.org/mapserver/trunk/mapserver mapserver
cd mapserver
echo "BUILD MAPSERVER"
# TODO. add my default config stuff.

cd ${SRCDIR}
svn co http://svn.scipy.org/svn/numpy/trunk numpy
cd ${SRCDIR}/numpy/numpy
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

#### JAVA
#wget http://www.iki.fi/kuparine/comp/ubuntu/install.sh
#sh install.sh
