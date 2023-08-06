"""
PieTunes is an abstraction of Apple's Scripting Bridge API for iTunes.
Copyright (C) 2018  Brian Farrell

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: brian.farrell@me.com
"""


from enum import IntEnum


class iTunesESrA(IntEnum):
    ALBUMS = 0x6b53724c
    ALL = 0x6b416c6c
    ARTISTS = 0x6b537252
    COMPOSERS = 0x6b537243
    DISPLAYED = 0x6b537256
    SONGS = 0x6b537253
