# -*- coding: utf-8 -*-
'''
modified by yuzt<zhenting.yu@gmail.com> @2014.9.27

@author: Huang Jiajun
created on 2013/10/24
'''

import urllib2
from StringIO import StringIO
import gzip
import socket
import traceback
import os

from conf import USERNAME, PASSWORD, COOKIE_FILE
from weibo_login import do_login


class Cookie(object):
    def __init__(self,username,password,cookiefile):
        self.username = username
        self.password = password
        self.cookiefile = cookiefile
        self.login = False

    def get_cookie(self):
        cookie = {}
        with open(cookiefile) as f:
            lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            space_index = line.find(' ')
            pair = line.split(';')[0][space_index:]
            pair = pair.replace('\"','')
            equal_index = pair.find('=')
            key = pair[:equal_index]
            value = pair[equal_index+1:]
            cookie[key] = value
        return cookie


def urlfetch(url):
    '''
    open the url and return html, may raise URLError
    '''
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    flag = False
    while True:
        try:
            response = urllib2.urlopen(request,timeout=7)
            break
        except socket.timeout:
            print "socket time out"
        except urllib2.URLError,e:
            print e.reason
            if isinstance(e.reason,socket.timeout):
                print "fetch "+url+" time out"
            else:
                print e.reason
                flag = True
                break
        except:
            traceback.format_exc()

    if flag:
        raise urllib2.URLError("raise other exception")
                
    try:
        if response.info().get('Content-Encoding') == 'gzip':
            #print 'gzip'
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
            html = data
        else:
            html = response.read()
    except:
        raise urllib2.URLError('socket time out')

    COOKIE_OUTOFDATE_ERROR = r'passport.weibo.com/wbsso/login?ssosavestate'
    if COOKIE_OUTOFDATE_ERROR in html:
        print "cookie out of time"
        if not os.path.exists(COOKIE_FILE):
            time.sleep(10)
            raise urllib2.URLError("cookie out of time")
        try:
            os.remove(COOKIE_FILE)
            do_login(USERNAME,PASSWORD,COOKIE_FILE)
            time.sleep(3)
        except:
            pass
        raise urllib2.URLError("cookie out of time")

    return html

def test():
    pass

if __name__ == "__main__":
    test()
