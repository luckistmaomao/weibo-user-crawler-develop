# -*- coding: utf-8 -*-
import sys
import os
import re
import operator
import itertools
from os import listdir
from time import sleep
from time import time
from collections import Counter
from collections import defaultdict
try:
	import jieba
	#import ltpservice
	from pymongo import MongoClient
	from conf import DBNAME,DBHOST,DBPORT

except ImportError:
	print >> sys.stderr
	print 'importError'


def connect_mongodb(dbhost=DBHOST,dbport=DBPORT,dbname=DBNAME):

	try:
		client = MongoClient(dbhost,dbport)
		db = client[dbname]
	except:
		print 'cannot connect'
	return db

def remove_newline(string):

	regex = r'[\r]?\n'
	reobj = re.compile(regex)
	return reobj.sub('',string)

def remove_mark(string):
	
	regex = r'(http://t.cn/.*)|(//@.*:)'
	reobj = re.compile(regex)
	return reobj.sub('',string)

def get_stopwords(filename='stopwords_1.txt'):
	
	with open(filename,'r') as f:
		stopwords_list = f.readlines()
	stopwords_list = [remove_newline(word) for word in stopwords_list]
	return stopwords_list

STOPWORDS_LIST = get_stopwords()
#def ltp_service(string,email="yuanhang.nju@gmail.com",token="2xugGBsI"):

#	stopwords_list = get_stopwords()
#	CHI_WORD_LENGTH =6
#	client = ltpservice.LTPService("%s:%s" % (email,token))
#	ltml = ltpservice.LTML()
#	string = string.encode('utf8')
#	ltml.build(string)

#	result = client.analysis(ltml,ltpservice.LTPOption.NE)
#	seg_list = [word.encode("utf8") for word in result.get_words(0,0)]
#	seg_list = filter(None,seg_list)

#	string_to_file = ' '.join([word for word in seg_list if word not in stopwords_list and len(word)>=CHI_WORD_LENGTH])
#	pos_to_file = ' '.join([pos.encode("utf8") for pos in result.get_pos(0,0)])
#	nameentity_to_file = ' '.join([e.get('cont').encode("utf8") for e in result.dom[1][0][0].finall('word') if e.get('ne') !='O']) 
	
#	return (string_to_file,pos_to_file,nameentity_to_file)

def jieba_service(string):
	
	CHI_WORD_LENGTH = 4
	string = string.encode("utf8")
	seg_list = jieba.cut(string)
	seg_list = [word.encode('utf-8') for word in seg_list]
	seg_list = filter(None,seg_list)
	string_to_file = None
	string_to_file = ' '.join([word for word in seg_list if word not in STOPWORDS_LIST and len(word)>=CHI_WORD_LENGTH])

	return string_to_file

def get_friends(current_dir,read_db,collections,uid,filename='friends.txt'):
	
	cursor = read_db[collections].find({"uid":uid})
	friends_list = []
	for tweet in cursor:
		try:
			content = tweet["content"]
			friends = re.findall(r'//@(.+?):',content)
			friends_list.extend(friends)
		except:
			pass
	
	friends_list = [friend.encode("utf8") for friend in friends_list]
	friends_list = filter(None,friends_list)
	friends_count_dict = Counter(friends_list)
	sorted_friends_dict = sorted(friends_count_dict.iteritems(),key=operator.itemgetter(1))
	
	friends_to_file = ''
	for item in sorted_friends_dict:
		friends_to_file += (item[0]+' '+str(item[1])+'\n')
	
	with open(current_dir+'/'+filename,'w') as f:
		f.write(friends_to_file)

def get_data(read_db,collections,uid):
	
	string_list = []
	cursor = read_db[collections].find({"uid":uid})
	for tweet in cursor:
		content = tweet["content"]
		content = remove_mark(content)
		if content:
			string_to_file = jieba_service(content)
			if string_to_file:
				forwards_num = tweet["n_forwards"]
				comments_num = tweet["n_comments"]
				string_list.append(str(forwards_num)+' '+str(comments_num)+' '+string_to_file)
	return string_list

def get_wordweight(read_db,collections,uid):
	
	
	lines = get_data(read_db,collections,uid)
	lines = [line.split(' ') for line in lines]
	forwards_comments_list = [map(int,line[0:2]) for line in lines]
	forwards_comments_sum_list = [sum(element) for element in zip(*forwards_comments_list)]
	try:
		forwards_sum = forwards_comments_sum_list[0]
		comments_sum = forwards_comments_sum_list[1]
		#print 'forwards_sum',forwards_sum
		#print 'comments_sum',comments_sum
		forwards_comments_sum  = forwards_sum+comments_sum
	except:
		pass

	
	wordweight_list_dict = defaultdict(list)
	tweet_count = len(lines)
	for line in lines:
		tweet_weight = (int(line[0])+int(line[1])+1)*1.0/(forwards_comments_sum+tweet_count)
		wordslist = line[2:]
		wordscount_dict = Counter(wordslist)
		max_word_count = wordscount_dict.most_common(1)[0][1]
		for word in wordslist:
			word_weight = (wordscount_dict[word]*1.0/max_word_count)*tweet_weight
			wordweight_list_dict[word].append(word_weight)
	
	wordweight_dict = defaultdict(int)
	for word in wordweight_list_dict:
		value = sum(wordweight_list_dict[word])
		wordweight_dict[word] = value
	
	sorted_tuple = sorted(wordweight_dict.iteritems(),key=operator.itemgetter(1))
	string_list = []
	for item in sorted_tuple:
		word_tuple = (item[0],item[1])
		string_list.append(word_tuple)
	return string_list	

if __name__ == "__main__":
	collections = 'micro_blog'
	uid = "3121700831" 
	read_db = connect_mongodb()
	from time import time
	start = time()
	get_wordweight(read_db,collections,uid)
	end = time()
	print end-start
