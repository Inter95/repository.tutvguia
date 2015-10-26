# -*- coding: utf-8 -*-
'''
    Torrenter plugin for XBMC
    Copyright (C) 2012 Vadim Skorba
    vadim.skorba@gmail.com

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
'''

import urllib
import re
import sys
#import HTMLParser

import SearcherABC


class ExtraTorrent(SearcherABC.SearcherABC):
    '''
    Weight of source with this searcher provided.
    Will be multiplied on default weight.
    Default weight is seeds number
    '''
    sourceWeight = 1

    '''
    Relative (from root directory of plugin) path to image
    will shown as source image at result listing
    '''
    searchIcon = '/resources/searchers/icons/ExtraTorrent.png'

    '''
    Flag indicates is this source - magnet links source or not.
    Used for filtration of sources in case of old library (setting selected).
    Old libraries won't to convert magnet as torrent file to the storage
    '''

    @property
    def isMagnetLinkSource(self):
        return True

    '''
    Main method should be implemented for search process.
    Receives keyword and have to return dictionary of proper tuples:
    filesList.append((
        int(weight),# Calculated global weight of sources
        int(seeds),# Seeds count
        str(title),# Title will be shown
        str(link),# Link to the torrent/magnet
        str(image),# Path/URL to image shown at the list
    ))
    '''

    def getTorrentFile(self, url):
        url=url.replace('download', 'torrent')
        headers = [('User-Agent',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 YaBrowser/14.10.2062.12061 Safari/537.36'),
           ('Referer', 'http://extratorrent.cc/'), ('Accept-encoding', 'gzip'), ]
        content = self.makeRequest(url, headers=headers)
        ok=re.compile('(magnet:.+?)"').findall(content)
        if len(ok)>0:
            return ok[0]

    def search(self, keyword):
        filesList = []
        #pars = HTMLParser.HTMLParser()
        url = "http://extratorrent.cc/search/?search=%s&new=1&x=0&y=0" % (urllib.quote_plus(keyword))
        headers = [('User-Agent',
                    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 YaBrowser/14.10.2062.12061 Safari/537.36'),
                   ('Referer', 'http://extratorrent.cc/'), ('Accept-encoding', 'gzip'), ]
        response = self.makeRequest(url, headers=headers)
        self.cookieJar.save(ignore_discard=True)

        if None != response and 0 < len(response):
            #print response
            dat = re.compile(
                r'''<a href="/torrent_(download/\d+).+? title="Download (.+?) torrent".+?</a>.+?</td><td>(.+?)</td>.+?<td class="sy">(.+?)</td>.+?<td class="ly">(.+?)</td>''',
                re.DOTALL).findall(response)
            for (link, title, size, seeds, leechers) in dat:
                size = size.replace('&nbsp;', ' ')
                seeds=seeds.replace('---', '0')
                leechers=leechers.replace('---', '0')
                image = sys.modules["__main__"].__root__ + self.searchIcon
                link = 'http://extratorrent.cc/'+link
                filesList.append((
                    int(int(self.sourceWeight) * int(seeds)),
                    int(seeds), int(leechers), size,
                    self.unescape(self.stripHtml(title)),
                    self.__class__.__name__ + '::' + link,
                    image,
                ))
        return filesList