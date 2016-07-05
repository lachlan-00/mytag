#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" mytagstrings
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
import sys

from gi.repository import Gtk

# Python 2 Tag support
if sys.version[0] == '2':
    # python-eyeD3 required for editing and loading tags
    try:
        import eyed3 as eyeD3

        TAG_SUPPORT = True
    except ImportError:
        try:
            import eyeD3

            TAG_SUPPORT = True
        except ImportError:
            eyeD3 = None
            TAG_SUPPORT = False

# quit if using python3
if sys.version[0] == '3':
    # look at using mutagen to support python3 instead of eyed3
    # import mutagen
    raise Exception('not python3 compatible, please use python 2.x')

# non-ascii characters to replace to fat/ntfs/windows support
URL_ASCII = ('%', "#", ';', '"', '<', '>', '?', '[', '\\', "]", '^', '`', '{',
             '|', '}', '€', '‚', 'ƒ', '„', '…', '†', '‡', 'ˆ', '‰', 'Š', '‹',
             'Œ', 'Ž', '‘', '’', '“', '”', '•', '–', '—', '˜', '™', 'š', '›',
             'œ', 'ž', 'Ÿ', '¡', '¢', '£', '¥', '|', '§', '¨', '©', 'ª', '«',
             '¬', '¯', '®', '¯', '°', '±', '²', '³', '´', 'µ', '¶', '·', '¸',
             '¹', 'º', '»', '¼', '½', '¾', '¿', 'À', 'Á', 'Â', 'Ã', 'Ä', 'Å',
             'Æ', 'Ç', 'È', 'É', 'Ê', 'Ë', 'Ì', 'Í', 'Î', 'Ï', 'Ð', 'Ñ', 'Ò',
             'Ó', 'Ô', 'Õ', 'Ö', 'Ø', 'Ù', 'Ú', 'Û', 'Ü', 'Ý', 'Þ', 'ß', 'à',
             'á', 'â', 'ã', 'ä', 'å', 'æ', 'ç', 'è', 'é', 'ê', 'ë', 'ì', 'í',
             'î', 'ï', 'ð', 'ñ', 'ò', 'ó', 'ô', 'õ', 'ö', '÷', 'ø', 'ù', 'ú',
             'û', 'ü', 'ý', 'þ', 'ÿ', '¦', ':', '*')


def remove_utf8(string):
    """ Function to help with FAT32 devices """
    count = 0
    # replace disallowed characters with '_'
    while count < len(URL_ASCII):
        try:
            string = string.replace(URL_ASCII[count], '_')
        except UnicodeDecodeError:
            pass
        count += 1
    return string


def fill_string(files, destin):
    """ function to replace the variables with the tags for each file """
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
        # Tag error
        item = None
    # pull tag info for the current item
    if item:
        tmp_title = item.getTitle()
        if tmp_title == 'None':
            tmp_title = None
        if tmp_title:
            tmp_title = tmp_title.replace('/', '_')
        tmp_artist = item.getArtist('TPE1')
        if tmp_artist == 'None':
            tmp_artist = None
        if tmp_artist:
            tmp_artist = tmp_artist.replace('/', '_')
        tmp_album = item.getAlbum()
        if tmp_album == 'None':
            tmp_album = None
        if tmp_album:
            tmp_album = tmp_album.replace('/', '_')
        tmp_albumartist = item.getArtist('TPE2')
        if tmp_albumartist == 'None':
            tmp_albumartist = None
        if tmp_albumartist:
            tmp_albumartist = tmp_albumartist.replace('/', '_')
        try:
            tmp_genre = str(item.getGenre())
        except eyeD3.tag.GenreException:
            tmp_genre = None
        if tmp_genre == 'None':
            tmp_genre = None
        if tmp_genre:
            tmp_genre = tmp_genre.replace('/', '_')
            if ')' in tmp_genre:
                tmp_genre = tmp_genre.split(')')[1]
        tmp_track = str(item.getTrackNum()[0])
        if tmp_track == 'None':
            tmp_track = None
        if tmp_track:
            if '/' in tmp_track:
                tmp_track = tmp_track.split('/')[0]
            if len(tmp_track) == 1:
                tmp_track = '0' + str(tmp_track)
            if len(tmp_track) > 2:
                tmp_track = tmp_track[:2]
        tmp_disc = str(item.getDiscNum()[0])
        if tmp_disc == 'None':
            tmp_disc = None
        if tmp_disc:
            if '/' in tmp_disc:
                tmp_disc = tmp_disc.split('/')[0]
            if len(tmp_disc) == 2 and tmp_disc <= 9:
                tmp_disc = tmp_disc[-1]
        tmp_year = item.getYear()
        if tmp_year == 'None':
            tmp_year = None
        tmp_comment = item.getComment()
        if tmp_comment == 'None':
            tmp_comment = None
        if tmp_comment:
            tmp_comment = tmp_comment.replace('/', '_')
        # replace temp strings with actual tags
        if tmp_title:
            destin = destin.replace('%title%', tmp_title)
        if tmp_albumartist:
            destin = destin.replace('%albumartist%', tmp_albumartist)
        else:
            destin = destin.replace('%albumartist%', '%artist%')
        if tmp_artist:
            destin = destin.replace('%artist%', tmp_artist)
        if tmp_album:
            destin = destin.replace('%album%', tmp_album)
        if tmp_genre:
            destin = destin.replace('%genre%', tmp_genre)
        if tmp_track:
            destin = destin.replace('%track%', tmp_track)
        if tmp_disc:
            destin = destin.replace('%disc%', tmp_disc)
        if tmp_year:
            destin = destin.replace('%year%', tmp_year)
        if tmp_comment:
            destin = destin.replace('%comment%', tmp_comment)
        destin = destin + files[(files.rfind('.')):]
        while Gtk.events_pending():
            Gtk.main_iteration()
        return destin
    return
