# -*- coding: utf-8 -*-
'''
    @author Jiajun Huang
    Created on 2013/10/17
'''
import yaml

conf_file = open("weibo.yaml", 'r')
conf_dic = yaml.load(conf_file)
conf_file.close()

DBNAME = conf_dic['db']['dbname']
DBHOST = conf_dic['db']['host']
DBPORT = conf_dic['db']['port']

USERNAME = conf_dic['login'][0]['username']
PASSWORD = conf_dic['login'][0]['password']
USERNAME = str(USERNAME)

COOKIE_FILE = conf_dic['cookie_file']

if __name__ == '__main__':
    print DBNAME, DBHOST, DBPORT
    print USERNAME, PASSWORD, COOKIE_FILE

