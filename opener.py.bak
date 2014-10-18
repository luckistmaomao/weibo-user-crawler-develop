# -*- coding: utf-8 -*-
'''
@author: Huang Jiajun
created on 2013/10/24
'''

import urllib2
from StringIO import StringIO
import gzip


def urlfetch(url):
    '''
    open the url and return html, may raise URLError
    '''
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)
    if response.info().get('Content-Encoding') == 'gzip':
        #print 'gzip'
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
        return data
    else:
        return response.read()
