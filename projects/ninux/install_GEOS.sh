wget http://download.osgeo.org/geos/geos-3.3.8.tar.bz2 &&
tar xvfj geos-3.3.8.tar.bz2 &&
cd geos-3.3.8 &&
./configure &&
make &&
make install &&
cd .. &&
rm -rf geos-3.3.8.tar.bz2 geos-3.3.8.tar.bz2