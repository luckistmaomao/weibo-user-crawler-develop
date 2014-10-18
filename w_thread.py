# -*- coding: utf-8 -*-
'''
@author Jiajun Huang
created at 2013/11/1
'''

import threading
from time import ctime


class WThread(threading.Thread):
    '''
    A sub class of Thread
    '''
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def getResult(self):
        return self.res

    def run(self):
        print '-starting', self.name, 'at:', ctime()
        self.res = apply(self.func, self.args)
        print self.name, 'finished at:', ctime()


