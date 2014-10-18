# -*- coding: utf-8 -*-
'''
@author Jiajun Huang
created at 2013/11/1
'''

import storage
from task import crawl_one
from w_thread import WThread

import time
from Queue import Queue
from random import randint

qsize = 1000
queue = Queue(qsize)    
seeds = ['2584784292', '2595656694', '1991194723', '1788911247']
for seed in seeds:
    queue.put(seed)

def worker():
    '''
    worker function that crawl weibo one user by one user
    '''
    while True:
    #for i in range(10):
        uid = queue.get()
        print 'start uid: ' + uid
        follows = crawl_one(uid)
        print 'finish uid: ' + uid
        for follow in follows:
            if len(storage.WeiboUser.objects(uid=follow.uid)) == 0 and not queue.full():
                    queue.put(follow.uid)
        time.sleep(randint(1, 10))

def main():
    n_threads = 4
    threads = []
    for i in range(n_threads):
        t = WThread(worker, [], 'work' + str(i))
        threads.append(t)
    
    for t in threads:
        t.setDaemon(True)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print 'all Done'

if __name__ == '__main__':
    main()

