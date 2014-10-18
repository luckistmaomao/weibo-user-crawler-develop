#-*- coding: utf-8 -*-

'''
@author: Jiajun Huang
created at 2013/12/6
'''

import logging

class Logger():
    def __init__(self, logfile, loggername):
        self.logger = logging.getLogger(loggername)

        self.logger.setLevel(logging.DEBUG) #set logger level to DEBUG

        #create handler for saving log to file
        file_handler = logging.FileHandler(logfile)
        file_handler.setLevel(logging.DEBUG)

        #create handler for printing log on screen
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        #define the format of handlers
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        #add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def getlog(self):
        return self.logger

def test():
    logger = Logger("logs/test.log", "Foo").getlog()
    logger.info("this is a very first testing log")

if __name__ == '__main__':
    test()

