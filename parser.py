# -*- coding: utf-8 -*-
'''
@author Jiajun Huang
created on 2013/10/19
'''

import storage

from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

def parse_user_profile(html):
    '''
    return an object of UserInfo
    Arguments:
    `html`: a text of html code
    '''
    soup = BeautifulSoup(html)
    user_info = storage.UserInfo()
    #domain
    regex = re.compile("\$CONFIG\['domain']='[0-9]+';")
    m = regex.search(html)
    if m is not None:
        user_info.domain = m.group()[19:-2]

    for script in soup.findAll('script'):
        text = script.text
        if 'FM.view(' in text:
            text = text[8:]
            if text.endswith(')'):
                text = text[:-1]
            if text.endswith(');'):
                text = text[:-2]
            data = json.loads(text)
            inner_html = data.get('html')
            if inner_html is None:
                continue
            inner_soup = BeautifulSoup(inner_html)
            #n_followees, n_followers and n_mblogs
            followee_strong = inner_soup.find('strong', attrs={'node-type': 'follow'})
            if followee_strong is not None:
                user_info.n_followees = int(followee_strong.text.strip())
            follower_strong = inner_soup.find('strong', attrs={'node-type': 'fans'})
            if follower_strong is not None:
                user_info.n_followers = int(follower_strong.text.strip())
            mblogs_strong  = inner_soup.find('strong', attrs={'node-type': 'weibo'})
            if mblogs_strong is not None:
                user_info.n_mblogs = int(mblogs_strong.text.strip())
            #other information
            pf_items = inner_soup.findAll('div',  attrs={'class': 'pf_item clearfix'})
            for item in pf_items:
                divs = item.findAll('div')
                i = 0
                while i < len(divs):
                    anna = divs[i].text
                    if anna == u'昵称':
                        user_info.nickname = divs[i+1].text.strip()
                    elif anna == u'所在地':
                        user_info.location = divs[i+1].text.strip()
                    elif anna == u'性别':
                        user_info.sex = True if divs[i+1].text.strip() == u'男' else False
                    elif anna == u'生日':
                        user_info.birth = divs[i+1].text.strip()
                    elif anna == u'博客':
                        user_info.blog = divs[i+1].text.strip()
                    elif anna == u'简介':
                        user_info.intro = divs[i+1].text.strip()
                    elif anna == u'邮箱':
                        user_info.email = divs[i+1].text.strip()
                    elif anna == u'个性域名':
                        user_info.site = divs[i+1].text.strip()
                    elif anna == u'QQ':
                        user_info.qq = divs[i+1].text.strip()
                    elif anna == u'MSN':
                        user_info.msn = divs[i+1].text.strip()
                    elif anna == u'大学' or anna == u'高中' or anna == u'初中' or anna == u'小学':
                        edu_info = storage.EduInfo()
                        school = divs[i+1].p.contents[0]
                        if school is not None:
                            edu_info.school = school.text.strip()
                        if school.nextSibling is not None:
                            edu_info.time = school.nextSibling.strip()
                        if len(divs[i+1].findAll('p')) > 1:
                            edu_info.detail = divs[i+1].findAll('p')[1].text.strip()
                        if edu_info.school is not None:
                            user_info.edu.append(edu_info)
                    elif anna == u'公司':
                        while (i+1) < len(divs):
                            acompany = divs[i+1]
                            work_info = storage.WorkInfo()
                            all_p = acompany.findAll('p')
                            company = all_p[0].contents[0]
                            if company is not None:
                                work_info.company = company.text.strip()
                            if company.nextSibling is not None:
                                work_info.time = company.nextSibling.strip()
                            j = 1
                            while j < len(all_p):
                                if all_p[j].text.strip().startswith(u'地区'):
                                    work_info.location = all_p[j].text.strip()[3:]
                                if all_p[j].text.strip().startswith(u'职位'):
                                    work_info.department_or_position = all_p[j].text.strip()[3:]
                                j += 1
                            user_info.work.append(work_info)
                            i += 1
                    elif anna == u'标签':
                        tags = divs[i+1]
                        if tags is not None:
                            for a in tags.findAll('a'):
                                user_info.tags.append(a.text.strip())
                    i += 2
    if user_info.nickname is not None:
        return user_info
    else:
        return None

def parse_follow(html):
    '''
    return a list of follows in this page
    `html`: html code as string-type
    '''
    soup = BeautifulSoup(html)
    follows = []
    for script in soup.findAll('script'):
        text = script.text
        if 'FM.view(' in text:
            text = text[8:]
            if text.endswith(')'):
                text = text[:-1]
            if text.endswith(');'):
                text = text[:-2]
            data = json.loads(text)
            inner_html = data.get('html')
            if inner_html is None:
                continue
            inner_soup = BeautifulSoup(inner_html)
            follows_li = inner_soup.findAll('li', attrs={'class': 'clearfix S_line1'})
            for item in follows_li:
                follow = storage.Follow()
                a = item.find('a', usercard=True)
                if a is not None:
                    follow.uid = a['usercard'][3:]
                    follow.nickname = a.text.strip()
                follows.append(follow)
    return follows

def parse_mblog(html, uid):
    '''
    return a list of micro-blogs in this page
    `html`: html code as string-type
    `uid`: uid of user who owns this page
    '''
    mblogs = list()
    soup = BeautifulSoup(html)
    for script in soup.findAll('script'):
        text = script.text
        if 'FM.view(' in text:
            text = text[8:]
            if text.endswith(')'):
                text = text[:-1]
            if text.endswith(');'):
                text = text[:-2]
            data = json.loads(text)
            inner_html = data.get('html')
            if inner_html is None:
                continue
            mblogs += _get_mblogs(inner_html, uid)

    return mblogs

def parse_json(data, uid):
    '''
    parse json data, and return a list of micro blogs
    `data`: json data
    'uid': weibo user id
    '''
    try:
        html = json.loads(data)['data']
        return _get_mblogs(html, uid)
    except Exception, e:
        print e
        return []


def _get_mblogs(html, uid):
    '''
    get mblogs from showed html
    `html`: html codes
    '''
    mblogs = list()
    soup = BeautifulSoup(html)
    mbdivs = soup.findAll('div', attrs={'class':'WB_feed_type SW_fun S_line2 '})  #a list of div-tags, each item of it contains a micro-blog
    for mbdiv in mbdivs:
        try:
            mblog = storage.MicroBlog()
            mblog.mid = mbdiv['mid']
            mblog.uid = uid
            mblog.content = mbdiv.find('div', attrs={'class': 'WB_text'}).text.strip()
        
            created_time = mbdiv.findAll('a', attrs={'class': 'WB_time'})[-1]['title']
            date, time = created_time.split()
            year, month, day = date.split('-')
            hour, minute = time.split(':')
            mblog.created_time = datetime(int(year), int(month), int(day), int(hour), int(minute))

            #n_likes, n_forwards, n_comments
            handle_divs = mbdiv.findAll('div', attrs={'class': 'WB_handle'})
            if len(handle_divs) > 0:
                handle_div = handle_divs[-1]
                handles_a = handle_div.findAll('a')
                like = handles_a[0]
                repost = handles_a[1]
                comment = handles_a[3]
                if len(like.text.strip()) > 0:
                    mblog.n_likes = int(like.text.strip()[1:-1])
                else:
                    mblog.n_likes = 0
                if len(repost.text.strip()) > 4:
                    mblog.n_forwards = int(repost.text.strip()[3:-1])
                else:
                    mblog.n_forwards = 0
                if len(comment.text.strip()) > 4:
                    mblog.n_comments = int(comment.text.strip()[3:-1])
                else:
                    mblog.n_comments = 0
      
            #geographical message
            geodiv = mbdiv.find('div', attrs={'class': 'map_data'})
            if geodiv is not None:
                geo = storage.Geo()
                geo.location = geodiv.text.strip()
                regex = re.compile('geo=.*&')
                anna = regex.findall(str(geodiv))[0]
                anna = anna.split('&')[0][4:]
                longitude, latitude = anna.split(',')
                geo.longitude = float(longitude)
                geo.latitude = float(latitude)
                mblog.geo = geo


            #if this mblog is not an original mblog
            if mbdiv.get('isforward') is not None:
                mblog.is_forward = True
                ori_mblog = storage.OriMBlog()
                usercard = mbdiv.find('a', attrs={'class': 'WB_name S_func3'})
                if usercard is not None:
                    uid = usercard['usercard'][3:]
                    ori_mblog.uid = uid
                    ori_mblog.mid = mbdiv.get('omid')
                    ori_mblog.content = mbdiv.findAll('div', attrs={'class': 'WB_text'})[-1].text.strip()
                mblog.ori_mblog = ori_mblog
            else:
                mblog.is_forward = False

            mblogs.append(mblog)
        except Exception, e:
            print e
    return mblogs

def test_info():
    from weibo_login import login
    from conf import USERNAME, PASSWORD, COOKIE_FILE
    from opener import urlfetch
    if login(USERNAME, PASSWORD, COOKIE_FILE) is False:
        print "Login failed!"
        return 
    html = urlfetch("http://weibo.com/1789809794/info")
    user_info = parse_user_profile(html)
    print user_info.nickname, user_info.location, user_info.sex, user_info.birth, \
            user_info.blog, user_info.site, user_info.intro, user_info.email, user_info.qq, user_info.msn
    print "n_followees: ",  user_info.n_followees
    print "n_followers: ",  user_info.n_followers
    print "n_mblogs: ",  user_info.n_mblogs
    print "domain: ", user_info.domain
    for edu in user_info.edu:
        print edu.school, edu.time, edu.detail
    for work in user_info.work:
        print work.company, work.time, work.department_or_position, work.location
    for tag in user_info.tags:
        print tag

def test_follow():
    ff = open('test/follow.html', 'r')
    html = ff.read()
    ff.close()
    follows = parse_follow(html)
    for follow in follows:
        print follow.uid, follow.nickname

def test_mblog():
    #ff = open('test/mblog2.html', 'r')
    #html = ff.read()
    #ff.close()
    from weibo_login import login
    from conf import USERNAME, PASSWORD, COOKIE_FILE
    from urllib2 import urlopen
    html = ''
    if login(USERNAME, PASSWORD, COOKIE_FILE):
        print 'Login!'
        from opener import urlfetch
        html = urlfetch("http://weibo.com/2584784292/weibo")
        #print html
    mblogs = parse_mblog(html, '2584784292')
    for m in mblogs:
        print 'uid: ', m.uid
        print 'mid: ', m.mid
        print 'content: ' , m.content
        print 'time: ', m.created_time
        print 'n_likes: ', m.n_likes
        print 'n_forward: ', m.n_forwards
        print 'n_comments: ', m.n_comments
        if m.geo:
            print 'longitude: ', m.geo.longitude
            print 'latitude: ', m.geo.latitude
            print 'location: ', m.geo.location
        print m.is_forward
        if m.is_forward:
            print 'ouid: ', m.ori_mblog.uid
            print 'omid: ', m.ori_mblog.mid
            print 'ocontent: ', m.ori_mblog.content
        print '======================================'

    

if __name__ == '__main__':
    #test_mblog()
    test_info()
    #test_get_domain()
    #test_get_n_mblogs()

