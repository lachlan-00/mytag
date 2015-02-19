#!/usr/bin/env python
#-*- coding: utf-8 -*-

""" remove_utf8
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
        count = count + 1
    return string
