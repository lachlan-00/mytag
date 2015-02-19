#!/usr/bin/env python
#-*- coding: utf-8 -*-

""" mytagworker
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

import os
import shutil
import threading

import mytagstrings

from gi.repository import Gtk

from xdg.BaseDirectory import xdg_config_dirs

# Get OS type
OS = os.name

# Acceptable media files
MEDIA_TYPES = ['.m4a', '.flac', '.ogg', '.mp2', '.mp3', '.wav', '.spx']

# Possible date splitters to get the year
YR_SPLIT = ['-', '/', '\\']

# list of tags the program will replace with the correct tag value
MUSIC_TAGS = ['%artist%', '%albumartist%', '%album%', '%year%',
              '%title%', '%disc%', '%track%', '%genre%', '%comment%']

if OS == 'nt':
    SLASH = '\\'
    UI_FILE = "./main.ui"
    CONFIG = './mytag.conf'
    ICON_DIR = './gnome/'
    USERHOME = os.getenv('userprofile')
elif OS == 'posix':
    SLASH = '/'
    UI_FILE = "/usr/share/mytag/main.ui"
    CONFIG = xdg_config_dirs[0] + '/mytag.conf'
    ICON_DIR = '/usr/share/icons/gnome/'
    USERHOME = os.getenv('HOME')

class WorkerThread(threading.Thread):
    """ run a separate thread to the ui """
    def __init__(self, notify_window):
        """Init Worker Thread Class."""
        super(WorkerThread, self).__init__()
        self._notify_window = notify_window
        self._want_abort = 0
        self._stop = threading.Event()
        self.setDaemon(True)
        self.returntext = None
        self.source = None
        self.files = None
        self.destin = None
        self.destinformat = None
        self.backupdir = None
        self.stoponerrors = None
        self.movemedia = None
        self.stopprocess = None
        self.start()
        return None

    def stop(self):
        """ stop the thread """
        self._stop.set()

    def stopped(self):
        """ Set Stop """
        return self._stop.isSet()

    def run(self, *args):
        """ run file organisation in a background thread """
        self.returntext = True
        self.source = None
        self.files = None
        self.destin = None
        self.destinformat = None
        self.stoponerrors = None
        self.movemedia = None
        if args:
            if args[0]:
                self.source = args[0]
            if args[1]:
                self.files = args[1]
            if args[2]:
                self.destin = args[2]
            if args[3]:
                self.destinformat = args[3].lower()
            if args[4]:
                if args[4] == 'True':
                    self.stoponerrors = True
                else:
                    self.stoponerrors = False
            if args[5]:
                if args[5] == 'True':
                    self.movemedia = True
                else:
                    self.movemedia = False
            if self.destin:
                self.backupdir = os.path.normpath(self.destin + '/BACKUP/')
            self.foldersearch(self.source)
        return self.returntext

    def foldersearch(self, folder):
        """ Start searching the source folder looking for music  """
        self.stopprocess = False
        try:
            tmpsort = os.listdir(folder)
            tmpsort.sort(key=lambda y: y.lower())
        except OSError:
            self.returntext = folder
            return False
        except TypeError:
            try:
                print(folder)
            except UnicodeEncodeError:
                pass
            self.returntext = folder
            return False
        # search for files and folders in the current dir
        for items in tmpsort:
            while Gtk.events_pending():
                Gtk.main_iteration()
            if not self.stopprocess:
                try:
                    path = os.path.normpath((folder).decode('utf-8') + u'/' +
                                            (items).decode('utf-8'))
                except UnicodeEncodeError:
                    path = os.path.normpath(folder + '/' + items)
                pathext = path[(path.rfind('.')):].lower()
                if os.path.isdir(path) and os.listdir(path) == []:
                    tmp_dir = path
                    # remove empty folders and search backwards for more
                    while os.listdir(tmp_dir) == []:
                        os.rmdir(tmp_dir)
                        tmp_dir = os.path.split(tmp_dir)[0]
                if os.path.isdir(path) and (self.backupdir !=
                                            os.path.dirname(path)):
                    # remove '.mediaartlocal' folders
                    if os.path.basename(path) == '.mediaartlocal':
                        for items in os.listdir(path):
                            try:
                                os.remove(os.path.join(path + u'/' + items))
                            except OSError:
                                self.returntext = 'permissions'
                                self.stopprocess = True
                                return
                        try:
                            os.rmdir(path)
                        except OSError:
                            pass
                    else:
                        # search subfolder for media
                        try:
                            print(path)
                        except UnicodeEncodeError:
                            pass
                        self.foldersearch(path)
                elif os.path.isfile(path) and pathext in MEDIA_TYPES:
                    # organise media file
                    self.organisefiles(path)
        return

    def organisefiles(self, files):
        """ sort media when found """
        # set output path and fill variables with the tag value
        stringtest = False
        currentdestin = os.path.normpath(self.destin + u'/' +
                                         self.destinformat)
        currentdestin = mytagstrings.fill_string(files, currentdestin)
        # ignore missing tags
        if not currentdestin:
            return 'permissions'
        for tags in MUSIC_TAGS:
            # if a tag variable is found in the output do not continue
            if tags in currentdestin:
                stringtest = True
                if self.stoponerrors:
                    self.returntext = [tags, os.path.dirname(files)]
                    self.stopprocess = True
                return False
        # remove bad characters for windows paths.
        if OS == 'nt':
            currentdestin = mytagstrings.remove_utf8(currentdestin)
        # Move files if the processed destination is different.
        if not files == currentdestin:
            while Gtk.events_pending():
                Gtk.main_iteration()
            # create a backup when conflicts are found
            if os.path.isfile(currentdestin):
                backupdestin = os.path.normpath(self.backupdir + '/' +
                                                self.destinformat)
                backup = mytagstrings.fill_string(files, backupdestin)
                if os.path.isfile(backup) and not files == backup:
                    count = 0
                    tmp_path = backup
                    tmpext = tmp_path.rfind('.')
                    while os.path.isfile(backup):
                        backup = tmp_path
                        backup = (tmp_path[:(tmpext)] +
                                  str(count) + tmp_path[(tmpext):])
                        count = count + 1
                # update destination to the non-conflicting destination
                currentdestin = backup
            if not os.path.isfile(currentdestin) and not stringtest:
                # create directoy for output file if not found
                if not os.path.isdir(os.path.dirname(currentdestin)):
                    os.makedirs(os.path.dirname(currentdestin))
                # move file and run cleanup
                try:
                    shutil.move(files, currentdestin)
                except OSError:
                    self.returntext = 'permissions'
                    self.stopprocess = True
                    return
                self.folder_cleanup(files, currentdestin)
        return

    def folder_cleanup(self, sourcedir, destindir):
        """ remove empty folders and move non-media with your media file """
        if not os.path.isdir(sourcedir):
            sourcedir = os.path.dirname(sourcedir)
        if not os.path.isdir(destindir):
            destindir = os.path.dirname(destindir)
        if not os.listdir(sourcedir) == []:
            tmp_dir = os.listdir(sourcedir)
            tmp_dir.sort(key=lambda y: y.lower())
            found_media = False
            # check for left over media files
            for files in tmp_dir:
                if not os.path.isdir((sourcedir + '/' + files) and not
                                     (destindir == sourcedir)):
                    filelist = files[(files.rfind('.')):].lower()
                    if filelist in MEDIA_TYPES:
                        found_media = True
            if self.movemedia:
                # move non-media when no other media files are in the folder
                for files in tmp_dir:
                    while Gtk.events_pending():
                        Gtk.main_iteration()
                    filelist = files[(files.rfind('.')):].lower()
                    if not found_media and not os.path.isdir(sourcedir +
                                                             '/' + files):
                        if not filelist in MEDIA_TYPES:
                            mvdest = destindir + '/' + files
                            mvsrc = sourcedir + '/' + files
                            # move non-media files when no more music found.
                            shutil.move(mvsrc, mvdest)
        # Remove empty folders, if you have moved out the last file.
        if os.listdir(sourcedir) == []:
            tmp_dir = sourcedir
            while os.listdir(tmp_dir) == []:
                os.rmdir(tmp_dir)
                tmp_dir = os.path.dirname(tmp_dir)
        return
