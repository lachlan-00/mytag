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

try:
    import mutagen
    TAG_SUPPORT = True
except ImportError:
    TAG_SUPPORT = True
    print 'Please install python-mutagen'

from multiprocessing import Process
from threading import Thread

from gi.repository import Gtk
from gi.repository import Gdk

MEDIA_TYPES = ['.m4a', '.flac', '.ogg', '.mp2', '.mp3', '.wav', '.spx']
YR_SPLIT = ['-', '/', '\\']


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
        if not TAG_SUPPORT:
            return False
        self.builder = Gtk.Builder()
        self.builder.add_from_file("main.ui")
        self.builder.connect_signals(self)
        self.current_dir = os.getenv('HOME')
        self.new_dir = None
        self.worker = None
        if not self.worker:
            self.worker = WorkerThread(self)
        self.run()

    def connectui(self, *args):
        """ connect all the window wisgets """
        self.settingsbutton = self.builder.get_object("settingsbutton")
        self.settingsbutton.connect("clicked", self.showconfig)
        self.editbutton = self.builder.get_object("editbutton")
        self.editbutton.connect("clicked", self.loadselection)
        self.backbutton = self.builder.get_object("backbutton")
        self.backbutton.connect("clicked", self.goback)
        self.homebutton = self.builder.get_object("homebutton")
        self.homebutton.connect("clicked", self.gohome)
        self.homebutton = self.builder.get_object("gobutton")
        self.homebutton.connect("clicked", self.savetags)
        self.folderlist = self.builder.get_object('folderstore')
        self.foldertree = self.builder.get_object('folderview')
        self.contentlist = self.builder.get_object('filestore')
        self.contenttree = self.builder.get_object('fileview')
        self.titlebutton = self.builder.get_object('titlebutton')
        self.artistbutton = self.builder.get_object('artistbutton')
        self.albumbutton = self.builder.get_object('albumbutton')
        self.albumartistbutton = self.builder.get_object('albumartistbutton')
        self.genrebutton = self.builder.get_object('genrebutton')
        self.trackbutton = self.builder.get_object('trackbutton')
        self.discbutton = self.builder.get_object('discbutton')
        self.yearbutton = self.builder.get_object('yearbutton')
        self.commentbutton = self.builder.get_object('commentbutton')
        self.titleentry = self.builder.get_object('titleentry')
        self.artistentry = self.builder.get_object('artistentry')
        self.albumentry = self.builder.get_object('albumentry')
        self.albumartistentry = self.builder.get_object('albumartistentry')
        self.genreentry = self.builder.get_object('genreentry')
        self.trackentry = self.builder.get_object('trackentry')
        self.discentry = self.builder.get_object('discentry')
        self.yearentry = self.builder.get_object('yearentry')
        self.commententry = self.builder.get_object('commententry')
        self.loadedlabel = self.builder.get_object('loadedlabel')
        self.currentdirlabel = self.builder.get_object('currentdirlabel')

    def run(self, *args):
        """ connect ui functions and show main window """
        self.Window = self.builder.get_object("main_window")
        self.Window.set_title("mytag: Python tag editor")
        self.Window.connect("destroy", self.quit)
        self.ConfWindow = self.builder.get_object("config_window")
        self.connectui()
        self.loadlists()
        # prepare folder and file views
        cell = Gtk.CellRendererText()
        foldercolumn = Gtk.TreeViewColumn("Select Folder:", cell, text=0)
        filecolumn = Gtk.TreeViewColumn("Select Files", cell, text=0)
        # set up folder list
        self.folderview = self.builder.get_object("folderview")
        self.folderview.connect("row-activated", self.folderclick)
        self.foldertree.append_column(foldercolumn)
        self.foldertree.set_model(self.folderlist)
        # set up file list
        self.fileview = self.builder.get_object("fileview")
        self.fileview.connect("row-activated", self.loadselection)
        self.contenttree.append_column(filecolumn)
        self.contenttree.set_model(self.contentlist)
        # fill the file and folder lists
        self.listfolder(self.current_dir)
        self.Window.show()
        #start the main GTK loop
        Gtk.main()

    def loadlists(self):
        # create all the tag lists
        self.title = []
        self.artist = []
        self.album = []
        self.albumartist = []
        self.genre = []
        self.track = []
        self.disc = []
        self.year = []
        self.comment = []
        self.tracklist = []
        self.trackselection = [self.title, self.artist, self.album, 
                               self.albumartist, self.genre, self.track, 
                               self.disc, self.year, self.comment]
        self.uibuttons = [[self.titlebutton, self.titleentry], 
                          [self.artistbutton, self.artistentry], 
                          [self.albumbutton, self.albumentry], 
                          [self.albumartistbutton, self.albumartistentry], 
                          [self.genrebutton, self.genreentry], 
                          [self.trackbutton, self.trackentry], 
                          [self.discbutton, self.discentry], 
                          [self.yearbutton, self.yearentry], 
                          [self.commentbutton, self.commententry]]
        return

    def showconfig(self, *args):
        self.ConfWindow.show()


    def quit(self, *args):
        """ stop the process thread and close the program"""
        self.worker._Thread__stop()
        self.Window.destroy()
        self.ConfWindow.destroy()
        Gtk.main_quit(*args)
        return False

    #def workermethods(self, *args):
    #    """ used to send multiple methods to the workerthread... """
    #    for items in args:
    #        if items.get_tooltip_text() == 'Reload the folder list':
    #            self.worker.run(self.test())
    #        if items.get_tooltip_text() == 'Edit the selected files':
    #            self.worker.run(self.test2())
    #    return True

    def savetags(self, *args):
        print 'savetagsfunction'
        for files in self.current_files:
            print files

    def loadtags(self, *args):
        """ connect chosen files with tags """
        self.loadlists()
        self.clearopenfiles()
        # pull tags for each music file
        for musicfiles in args[0]:
            try:
                item = mutagen.File(musicfiles)
            except:
                print 'Tag error: ' + musicfiles
                item = None
                pass
            # pull tag info per item
            if item:
                tmp_title = str(item.get('TIT2'))
                if tmp_title == 'None':
                    tmp_title = None
                tmp_artist = str(item.get('TPE1'))
                if tmp_artist == 'None':
                    tmp_artist = None
                tmp_album = str(item.get('TALB'))
                if tmp_album == 'None':
                    tmp_album = None
                tmp_albumartist = str(item.get('TPE2'))
                if tmp_albumartist == 'None':
                    tmp_albumartist = None
                tmp_genre = None
                tmp_track = str(item.get('TRCK'))
                if '/' in tmp_track:
                    tmp_track = tmp_track.split('/')[0]
                if len(tmp_track) == 1:
                    tmp_track = '0' + str(tmp_track)
                if len(tmp_track) > 2:
                    tmp_track = tmp_track[:2]
                tmp_disc = str(item.get('TPOS'))
                if '/' in tmp_disc:
                    tmp_disc = tmp_disc.split('/')[0]
                if len(tmp_disc) == 2:
                    tmp_disc = tmp_disc[-1]
                tmp_year = str(item.get('TDRC'))
                if len(tmp_year) != 4:
                    for items in YR_SPLIT:
                        if items in tmp_year:
                            tmp_year = tmp_year.split(items)
                    for items in tmp_year:
                        if len(items) == 4:
                            tmp_year = items
                tmp_comment = None ###??? get comment tag?
                tmp_item = [tmp_title, tmp_artist, tmp_album, tmp_albumartist, 
                            tmp_genre, tmp_track, tmp_disc, tmp_year, 
                            tmp_comment]
                # add tags to list
                self.title.append(tmp_title)
                self.artist.append(tmp_artist)
                self.album.append(tmp_album)
                self.albumartist.append(tmp_albumartist)
                self.genre.append(tmp_genre)
                self.track.append(tmp_track)
                self.disc.append(tmp_disc)
                self.year.append(tmp_year)
                self.comment.append(tmp_comment)
                #self.tracklist.append(tmp_item)
        # compare tags
        count = 0
        for types in self.trackselection:
            comparison = False
            if len(args[0]) == 1:
                comparison = True
            for item in types[1:]:
                if item == None:
                    comparison = False
                    break
                if item != types[0]:
                    comparison = False
                    break
                comparison = True
            if comparison:
                self.uibuttons[count][0].set_active(True)
                if types[0]:
                    self.uibuttons[count][1].set_text(types[0])
                else:
                    self.uibuttons[count][0].set_active(False)
                    self.uibuttons[count][1].set_text('')
            else:
                self.uibuttons[count][0].set_active(False)
                self.uibuttons[count][1].set_text('')
            count = count + 1
        return

    def loadselection(self, *args):
        """ load files into tag editor """
        self.new_files = None
        model, fileiter = self.contenttree.get_selection().get_selected_rows()
        self.current_files = []
        for files in fileiter:
            tmp_file = self.current_dir + '/' + model[files][0]
            self.current_files.append(tmp_file)
        self.loadedlabel.set_text('Loaded: ' + str(len(fileiter)))
        self.loadtags(self.current_files)
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
        self.clearopenfiles()
        self.listfolder(os.getenv('HOME'))

    def goback(self, *args):
        """ go back the the previous directory """
        back_dir = os.path.dirname(self.current_dir)
        self.clearopenfiles()
        self.listfolder(back_dir)

    def clearopenfiles(self):
        count = 0
        while count < len(self.uibuttons):
            self.uibuttons[count][0].set_active(False)
            self.uibuttons[count][1].set_text('')
            count = count + 1
        self.loadedlabel.set_text('')
        return

    def listfolder(self, *args):
        """ function to list the folder column """
        self.current_dir = args[0]
        self.currentdirlabel.set_text('Current Folder: ' + self.current_dir)
        if not type(args[0]) == type(''):
            #print args[0].get_current_folder()
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
        self.clearopenfiles()
        self.listfiles()
        return

    def listfiles(self, *args):
        """ function to fill the file list column """
        self.current_files = []
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
            test_ext = items[(items.rfind('.')):] in MEDIA_TYPES
            if not items[0] == '.' and test_file and test_ext:
                self.contentlist.append([items])
        return


if __name__ == "__main__":
    Gdk.threads_init()
    mytag()

