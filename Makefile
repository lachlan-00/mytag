INSTALLPATH="/usr/share/mytag"
INSTALLTEXT="mytag is now installed"
UNINSTALLTEXT="mytag has been removed"

install-req:
	@mkdir -p $(INSTALLPATH)
	@cp bin/mytag /usr/bin/ -f
	@cp share/mytag.desktop /usr/share/applications/ -f
	@cp mytag/* $(INSTALLPATH) -f
	@cp share/mytag.png /usr/share/pixmaps
	@cp README $(INSTALLPATH) -f

install: install-req
	@echo $(INSTALLTEXT)

uninstall-req:
	@rm -rf $(INSTALLPATH)
	@rm /usr/share/pixmaps/mytag.png
	@rm /usr/share/applications/mytag.desktop
	@rm /usr/bin/mytag

uninstall: uninstall-req
	@echo $(UNINSTALLTEXT)
