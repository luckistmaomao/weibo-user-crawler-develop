# -*- coding: utf-8 -*-
'''
modified by @yuzt on 2014.8.13

@author Jiajun Huang
created on 2013/10/24
'''
import traceback
import time
import urllib
import urllib2
import json
import os
from random import randint
import datetime
import re
import random
try:
    from weibo_login import login
    from conf import USERNAME, PASSWORD, COOKIE_FILE
    from page_parser import parse_user_profile, parse_follow, parse_mblog,\
             parse_json
    from opener import urlfetch
    from errors import UnsuspectedPageStructError, JsonDataParsingError
    from logger import Logger
    from errors import UnsuspectedPageStructError, JsonDataParsingError, URLError
    import storage
except ImportError:
    s = traceback.format_exc()
    print s

MAXTIMES2TRY = 3
MAXSLEEPINGTIME = 20

#log support
if not os.path.exists('logs'):
    os.mkdir('logs')
log = Logger("logs/routine.log", "RoutineLogger").getlog()
event_logger = Logger("logs/events.log", "EventLogger").getlog()
error_logger = Logger("logs/errors.log","ErrorLogger").getlog()

def get_info(uid, weibo_user_type=1001):
    '''
    get a weibo-user's information
    `uid`: uid of this user
    `weibo_user_type`: 1001 stands for normal users while 1002 stands for media users
    return: UserInfo
    '''
    if not os.path.exists(COOKIE_FILE):
        time.sleep(random.uniform(5,25))
    if login(USERNAME, PASSWORD, COOKIE_FILE):
        for o_o in range(MAXTIMES2TRY):
            try:
                url = 'http://weibo.com/' + uid + '/info'
                html = urlfetch(url)
            except URLError:
                log.error("URLError! - url: %s" % url)
                time.sleep(randint(1, MAXSLEEPINGTIME))
                continue
            else:
                try:
                    info = parse_user_profile(html, weibo_user_type)
                except UnsuspectedPageStructError:
                    log.error("Unsuspected page structure! - url: %s" % url)
                else:
                    return info
    else:
        log.error("Login fail!")
        try:
            os.remove(COOKIE_FILE)
        except:
            pass

def get_follows(uid, n_follows, followee_or_follower):
    '''
    get a weibo-user's followees or followers
    `uid`: uid of this user
    `n_follows`: number of follows to get 
    `followee_or_follower`: 1-followee, 2-follower
    return: a list of Follow
    '''
    if not os.path.exists(COOKIE_FILE):
        time.sleep(random.uniform(5,25))
    if login(USERNAME, PASSWORD, COOKIE_FILE):
        follows = []
        n_follows = 200 if n_follows > 200 or n_follows is None else n_follows #at most 200   
        n_pages = int(n_follows / 20) + 1 #20 follows per page
        n_pages = n_follows/20 if n_follows%20==0 else (n_follows/20+1)
        for page in range(n_pages):
            for o_o in range(MAXTIMES2TRY):
                try:
                    if followee_or_follower == 1:
                        url = 'http://weibo.com/' + uid + '/follow?page=' + str(page+1)
                    else:
                        url = 'http://weibo.com/' + uid + '/follow?relate=fans&page=' + str(page+1)
                    html = urlfetch(url)
                except URLError:
                    log.error("URLError! - url: %s" % url)
                    time.sleep(randint(1, MAXSLEEPINGTIME))
                    continue
                else:
                    try:
                        follows_on_current_page = parse_follow(html)
                    except UnsuspectedPageStructError:
                        log.error("Unsuspected page structure! - url: %s" % url)
                        try:
                            os.remove(COOKIE_FILE)
                        except:
                            pass
                        if not os.path.exists(COOKIE_FILE):
                            time.sleep(random.uniform(5,25))
                        if login(USERNAME, PASSWORD, COOKIE_FILE) == 0:
                            log.error("Login fail!")
                    else:
                        follows += follows_on_current_page
                        if followee_or_follower == 1:
                            log.info("Followees fetched. - uid: %s - count: %d - page:%d" % (uid, len(follows_on_current_page), page+1))
                        else:
                            log.info("Followers fetched. - uid: %s - count: %d - page:%d" % (uid, len(follows_on_current_page), page+1))
                    break
            time.sleep(randint(1, MAXSLEEPINGTIME))
        return follows
    else:
        log.error("Login fail!")
        try:
            os.remove(COOKIE_FILE)
        except:
            pass
        
def get_mblogs(uid, n_mblogs, domain = None, weibo_user_type=1001,limit=100):
    '''
    get micro-blogs of a weibo-user and save to mongodb
    `uid`: uid of this user 
    `n_mblogs`: number of mblogs to get
    `domain`: domain of this user
    `weibo_user_type`: 1001 stands for normal users while 1002 stands for media users
    return: the number of mblogs actually got
    '''
    mblog_count = 0
    if not os.path.exists(COOKIE_FILE):
        time.sleep(random.uniform(5,25))
    if login(USERNAME, PASSWORD, COOKIE_FILE):
        if n_mblogs is None:
            n_mblogs = 0
        n_pages = int(n_mblogs / 45) #45 mblogs per page
#        n_pages = n_pages if n_pages<limit else limit
        page = 1  #begin from first page
        last_update_time = datetime.datetime(1,1,1)
        while page <= n_pages+1:
            count_on_this_page = 0
            url = ''
            if weibo_user_type == 1001:
                url = 'http://weibo.com/' + uid + '/weibo?page=' + str(page)
            elif weibo_user_type == 1002:
                url = 'http://weibo.com/' + uid + '/mblog?page=' + str(page)
            mblogs = None
            for o_o in range(MAXTIMES2TRY):
                try:
                    html = urlfetch(url)
                except URLError:
                    log.error("URLError! - url: %s" % url)
                    time.sleep(randint(1, MAXSLEEPINGTIME))
                    continue
                else:
                    try:
                        mblogs = parse_mblog(html, uid)
                    except UnsuspectedPageStructError:
                        log.error("Unsuspected page structure! - url: %s" % url)
                    else:
                        break
            if mblogs is not None and len(mblogs) > 0:
                if page == 1:
                    last_update_time = mblogs[0].created_time
                for mblog in mblogs:
                    if len(storage.MicroBlog.objects(mid=mblog.mid)) < 1:
                        mblog.save()
                    count_on_this_page += 1
                #load ajax data
                params = dict()
                params['max_id'] = mblogs[-1].mid
                params['end_id'] = mblogs[0].mid
                params['page'] = str(page)
                params['pre_page'] = str(page)
                params['count'] = str(15)
                params['feed_type'] = 0
                params['__rnd'] = str(int(time.time()*1000))
                params['id'] = domain + uid if domain is not None and uid is not None else None
                params['pagebar'] = '0'
                params['domain'] = domain
                params['script_uri'] = r'/' + uid + r'/weibo'

                url = 'http://weibo.com/p/aj/mblog/mbloglist?' + urllib.urlencode(params)
                #ajax_resp = urlfetch('http://weibo.com/p/aj/mblog/mbloglist?' + urllib.urlencode(params))
                ajax_mblogs = None
                for o_O in range(MAXTIMES2TRY):
                    try:
                        ajax_resp = urlfetch(url)
                    except URLError:
                        log.error("URLError! - url: %s" % url)
                    else:
                        try:
                            ajax_mblogs = parse_json(ajax_resp, uid)
                        except JsonDataParsingError:
                            log.error("No json data to be loaded! - url: %s" % url)
                        except UnsuspectedPageStructError:
                            log.error("Unsuspected page structure! - url: %s" % url)
                        else:
                            break
                if ajax_mblogs is not None and len(ajax_mblogs) > 0:
                    params['max_id'] = ajax_mblogs[-1].mid 
                    params['__rnd'] = str(int(time.time()*1000))
                    params['pagebar'] = '1'

                    url = 'http://weibo.com/p/aj/mblog/mbloglist?' + urllib.urlencode(params)
                    for o_O in range(MAXTIMES2TRY):
                        try:
                            ajax_resp = urlfetch(url)
                        except URLError:
                            log.error("URLError! - url: %s" % url)
                        else:
                            try:
                                ajax_mblogs += parse_json(ajax_resp, uid)
                            except JsonDataParsingError:
                                log.error("No json data to be loaded! - url: %s" % url)
                            except UnsuspectedPageStructError:
                                log.error("Unsuspected page structure! - url: %s" % url)
                            else:
                                break

                    for mblog in ajax_mblogs:
                        if len(storage.MicroBlog.objects(mid=mblog.mid)) < 1:
                            mblog.save()
                        count_on_this_page += 1
                log.info("MicroBlogs fetched - uid: %s - page: %d - count: %d" % (uid, page, count_on_this_page))
            else:
                #page fetch fail
                try:
                    os.remove(COOKIE_FILE)
                except:
                    pass

                if not os.path.exists(COOKIE_FILE):
                    time.sleep(random.uniform(5,25))
                if login(USERNAME, PASSWORD, COOKIE_FILE) == 0:
                    log.error("Login fail!")
            page += 1
            mblog_count += count_on_this_page
            time.sleep(randint(1, MAXSLEEPINGTIME))
    else:
        log.error("Login fail!")
        try:
            os.remove(COOKIE_FILE)
        except:
            pass
    print last_update_time
    return mblog_count,last_update_time

def crawl_one(uid, weibo_user_type=1001):
    '''
    get one's profile, follows, and all his/her microblogs
    `uid`: the user's uid
    `weibo_user_type`: normal user(1001) or media user(1002)
    '''
    event_logger.info("Crawl_one start uid: %s" % uid)

    info = get_info(uid, weibo_user_type)

    if info:
        event_logger.info("Information fetching succeed - uid: %s" % uid)
    else:
        event_logger.critical("Infromation fetching fail - uid: %s" % uid)
        return 
#    followees = get_follows(uid, info.n_followees, 1)
#    event_logger.info("Followees fetched - uid:%s - target amount: %d - realized amount: %d" % (uid, info.n_followees, len(followees)))
#    followers = get_follows(uid, info.n_followers, 2)
#    event_logger.info("Followers fetched - uid: %s - target amount: %d - realized amount: %d" % (uid, info.n_followers, len(followers)))

    total_mblogs,last_update_time = get_mblogs(uid, info.n_mblogs, info.domain, weibo_user_type, limit=100)

    user, create = storage.WeiboUser.objects.get_or_create(uid=uid)
    user.info = info
#    user.followees = followees
#    user.followers = followers
    user.last_update_time = last_update_time

    for o_O in range(MAXTIMES2TRY):
        try:
            user.save()
        except Exception, e:
            s = traceback.format_exc()
            error_logger.error("Mongo Error wit uid:%s" % (uid,))
            error_logger.error(s)
        else:
            break

    event_logger.info("MicroBlogs fetched - uid: %s - target amount: %d - realized amount: %d)" % (uid, info.n_mblogs, total_mblogs))
    event_logger.info("Finish uid: %s" % uid)


def create_time(t):
    return t.created_time

def add_crawl(uid,weibo_user_type=1001):
    event_logger.info("Add crawl start uid: %s" % uid)
    
    last_update_time = storage.WeiboUser.objects(uid=uid)[0].last_update_time
    if last_update_time is None:
        last_update_time = datetime.datetime(1,1,1)
    info = get_info(uid)
    mblog_count = 0
    new_mblog_count = 0
    n_mblogs = info.n_mblogs
    domain = info.domain

    if not os.path.exists(COOKIE_FILE):
        time.sleep(random.uniform(5,25))
    if login(USERNAME, PASSWORD, COOKIE_FILE):
        if n_mblogs is None:
            n_mblogs = 0
        n_pages = int(n_mblogs / 45) #45 mblogs per page
        page = 1  #begin from first page
        new_last_update_time = datetime.datetime(1,1,1) 
        while page <= n_pages+1:
            count_on_this_page = 0
            url = ''
            if weibo_user_type == 1001:
                url = 'http://weibo.com/' + uid + '/weibo?page=' + str(page)
            elif weibo_user_type == 1002:
                url = 'http://weibo.com/' + uid + '/mblog?page=' + str(page)
            mblogs = None
            for o_o in range(MAXTIMES2TRY):
                try:
                    html = urlfetch(url)
                    #with open('data/'+ uid + '.html' ,'w') as f:
                    #    f.write(html)
                except URLError:
                    log.error("URLError! - url: %s" % url)
                    time.sleep(randint(1, MAXSLEEPINGTIME))
                    continue
                else:
                    try:
                        mblogs = parse_mblog(html, uid)
                        if page == 1:
                            mblogs = sorted(mblogs,key=create_time,reverse=True)
                    except UnsuspectedPageStructError:
                        log.error("Unsuspected page structure! - url: %s" % url)
                    break
            if mblogs is not None and len(mblogs) > 0:
                if page == 1:
                    new_last_update_time = mblogs[0].created_time
                for mblog in mblogs:
                    if mblog.created_time <= last_update_time:
                        if new_last_update_time > last_update_time:
                            storage.WeiboUser.objects(uid=uid).update(set__last_update_time=new_last_update_time,set__info=info)
                        log.info("MicroBlogs fetched - uid: %s - new microblog count: %d" % (uid, new_mblog_count))
                        return
                    if len(storage.MicroBlog.objects(mid=mblog.mid)) < 1:
                        mblog.save()
                        new_mblog_count += 1
                    count_on_this_page += 1
                #load ajax data
                params = dict()
                params['max_id'] = mblogs[-1].mid
                params['end_id'] = mblogs[0].mid
                params['page'] = str(page)
                params['pre_page'] = str(page)
                params['count'] = str(15)
                params['feed_type'] = 0
                params['__rnd'] = str(int(time.time()*1000))
                params['id'] = domain + uid if domain is not None and uid is not None else None
                params['pagebar'] = '0'
                params['domain'] = domain
                params['script_uri'] = r'/' + uid + r'/weibo'

                url = 'http://weibo.com/p/aj/mblog/mbloglist?' + urllib.urlencode(params)
                #ajax_resp = urlfetch('http://weibo.com/p/aj/mblog/mbloglist?' + urllib.urlencode(params))
                ajax_mblogs = None
                try:
                    ajax_resp = urlfetch(url)
                except URLError:
                    log.error("URLError! - url: %s" % url)
                else:
                    try:
                        ajax_mblogs = parse_json(ajax_resp, uid)
                    except JsonDataParsingError:
                        log.error("No json data to be loaded! - url: %s" % url)
                    except UnsuspectedPageStructError:
                        log.error("Unsuspected page structure! - url: %s" % url)
                if ajax_mblogs is not None and len(ajax_mblogs) > 0:
                    params['max_id'] = ajax_mblogs[-1].mid 
                    params['__rnd'] = str(int(time.time()*1000))
                    params['pagebar'] = '1'

                    url = 'http://weibo.com/p/aj/mblog/mbloglist?' + urllib.urlencode(params)
                    ajax_resp = urlfetch(url)

                    try:
                        ajax_mblogs += parse_json(ajax_resp, uid)
                    except JsonDataParsingError:
                        log.error("No json data to be loaded! - url: %s" % url)
                    except UnsuspectedPageStructError:
                        log.error("Unsuspected page structure! - url: %s" % url)

                    for mblog in ajax_mblogs:
                        if mblog.created_time <= last_update_time:
                            log.info("MicroBlogs fetched - uid: %s - new microblog count: %d" % (uid, new_mblog_count))
                            return
                        if len(storage.MicroBlog.objects(mid=mblog.mid)) < 1:
                            if new_last_update_time > last_update_time:
                                storage.WeiboUser.objects(uid=uid).update(set__last_update_time=new_last_update_time,set__info=info)
                            mblog.save()
                            new_mblog_count+=1
                        count_on_this_page += 1
                log.info("MicroBlogs fetched - uid: %s - page: %d - count: %d" % (uid, page, count_on_this_page))
            else:
                #page fetch fail
                try:
                    os.remove(COOKIE_FILE)
                except:
                    pass

                if not os.path.exists(COOKIE_FILE):
                    time.sleep(random.uniform(5,25))
                if login(USERNAME, PASSWORD, COOKIE_FILE) == 0:
                    log.error("Login fail!")
            page += 1
            mblog_count += count_on_this_page
            time.sleep(randint(1, MAXSLEEPINGTIME))
    else:
        log.error("Login fail!")
        try:
            os.remove(COOKIE_FILE)
        except:
            pass
    if new_last_update_time > last_update_time:
        storage.WeiboUser.objects(uid=uid).update(set__last_update_time=new_last_update_time)

def get_uid_by_uickname(nickname):
    if not os.path.exists(COOKIE_FILE):
        time.sleep(random.uniform(5,25))
    if login(USERNAME, PASSWORD, COOKIE_FILE):
        for o_o in range(MAXTIMES2TRY):
            try:
                url = 'http://weibo.com/n/' +nickname
                html = urlfetch(url)
            except URLError:
                log.error("URLError! - url: %s" % url)
                time.sleep(randint(1, MAXSLEEPINGTIME))
                continue
            else:
                try:
                    if 'noresult_tit' in html:
                        return "This username does not match a weibo user"
                    uid_pattern = re.compile('oid\'.+?\'(\d+)\'')
                    uid = uid_pattern.findall(html)[0]
                    return uid
                except:
                    pass
    else:
        log.error("Login fail!")
        try:
            os.remove(COOKIE_FILE)
        except:
            pass

def get_mblogs_by_time(uid,start,end):
    mblog_count = 0
    if not os.path.exists(COOKIE_FILE):
        time.sleep(random.uniform(5,25))
    if login(USERNAME, PASSWORD, COOKIE_FILE):
        info = get_info(uid)
        domain = info.domain
        url = 'http://weibo.com/%s/weibo?is_ori=1&is_forward=1&key_word=&start_time=%s&end_time=%s&is_search=1' % (uid,start,end)
        html = urlfetch(url)
        pattern = re.compile('S_spetxt.+?\>(\d+)\<')
        n_mblogs = int(pattern.findall(html)[0])
        print uid,start,n_mblogs
        n_pages = int(n_mblogs / 45) #45 mblogs per page
        page = 1  #begin from first page
        last_update_time = datetime.datetime(1,1,1)
        while page <= n_pages+1:
            count_on_this_page = 0
            base_url = 'http://weibo.com/%s/weibo?is_ori=1&is_forward=1&key_word=&start_time=%s&end_time=%s&page=%s&is_search=1' % (uid,start,end,page)
            mblogs = None
            for o_o in range(MAXTIMES2TRY):
                try:
                    html = urlfetch(base_url)
                except URLError:
                    log.error("URLError! - url: %s" % url)
                    time.sleep(randint(1, MAXSLEEPINGTIME))
                    continue
                else:
                    try:
                        mblogs = parse_mblog(html, uid)
                    except UnsuspectedPageStructError:
                        log.error("Unsuspected page structure! - url: %s" % url)
                    break
            if mblogs is not None and len(mblogs) > 0:
                if page == 1:
                    last_update_time = mblogs[0].created_time
                for mblog in mblogs:
                    if len(storage.MicroBlog.objects(mid=mblog.mid)) < 1:
                        mblog.save()
                    count_on_this_page += 1
                #load ajax data
                params = dict()
                params['max_id'] = mblogs[-1].mid
                params['end_id'] = mblogs[0].mid
                params['page'] = str(page)
                params['pre_page'] = str(page)
                params['count'] = str(15)
                params['feed_type'] = 0
                params['__rnd'] = str(int(time.time()*1000))
                params['id'] = domain + uid if domain is not None and uid is not None else None
                params['pagebar'] = '0'
                params['domain'] = domain
                params['script_uri'] = r'/' + uid + r'/weibo'

                url = 'http://weibo.com/p/aj/mblog/mbloglist?is_ori=1&is_forward=1&key_word=&start_time=%s&end_time=%s&is_search=1&' % (start,end)
                url = url + urllib.urlencode(params)
                #ajax_resp = urlfetch('http://weibo.com/p/aj/mblog/mbloglist?' + urllib.urlencode(params))
                ajax_mblogs = None
                try:
                    ajax_resp = urlfetch(url)
                except URLError:
                    log.error("URLError! - url: %s" % url)
                else:
                    try:
                        ajax_mblogs = parse_json(ajax_resp, uid)
                    except JsonDataParsingError:
                        log.error("No json data to be loaded! - url: %s" % url)
                    except UnsuspectedPageStructError:
                        log.error("Unsuspected page structure! - url: %s" % url)
                if ajax_mblogs is not None and len(ajax_mblogs) > 0:
                    params['max_id'] = ajax_mblogs[-1].mid 
                    params['__rnd'] = str(int(time.time()*1000))
                    params['pagebar'] = '1'

                    url = 'http://weibo.com/p/aj/mblog/mbloglist?is_ori=1&is_forward=1&key_word=&start_time=%s&end_time=%s&is_search=1&' % (start,end)
                    url = url + urllib.urlencode(params)
                    ajax_resp = urlfetch(url)

                    try:
                        ajax_mblogs += parse_json(ajax_resp, uid)
                    except JsonDataParsingError:
                        log.error("No json data to be loaded! - url: %s" % url)
                    except UnsuspectedPageStructError:
                        log.error("Unsuspected page structure! - url: %s" % url)

                    for mblog in ajax_mblogs:
                        if len(storage.MicroBlog.objects(mid=mblog.mid)) < 1:
                            mblog.save()
                        count_on_this_page += 1
                log.info("MicroBlogs fetched - uid: %s - page: %d - count: %d" % (uid, page, count_on_this_page))
            else:
                #page fetch fail
                try:
                    os.remove(COOKIE_FILE)
                except:
                    pass
                if not os.path.exists(COOKIE_FILE):
                    time.sleep(random.uniform(5,25))
                if login(USERNAME, PASSWORD, COOKIE_FILE) == 0:
                    log.error("Login fail!")
            page += 1
            mblog_count += count_on_this_page
            time.sleep(randint(1, MAXSLEEPINGTIME))
    else:
        log.error("Login fail!")
        try:
            os.remove(COOKIE_FILE)
        except:
            pass
    return mblog_count,last_update_time


def test_info():
    #info = get_info('1618051664', 1002)
    with open("media.txt") as f:
        for line in f:
            line = line.strip()
            uid = line.split(' ')[0]
            info = get_info(uid)
            print info.nickname
            print info.n_mblogs
            print info.n_followees
            print info.n_followers
            print info.weibo_user_type

def test_follow():
    follows = get_follows('1699002082', 81, 2)
    for follow in follows:
        print follow.uid

def test_mblog():
    #total_mblogs = get_mblogs("3121700831", 663, "100505")
    total_mblogs = get_mblogs('1198367585', 500, '100505')
    #total_mblogs = get_mblogs('1618051664', 100, '100206', 1002)
    print total_mblogs

def test():
    uid = '3015910193'
#    crawl_one(uid)
#    add_crawl(uid)
#    get_info(uid)
    info = get_info(uid)
    print info.n_mblogs

#    search_usernames = ['新华视点','人民日报','央视新闻']
#    uids = ['1699432410','2803301701','2656274875']
#
#    search_times = ['2012-11-18','2012-12-1','2012-12-28','2013-1-9','2013-1-17','2013-2-4','2013-3-19']
#    users = zip(uids,search_usernames)
#
#    at_pattern = re.compile(u"@([0-9a-zA-Z\u4e00-\u9fa5\-\_]+)")
#    for uid,username in users:
#        for search_time in search_times:
#            at_nicknames = []
#            start = datetime.datetime.strptime(search_time,'%Y-%m-%d')
#            end = start + datetime.timedelta(1)
#            for micro_blog in storage.MicroBlog.objects(uid=uid,created_time__gte=start,created_time__lt=end):
#                content = micro_blog.content
#                for nickname in at_pattern.findall(content):
#                    at_nicknames.append(nickname)
#            print username,search_time,','.join(at_nicknames)

#    for micro_blog in storage.MicroBlog.objects:
#        print micro_blog.created_time
#    for uid in uids:
#        for search_time in search_times:
#            get_mblogs_by_time(uid,search_time,search_time)
#            time.sleep(random.randint(5,10))

if __name__ == '__main__':
    test()

