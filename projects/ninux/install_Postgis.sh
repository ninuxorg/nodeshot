wget http://download.osgeo.org/postgis/source/postgis-2.0.3.tar.gz &&
tar xfvz postgis-2.0.3.tar.gz &&
cd postgis-2.0.3 &&
./configure &&
make &&
make install &&
ldconfig &&
make comments-install 