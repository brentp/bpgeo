SRCDIR=/usr/local/src
cd $SRCDIR
svn co https://matplotlib.svn.sourceforge.net/svnroot/matplotlib/trunk/matplotlib/ matplotlibsvn
cd matplotlibsvn
sudo python setup.py install

cd $SRCDIR


# virtualenv
sudo easy_install -UZ virtualenvwrapper virtualenv
mkdir ~/.virtualenvs
# add 'source /usr/local/bin/virtualenvwrapper_bashrc' to ~/.bashrc

