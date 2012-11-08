#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" mytag
    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    ----------------Licence----------------
    GNU General Public License version 3

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#import shutil
#import os
#import subprocess
#import random
#import mimetypes
import threading

from multiprocessing import Process
from threading import Thread

from gi.repository import Gtk
from gi.repository import Gdk

class WorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window):
        """Init Worker Thread Class."""
        super(WorkerThread, self).__init__()
        self._notify_window = notify_window
        self._want_abort = 0
        self._stop = threading.Event()
        self.setDaemon(True)
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()
        return None

    def run(self, *args):
        """ run the desired method in a background thread """
        try:
            if len(args) == 1:
                args()
        except TypeError:
            pass
        Thread.__init__(self)


class mytag(object):


    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("main.ui")
        self.builder.connect_signals(self)
        self.worker = None
        if not self.worker:
            self.worker = WorkerThread(self)
        self.run()

    def run(self, *args):
        self.Window = self.builder.get_object("main_window")
        self.Window.set_title("mytag: Python tag editor")
        self.Window.connect("destroy", self.quit)
        self.editbutton = self.builder.get_object("editbutton")
        self.editbutton.connect("clicked", self.workermethods)
        self.folderbutton = self.builder.get_object("folderbutton")
        self.folderbutton.connect("clicked", self.workermethods)
        self.Window.show()
        Gtk.main()
        #
        #self.worker.run(self.test2())

    def quit(self, *args):
        # Permanently stop the process thread
        self.worker._Thread__stop()
        self.Window.destroy()
        Gtk.main_quit(*args)
        return False

    def workermethods(self, *args):
        for items in args:
            if items.get_tooltip_text() == 'Reload the folder list':
                self.worker.run(self.test())
            if items.get_tooltip_text() == 'Edit the selected files':
                self.worker.run(self.test2())
        return True

    def test(self, *args):
        print 'TESTED'
        print 'TESTED'
        print 'TESTED'
        print 'TESTED'
        return True

    def test2(self, *args):
        count = 0
        while count < 1000:
            print 'secondmethodrunning'
            count = count + 1
        return True

if __name__ == "__main__":
    Gdk.threads_init()
    mytag()

