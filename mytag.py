#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" mytag: Python tag editor
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
import ConfigParser
import sys

#from multiprocessing import Process
#from threading import Thread

from gi.repository import Gtk
from gi.repository import Gdk

# quit if using python3
if sys.version[0] == 3:
    raise Exception('not python3 compatible, please use python 2.x')

# python-eyeD3 required for editing and loading tags
try:
    import eyeD3
    TAG_SUPPORT = True
except ImportError:
    TAG_SUPPORT = False


MEDIA_TYPES = ['.m4a', '.flac', '.ogg', '.mp2', '.mp3', '.wav', '.spx']
YR_SPLIT = ['-', '/', '\\']
MUSIC_TAGS = ['%artist%', '%albumartist%', '%album%', '%year%',
                 '%title%', '%disc%', '%track%']


class WorkerThread(threading.Thread):
    """ run a separate thread to the ui """
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
        """ run the desired method in the background thread """
        try:
            if len(args) == 1:
                args()
        except TypeError:
            pass
        threading.Thread.__init__(self)


class MYTAG(object):
    """ browse folders and set set using ui """
    def __init__(self):
        """ start mytag """
        if not TAG_SUPPORT:
            raise Exception('Please install python-eyed3')
        self.builder = Gtk.Builder()
        self.builder.add_from_file("main.ui")
        self.builder.connect_signals(self)
        self.worker = None
        if not self.worker:
            self.worker = WorkerThread(self)
        # get config info
        self.conf = ConfigParser.RawConfigParser()
        self.conf.read('./mytag.conf')
        self.homefolder = self.conf.get('conf', 'home')
        self.library = self.conf.get('conf', 'defaultlibrary')
        self.libraryformat = self.conf.get('conf', 'outputstyle')
        self.current_dir = self.homefolder
        self.current_files = None
        self.filelist = None
        # load main window items
        self.window = self.builder.get_object("main_window")
        self.settingsbutton = self.builder.get_object("settingsbutton")
        self.editbutton = self.builder.get_object("editbutton")
        self.backbutton = self.builder.get_object("backbutton")
        self.homebutton = self.builder.get_object("homebutton")
        self.gobutton = self.builder.get_object("gobutton")
        self.folderlist = self.builder.get_object('folderstore')
        self.foldertree = self.builder.get_object('folderview')
        self.folderview = self.builder.get_object("folderview")
        self.fileview = self.builder.get_object("fileview")
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
        # load config window items
        self.confwindow = self.builder.get_object("config_window")
        self.libraryentry = self.builder.get_object('libraryentry')
        self.styleentry = self.builder.get_object('styleentry')
        self.homeentry = self.builder.get_object('homeentry')
        self.applybutton = self.builder.get_object("applyconf")
        self.closebutton = self.builder.get_object("closeconf")
        # set tag items
        self.title = None
        self.artist = None
        self.album = None
        self.albumartist = None
        self.genre = None
        self.track = None
        self.disc = None
        self.year = None
        self.comment = None
        self.tracklist = None
        self.trackselection = None
        self.uibuttons = None
        # create lists and connect actions
        self.loadlists()
        self.connectui()
        self.run()

    def connectui(self):
        """ connect all the window wisgets """
        # main window actions
        self.window.connect("destroy", self.quit)
        self.settingsbutton.connect("clicked", self.showconfig)
        self.editbutton.connect("clicked", self.loadselection)
        self.backbutton.connect("clicked", self.goback)
        self.homebutton.connect("clicked", self.gohome)
        self.gobutton.connect("clicked", self.savetags)
        # config window actions
        self.applybutton.connect("clicked", self.saveconf)
        self.closebutton.connect("clicked", self.closeconf)
        cell = Gtk.CellRendererText()
        foldercolumn = Gtk.TreeViewColumn("Select Folder:", cell, text=0)
        filecolumn = Gtk.TreeViewColumn("Select Files", cell, text=0)
        # set up folder list
        self.folderview.connect("row-activated", self.folderclick)
        self.foldertree.append_column(foldercolumn)
        self.foldertree.set_model(self.folderlist)
        # set up file list
        self.fileview.connect("row-activated", self.loadselection)
        self.contenttree.append_column(filecolumn)
        self.contenttree.set_model(self.contentlist)
        # list default dir
        self.listfolder(self.current_dir)

    def run(self):
        """ show the main window and start the main GTK loop """
        self.window.show()
        Gtk.main()

    def loadlists(self):
        """ create/empty all the lists used for tagging """
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
        """ fill and show the config window """
        self.conf.read('./mytag.conf')
        self.homefolder = self.conf.get('conf', 'home')
        self.library = self.conf.get('conf', 'defaultlibrary')
        self.libraryformat = self.conf.get('conf', 'outputstyle')
        self.homeentry.set_text(self.homefolder)
        self.libraryentry.set_text(self.library)
        self.styleentry.set_text(self.libraryformat)
        self.confwindow.show()

    def saveconf(self, *args):
        """ save any config changes """
        self.conf.set('conf', 'home', self.homeentry.get_text())
        self.conf.set('conf', 'defaultlibrary', self.libraryentry.get_text())
        self.conf.set('conf', 'outputstyle', self.styleentry.get_text())

    def closeconf(self, *args):
        """ hide the config window """
        self.confwindow.hide()

    def quit(self, *args):
        """ stop the process thread and close the program"""
        self.worker._Thread__stop()
        self.confwindow.destroy()
        self.window.destroy()
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
        """ update the loaded files with new tags """
        # check for active changes
        count = 0
        tmp_changes = []
        while count < len(self.uibuttons):
            if self.uibuttons[count][0].get_active():
                tmp_changes.append([count, self.uibuttons[count][1].get_text()])
            count = count + 1
        for files in self.current_files:
            tmp_title = None
            tmp_artist = None
            tmp_album = None
            tmp_albumartist = None
            tmp_genre = None
            tmp_track = None
            tmp_disc = None
            tmp_year = None
            tmp_comment = None
            try:
                item = eyeD3.Tag()
                item.link(files)
                item.setVersion(eyeD3.ID3_V2_4)
                item.setTextEncoding(eyeD3.UTF_8_ENCODING)
            except:
                print 'Tag error: ' + files
                item = None
                pass
            if item:
                # get the current tags
                current_title = item.getTitle()
                if current_title == 'None':
                    current_title = None
                current_artist = item.getArtist('TPE1')
                if current_artist == 'None':
                    current_artist = None
                current_album = item.getAlbum()
                if current_album == 'None':
                    current_album = None
                current_albumartist = item.getArtist('TPE2')
                if current_albumartist == 'None':
                    current_albumartist = None
                current_genre = str(item.getGenre())
                if current_genre == 'None':
                    current_genre = None
                current_track = str(item.getTrackNum()[0])
                if '/' in current_track:
                    current_track = current_track.split('/')[0]
                if len(current_track) == 1:
                    current_track = '0' + str(current_track)
                if len(current_track) > 2:
                    current_track = current_track[:2]
                #current_disc = str(item.get('TPOS'))
                current_disc = str(item.getDiscNum()[0])
                if '/' in current_disc:
                    current_disc = current_disc.split('/')[0]
                if len(current_disc) == 2:
                    current_disc = current_disc[-1]
                current_year = str(item.getYear())
                if len(current_year) != 4:
                    for items in YR_SPLIT:
                        if items in current_year:
                            current_year = current_year.split(items)
                    for items in current_year:
                        if len(items) == 4:
                            current_year = items
                if current_year == 'None':
                    current_year = None
                current_comment = item.getComment()
                if current_comment == 'None':
                    current_comment = None
                # get the changes from the UI
                for changes in tmp_changes:
                    if changes[0] == 0:
                        tmp_title = changes[1]
                    if changes[0] == 1:
                        tmp_artist = changes[1]
                    if changes[0] == 2:
                        tmp_album = changes[1]
                    if changes[0] == 3:
                        tmp_albumartist = changes[1]
                    if changes[0] == 4:
                        tmp_genre = changes[1]
                    if changes[0] == 5:
                        tmp_track = changes[1]
                    if changes[0] == 6:
                        tmp_disc = changes[1]
                    if changes[0] == 7:
                        tmp_year = changes[1]
                    if changes[0] == 8:
                        tmp_comment = changes[1]
                # set changes
                if tmp_title != None and tmp_title != current_title:
                    item.setTitle(tmp_title)
                if tmp_artist != None and tmp_artist != current_artist:
                    item.setArtist(tmp_artist)
                if tmp_album != None and tmp_album != current_album:
                    item.setAlbum(tmp_album)
                if tmp_albumartist != None and (tmp_albumartist !=
                        current_albumartist):
                    item.setArtist(tmp_albumartist, 'TPE2')
                if tmp_genre != None and tmp_genre != current_genre:
                    item.setGenre(tmp_genre)
                if tmp_track != None and tmp_track != current_track:
                    item.setTitle(tmp_track)
                if tmp_disc != None and tmp_disc != current_disc:
                    item.setDiscNum(tmp_disc, None)
                if tmp_year != None and tmp_year != current_year:
                    try:
                        int(tmp_year)
                        item.setDate(tmp_year, None)
                    except ValueError:
                        print 'Invalid Year'
                if tmp_comment != None and tmp_comment != current_comment:
                    item.removeComments()
                    item.addComment(tmp_comment)
                # write changes
                item.update(eyeD3.ID3_V2_4)
                # reload new tags
                self.loadtags(self.current_files)

    def loadtags(self, *args):
        """ connect chosen files with tags """
        self.loadlists()
        self.clearopenfiles()
        # pull tags for each music file
        for musicfiles in args[0]:
            try:
                item = eyeD3.Tag()
                item.link(musicfiles)
                item.setVersion(eyeD3.ID3_V2_4)
                item.setTextEncoding(eyeD3.UTF_8_ENCODING)
            except:
                print 'Tag error: ' + musicfiles
                item = None
            # pull tag info per item
            if item:
                tmp_title = item.getTitle()
                if tmp_title == 'None':
                    tmp_title = None
                tmp_artist = item.getArtist('TPE1')
                if tmp_artist == 'None':
                    tmp_artist = None
                tmp_album = item.getAlbum()
                if tmp_album == 'None':
                    tmp_album = None
                tmp_albumartist = item.getArtist('TPE2')
                if tmp_albumartist == 'None':
                    tmp_albumartist = None
                tmp_genre = str(item.getGenre())
                if ')' in tmp_genre:
                    tmp_genre = tmp_genre.split(')')[1]
                if tmp_genre == 'None':
                    tmp_genre = None
                tmp_track = str(item.getTrackNum()[0])
                if '/' in tmp_track:
                    tmp_track = tmp_track.split('/')[0]
                if len(tmp_track) == 1:
                    tmp_track = '0' + str(tmp_track)
                if len(tmp_track) > 2:
                    tmp_track = tmp_track[:2]
                tmp_disc = str(item.getDiscNum()[0])
                if '/' in tmp_disc:
                    tmp_disc = tmp_disc.split('/')[0]
                if len(tmp_disc) == 2:
                    tmp_disc = tmp_disc[-1]
                tmp_year = str(item.getYear())
                if len(tmp_year) != 4:
                    for items in YR_SPLIT:
                        if items in tmp_year:
                            tmp_year = tmp_year.split(items)
                    for items in tmp_year:
                        if len(items) == 4:
                            tmp_year = items
                if tmp_year == 'None':
                    tmp_year = None
                tmp_comment = item.getComment()
                if tmp_comment == 'None':
                    tmp_comment = None
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
                if not types[0]:
                    self.uibuttons[count][1].set_text('')
                else:
                    self.uibuttons[count][1].set_text('[Multiple]')
            count = count + 1
        return

    def loadselection(self, *args):
        """ load files into tag editor """
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
            new_dir = self.current_dir + '/' + model[treeiter][0]
        if os.path.isdir(new_dir):
            self.listfolder(new_dir)
        return

    def gohome(self, *args):
        """ go to the defined home folder """
        self.clearopenfiles()
        self.listfolder(self.homefolder)

    def goback(self, *args):
        """ go back the the previous directory """
        back_dir = os.path.dirname(self.current_dir)
        self.clearopenfiles()
        self.listfolder(back_dir)

    def clearopenfiles(self):
        """ clear the tags ui when changing folder """
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
            test_dir = os.path.isdir(self.current_dir + '/' + items)
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
            test_file = os.path.isfile(self.current_dir + '/' + items)
            test_ext = items[(items.rfind('.')):] in MEDIA_TYPES
            if not items[0] == '.' and test_file and test_ext:
                self.contentlist.append([items])
        return


if __name__ == "__main__":
    Gdk.threads_init()
    MYTAG()
