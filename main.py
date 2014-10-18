#coding:utf-8
"""
@author yuzt
created on 2014.8.8
"""

import Queue
import time
import threading
import random
import traceback
try:
    import storage
    from storage import WeiboUser,WaitCrawlUser,MicroBlog
    from task import crawl_one,add_crawl
    from multithreads import Threadpool
except ImportError:
    s = traceback.format_exc()
    print s

class WaitCrawlUserListManager(threading.Thread):
    """
    维护等待完整爬取的用户队列
    """
    def __init__(self,wait_user_queue):
        threading.Thread.__init__(self)
        self.weibo_user_set = self.get_weibo_user_set()
        self.wait_user_queue = wait_user_queue

    def run(self):
        while True:
            for wait_crawl_user in WaitCrawlUser.objects:
                uid = wait_crawl_user.uid
                if uid in self.weibo_user_set:
                    continue
                self.weibo_user_set.add(uid)
                self.wait_user_queue.put(uid)
            time.sleep(60)

    def get_weibo_user_set(self):
        user_set = set()
        for weibo_user in WeiboUser.objects:
            user_set.add(weibo_user.uid)
        return user_set


class WeiboUserListManager(threading.Thread):
    """
    维护增量爬取的用户队列
    """
    def __init__(self,weibo_user_queue):
        threading.Thread.__init__(self)
        self.weibo_user_queue = weibo_user_queue

    def run(self):
        while True:
            for weibo_user in WeiboUser.objects:
                uid = weibo_user.uid
                self.weibo_user_queue.put(uid)
                sleep_time = random.randint(10,20) 
                time.sleep(sleep_time)


def main():
    wait_pool = Threadpool(4,crawl_one)
    with open('IDs.txt') as f:
        IDs = [line.strip() for line in f.xreadlines()]
    user_set = set()
    for weibo_user in WeiboUser.objects:
        user_set.add(weibo_user.uid)


    start = 0
    length = len(IDs) 
    
    for ID in IDs[:]:
        if ID not in user_set:
            wait_pool.user_queue.put(ID)

    #add_pool = Threadpool(5,add_crawl) 
    #wait_crawl_user_list_manager = WaitCrawlUserListManager(wait_pool.user_queue)
    #wait_crawl_user_list_manager.start()
    
    #weibo_user_list_manager = WeiboUserListManager(add_pool.user_queue)
    #weibo_user_list_manager.start()

if __name__ == "__main__":
    main()
