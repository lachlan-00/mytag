#!/bin/sh
gksu "cp ./usr/bin/mytag /usr/bin/"
gksu "cp ./usr/share/applications/mytag.desktop /usr/share/applications/"
gksu "mkdir /usr/share/mytag"
gksu "cp ./usr/share/mytag/main.ui /usr/share/mytag/"
gksu "cp ./usr/share/mytag/mytag.conf.example /usr/share/mytag/"
gksu "cp ./usr/share/mytag/README /usr/share/mytag/"
gksu "cp ./usr/share/pixmaps/mytag.png /usr/share/pixmaps/"
