INSTALLPATH="/usr/share/mytag"
INSTALLTEXT="mytag is now installed"
UNINSTALLTEXT="mytag has been removed"

install-req:
	@mkdir -p $(INSTALLPATH)
	@cp -r mytag/* $(INSTALLPATH) -f
	@cp README $(INSTALLPATH) -f
	@cp AUTHORS $(INSTALLPATH) -f
	@cp LICENSE $(INSTALLPATH) -f
	@cp bin/mytag /usr/bin/ -f
	@cp share/mytag.png /usr/share/pixmaps -f
	@cp share/mytag.desktop /usr/share/applications/ -f
	@chmod +x /usr/bin/mytag
	@chmod +x /usr/share/mytag/mytag.py

install: install-req
	@echo $(INSTALLTEXT)

uninstall-req:
	@rm -rf $(INSTALLPATH)
	@rm /usr/share/pixmaps/mytag.png
	@rm /usr/share/applications/mytag.desktop
	@rm /usr/bin/mytag

uninstall: uninstall-req
	@echo $(UNINSTALLTEXT)
