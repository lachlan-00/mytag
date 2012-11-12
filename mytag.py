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
        self.worker = None
        if not self.worker:
            self.worker = WorkerThread(self)
        self.run()

    def run(self, *args):
        """ create main window and connect functions """
        self.Window = self.builder.get_object("main_window")
        self.Window.set_title("mytag: Python tag editor")
        self.Window.connect("destroy", self.quit)
        self.editbutton = self.builder.get_object("editbutton")
        self.editbutton.connect("clicked", self.loadselection)
        self.backbutton = self.builder.get_object("backbutton")
        self.backbutton.connect("clicked", self.goback)
        self.homebutton = self.builder.get_object("homebutton")
        self.homebutton.connect("clicked", self.gohome)
        # prepare folder and file views
        ## required? cell = Gtk.CellRendererText() ## required?
        ## required? foldercolumn = Gtk.TreeViewColumn("Select Folder:", cell, text=0) ## required?
        ## required? filecolumn = Gtk.TreeViewColumn("Select Files", cell, text=0) ## required?

        self.folderview = self.builder.get_object("folderview")
        self.folderview.connect("row-activated", self.folderclick)
        self.listfolder(self.current_dir)
        ## required? self.foldertree.set_model(self.folderlist)
        ## required? self.foldertree.append_column(foldercolumn)
        ## required? self.foldertree.set_model(self.folderlist)

        self.fileview = self.builder.get_object("fileview")
        self.fileview.connect("row-activated", self.loadselection)
        
        ## required? self.contenttree.append_column(filecolumn)
        ## required? self.contenttree.set_model(self.filelist)
        self.Window.show()
        Gtk.main()

    def quit(self, *args):
        """ stop the process thread and close the program"""
        self.worker._Thread__stop()
        self.Window.destroy()
        Gtk.main_quit(*args)
        return False

    #def workermethods(self, *args):
    #    for items in args:
    #        if items.get_tooltip_text() == 'Reload the folder list':
    #            self.worker.run(self.test())
    #        if items.get_tooltip_text() == 'Edit the selected files':
    #            self.worker.run(self.test2())
    #    return True

    def loadselection(self, *args):
        """ load files into tag editor """
        self.new_files = None
        model, fileiter = self.contenttree.get_selection().get_selected_rows() #.get_selected()
        refs = []
        for files in fileiter:
            refs.append(Gtk.TreeRowReference.new(model, files))
            print files
            self.contenttree.get_selection(model, files)
        print refs
        #if fileiter:
        #    print model[fileiter][0]
        #    self.new_files = self.current_dir + '/' + model[fileiter][0]
        #print self.new_files
        #print dir(self.contenttree.get_selected_rows())
        #print self.contenttree.get_selected_rows().get_selected()
        #print self.contenttree.get_selected_rows().get_selected()
        #if os.path.isfile(self.new_files):
        #    self.listfolder(self.new_files)
        return

    def folderclick(self, *args):
        """ traverse folders on double click """
        model, treeiter = self.foldertree.get_selection().get_selected()
        if treeiter:
            self.new_dir = self.current_dir + '/' + model[treeiter][0]
        if os.path.isdir(self.new_dir):
            self.listfolder(self.new_dir)
        return


    def gohome(self, *args):
        """ go to the defined home folder """
        ### CONF OPTIONS TO BE ADDED TO CHANGE HOME
        self.listfolder(os.getenv('HOME'))

    def goback(self, *args):
        """ go back the the previous directory """
        back_dir = os.path.dirname(self.current_dir)
        self.listfolder(back_dir)


    def listfolder(self, *args):
        """ function to list the folder column """
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
        """ function to fill the file list column """
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


if __name__ == "__main__":
    Gdk.threads_init()
    mytag()

