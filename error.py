# -*- coding: utf-8 -*-
'''
    author: Jiajun
    created on 2013.11.15
'''
try:
	import MySQLdb as mdb
	import sys
	from conf import LOGDB, LOGHOST,LOGUSER, LOGPW

except ImportError:
        print >> sys.stderr
	exit()

try:
	con = mdb.connect(LOGHOST, LOGUSER, LOGPW, LOGDB)
except:
	print 'Error connecting MySQL'
	exit()

cur = con.cursor()
cur.execute('CREATE TABLE IF NOT EXIST \
	weibolog(id INT PRIMARY KEY AUTO_INCREMENT,errortype INT, \
			kw VARCHAR(25), page INT, time DATETIME)')

class ERRORTYPE(object):
	URLERROR = 0
	LOGINERROR = 0
	VERIFICATIONERROR = 2


class errorlog(object):
	@staticmethod
	def urlerror(self, kw, page, time):
		cur.execute('INSERT INTO searchlog(errortype,kw,page,time) \
				VALUES(ERRORTYPE.URLERROR, kw, page, time)')

	@staticmethod
	def loginerror(self, kw, page, time):
		cur.execute('INSERT INTO searchlog(errortype,kw,page,time) \
				VALUES(ERRORTYPE.LOGINERROR, kw, page, time)')

	@staticmethod
	def verificationerror(self, kw, page, time):
		cur.execute('INSERT INTO searchlog(errortype,kw,page,time) \
			VALUES(ERRORTYPE.VERIFICATIONERROR, kw, page, time)')


if __name__ == '__main__':
	
	pass

