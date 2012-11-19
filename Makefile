INSTALLPATH="/usr/share/mytag"
INSTALLTEXT="mytag is now installed"
UNINSTALLTEXT="mytag has been removed"

install-req:
	mkdir -p $(INSTALLPATH)
	cp bin/mytag /usr/bin/ -f
	cp share/mytag.desktop /usr/share/applications/ -f
	cp mytag/* $(INSTALLPATH) -f
	cp share/mytag.png /usr/share/pixmaps
        cp README $(INSTALLPATH) -f
	cp UNINSTALL.sh $(INSTALLPATH) -f

install: install-req
	$(INSTALLTEXT)

uninstall-req:
	# Simply remove the installation path folder
	rm -rf $(INSTALLPATH)
        rm /usr/share/pixmaps/mytag.png
        rm /usr/share/applications/mytag.desktop
        rm /usr/bin/mytag

uninstall: uninstall-req
	$(UNINSTALLTEXT)
