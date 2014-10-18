# -** coding: utf-8 -*-
'''
@author Jiajun Huang
created at 2013/11/14
'''

import storage 
from task import crawl_one
from w_thread import WThread

import time
from Queue import Queue
from random import randint

qsize = 1000
queue = Queue(qsize)


def queue_generate(file_name):
    '''
    read weibo users from file and put them into the queue
    '''
    uid_file = open(file_name, 'r')
    for each_line in uid_file:
        uid = each_line.split()[0] #the first section of each line should be a uid
        queue.put(uid)
    uid_file.close()

def worker(weibo_user_type):
    '''
    workers who crawl weibo users one by one util the Queue is empty
    '''
    while queue.empty() is False:
        uid = queue.get()

        crawl_one(uid, weibo_user_type)

        time.sleep(randint(1, 30))

def master(weibo_user_type=1001):
    n_threads = 5
    threads = []
    for i in range(n_threads):
        t = WThread(worker, [weibo_user_type], 'workor' + str(i))
        threads.append(t)

    for t in threads:
        t.setDaemon(True)

    for t in threads:
        t.start()
        time.sleep(5)

    for t in threads:
        t.join()
    
    log.info("All done")

def main():
    #queue_generate('famous.txt')
    #queue_generate('media.txt')
    #master(1002)
    queue_generate('a_small_list.txt')
    master()


if __name__ == '__main__':
    main()


