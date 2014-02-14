
Install alsa for debug (alsasink gstreamer element)

# yum install alsa-lib alsa-lib-devel





Install gstreamer 1.2

export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig
export LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib

wget http://gstreamer.freedesktop.org/src/gst-libav/gst-libav-1.2.0.tar.xz
wget --no-check-certificate https://webm.googlecode.com/files/libvpx-v1.2.0.tar.bz2

wget http://ftp.gnome.org/pub/gnome/sources/gobject-introspection/1.38/gobject-introspection-1.38.0.tar.xz
wget http://gstreamer.freedesktop.org/src/gstreamer/gstreamer-1.2.0.tar.xz
wget http://gstreamer.freedesktop.org/src/gst-plugins-base/gst-plugins-base-1.2.0.tar.xz
wget http://gstreamer.freedesktop.org/src/gst-plugins-good/gst-plugins-good-1.2.0.tar.xz
wget http://gstreamer.freedesktop.org/src/gst-plugins-ugly/gst-plugins-ugly-1.2.0.tar.xz
wget http://gstreamer.freedesktop.org/src/gst-plugins-bad/gst-plugins-bad-1.2.0.tar.xz


tar xJf gst-libav-1.2.0.tar.xz
tar xjf libvpx-v1.2.0.tar.bz2
tar xJf gobject-introspection-1.38.0.tar.xz
tar xJf gstreamer-1.2.0.tar.xz
tar xJf gst-plugins-base-1.2.0.tar.xz
tar xJf gst-plugins-good-1.2.0.tar.xz
tar xJf gst-plugins-ugly-1.2.0.tar.xz
tar xJf gst-plugins-bad-1.2.0.tar.xz

cd ./gst-libav-1.2.0
./configure
make && make install
cd ..

cd ./libvpx-v1.2.0
./configure --enable-realtime-only --enable-error-concealment --disable-examples --enable-vp8 --enable-shared --enable-pic --as=yasm
make && make install
cd ..

cd ./gobject-introspection-1.38.0
./configure --disable-static
make && make install
cd ..

cd ./gstreamer-1.2.0
./configure --enable-introspection=yes
make && make install
cd ..

cd ./gst-plugins-base-1.2.0
./configure --enable-introspection=yes
make && make install
cd ..

cd ./gst-plugins-good-1.2.0
./configure
make && make install
cd ..

cd ./gst-plugins-ugly-1.2.0
./configure
make && make install
cd ..

cd ./gst-plugins-bad-1.2.0
./configure --enable-introspection=yes
make && make install
cd ..


