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
import os
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
        self.current_dir = os.getenv('HOME')
        self.new_dir = None
        self.folderlist = self.builder.get_object('folderstore')
        self.foldertree = self.builder.get_object('folderview')
        self.contentlist = self.builder.get_object('filestore')
        self.contenttree = self.builder.get_object('fileview')
        #self.choosefolder = self.builder.get_object('librarychooser')
        self.worker = None
        if not self.worker:
            self.worker = WorkerThread(self)
        self.run()

    def run(self, *args):
        self.Window = self.builder.get_object("main_window")
        self.Window.set_title("mytag: Python tag editor")
        self.Window.connect("destroy", self.quit)
        self.editbutton = self.builder.get_object("editbutton")
        self.editbutton.connect("clicked", self.loadselection)
        self.backbutton = self.builder.get_object("backbutton")
        self.backbutton.connect("clicked", self.goback)
        self.homebutton = self.builder.get_object("homebutton")
        self.homebutton.connect("clicked", self.gohome)
        self.folderview = self.builder.get_object("folderview")
        self.folderview.connect("row-activated", self.folderclick)
        self.listfolder(self.current_dir)
        self.foldertree.set_model(self.folderlist)
        cell = Gtk.CellRendererText()
        foldercolumn = Gtk.TreeViewColumn("Select Folder:", cell, text=0)
        self.foldertree.append_column(foldercolumn)
        self.foldertree.set_model(self.folderlist)
        filecolumn = Gtk.TreeViewColumn("Select Files", cell, text=0)
        self.contenttree.append_column(filecolumn)
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

    def loadselection(self, *args):
        print dir(self.contenttree.get_selection())
        model, fileiter = self.contenttree.get_selection().get_selected()
        if fileiter:
            print model[treeiter][0]
            #self.new_files = self.current_dir + '/' + model[treeiter][0]
        #if os.path.isdir(self.new_dir):
        #    self.listfolder(self.new_dir)
        return

    def folderclick(self, *args):
        model, treeiter = self.foldertree.get_selection().get_selected()
        if treeiter:
            self.new_dir = self.current_dir + '/' + model[treeiter][0]
        if os.path.isdir(self.new_dir):
            self.listfolder(self.new_dir)
        return


    def gohome(self, *args):
        print 'gohome'
        self.listfolder(os.getenv('HOME'))

    def goback(self, *args):
        back_dir = os.path.dirname(self.current_dir)
        #print dir(self.choosefolder)
        self.listfolder(back_dir)


    def listfolder(self, *args):
        self.current_dir = args[0]
        if not type(args[0]) == type(''):
            print args[0].get_current_folder()
            self.current_dir = args[0].get_current_folder()
        self.filelist = os.listdir(self.current_dir)
        self.filelist.sort()
        # clear list if we have scanned before
        for items in self.folderlist:
            self.folderlist.remove(items.iter)
        # clear combobox before adding entries
        for items in self.foldertree:
            self.foldertree.remove(items.iter)
        # search the supplied directory for items
        for items in self.filelist:
            test_dir = os.path.isdir(self.current_dir + '/'+ items)
            if not items[0] == '.' and test_dir:
                self.folderlist.append([items])
        self.listfiles()
        return

    def listfiles(self, *args):
        print self.current_dir
        files_dir = os.listdir(self.current_dir)
        files_dir.sort()
        # clear list if we have scanned before
        for items in self.contentlist:
            self.contentlist.remove(items.iter)
        # clear combobox before adding entries
        for items in self.contenttree:
            self.contenttree.remove(items.iter)
        # search the supplied directory for items
        for items in files_dir:
            test_file = os.path.isfile(self.current_dir + '/'+ items)
            if not items[0] == '.' and test_file:
                self.contentlist.append([items])
        return

    def test2(self, *args):
        count = 0
        while count < 1000:
            print 'secondmethodrunning'
            count = count + 1
        return True

if __name__ == "__main__":
    Gdk.threads_init()
    mytag()

