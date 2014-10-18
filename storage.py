# -*- coding: utf-8 -*-
'''
    #author: Jiajun Huang
    created on 2013/10/13
'''
import traceback
try:
    from mongoengine import Document, EmbeddedDocument, \
            StringField, DateTimeField, EmailField, \
            BooleanField, URLField, IntField, FloatField, \
            ListField, EmbeddedDocumentField
    from conf import DBNAME, DBHOST, DBPORT
    import mongoengine
except ImportError:
    s = traceback.format_exc()
    print s
    

#connent mongodb with dbname
mongoengine.connect(DBNAME, host=DBHOST, port=DBPORT)


class ForwardOrComment(EmbeddedDocument):
    mid = StringField(required=True)
    uid = StringField(required = True)
    content = StringField()
    created_time = DateTimeField()


class Like(EmbeddedDocument):
    uid = StringField(required=True)


class Geo(EmbeddedDocument):
    longitude = FloatField()
    latitude = FloatField()
    location = StringField()


class OriMBlog(EmbeddedDocument):
    uid = StringField()
    mid = StringField()
    content = StringField()
    faces = ListField(StringField())


class MicroBlog(Document):
    mid = StringField(unique=True,required=True)
    uid = StringField(required=True)
    content = StringField()
    created_time = DateTimeField()
    geo = EmbeddedDocumentField(Geo)

    is_forward = BooleanField()
    ori_mblog = EmbeddedDocumentField(OriMBlog)
    
    n_likes = IntField()
    likes = ListField(EmbeddedDocumentField(Like))
    n_forwards = IntField()
    forwards = ListField(EmbeddedDocumentField(ForwardOrComment))
    n_comments = IntField()
    comments = ListField(EmbeddedDocumentField(ForwardOrComment))
    
    faces = ListField(StringField())


class EduInfo(EmbeddedDocument):
    school = StringField()
    time = StringField()
    detail = StringField()


class WorkInfo(EmbeddedDocument):
    company = StringField()
    time = StringField()
    department_or_position = StringField()
    location = StringField()


class UserInfo(EmbeddedDocument):
    nickname = StringField()
    location = StringField()
    sex = BooleanField()
    birth = StringField()
    blog = StringField()
    site = StringField()
    intro = StringField()
    email = EmailField()
    qq = StringField()
    msn = StringField()
    edu = ListField(EmbeddedDocumentField(EduInfo))
    work = ListField(EmbeddedDocumentField(WorkInfo))
    tags = ListField(StringField())
    n_followees = IntField()
    n_followers = IntField()
    n_mblogs = IntField()
    domain = StringField()
    weibo_user_type = IntField()


class Follow(EmbeddedDocument):
    uid = StringField()
    nickname = StringField()


class WeiboUser(Document):
    uid = StringField(unique=True, required=True)
    last_update_time = DateTimeField()   #lastest update time 
    last_mid = StringField()        #the lastest microblog this user posted 

    info = EmbeddedDocumentField(UserInfo)
    followees = ListField(EmbeddedDocumentField(Follow))
    followers = ListField(EmbeddedDocumentField(Follow))

class WaitCrawlUser(Document):
    uid = StringField(unique=True, required=True)
    nickname = StringField()
    

def test():
    user_info = UserInfo()
    user_info.nickname = u"默契"
    user_info.email = u'mmmoqi@gmail.com'
    print user_info.nickname, user_info.email, user_info.edu is None

if __name__ == '__main__':
    test()
