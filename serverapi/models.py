from django.db import models
from mongoengine import *
import mongoengine
# Create your models here.

# 指明要连接的数据库
# connect('Complaint',host = '127.0.0.1',port = 27017)

connect('qq', host='localhost', port=27017)

class QQscore10Model(Document):
    data = mongoengine.StringField()
    srank = mongoengine.ListField()
    score = mongoengine.IntField(default=0)
    nuniv= mongoengine.IntField(default=0)
    nsp = mongoengine.IntField(default=0)
    total = mongoengine.IntField(default=0)
    province_id = mongoengine.IntField(default=37)
    local_type_id = mongoengine.IntField(default=1)
    counts = mongoengine.StringField()
    meta = {'collection':'qqscore10'}

class QQscoreModel(Document):
    data = mongoengine.StringField()
    srank = mongoengine.ListField()
    score = mongoengine.IntField(default=0)
    nuniv= mongoengine.IntField(default=0)
    nsp = mongoengine.IntField(default=0)
    total = mongoengine.IntField(default=0)
    province_id = mongoengine.IntField(default=37)
    local_type_id = mongoengine.IntField(default=1)
    counts = mongoengine.StringField()
    meta = {'collection':'qqscoreall'}

class UserInfos(Document):
    avatarUrl = mongoengine.StringField()
    city = mongoengine.StringField()
    country = mongoengine.StringField()
    gender = mongoengine.IntField(default=1)
    language = mongoengine.StringField()
    nickName = mongoengine.StringField()
    province = mongoengine.StringField()
    openid = mongoengine.StringField()
    meta = {'collection': 'userinfos'}

class UserRepost(Document):
    avatarUrl = mongoengine.StringField()
    city = mongoengine.StringField()
    country = mongoengine.StringField()
    gender = mongoengine.IntField(default=1)
    language = mongoengine.StringField()
    nickName = mongoengine.StringField()
    province = mongoengine.StringField()
    openid = mongoengine.StringField()
    friends = mongoengine.ListField(UserInfos())
    meta = {'collection': 'userrepost'}

class UserInfo(Document):
    openid = mongoengine.StringField()
    info = mongoengine.StringField()

class UserRepostStr(Document):
    openid = mongoengine.StringField()
    info = mongoengine.StringField()
    friends = mongoengine.ListField()    
    vip = mongoengine.IntField(default=0)
    isvip = mongoengine.IntField(default=0)
    #friends = mongoengine.ListField(UserInfo())    
    meta = {'collection': 'userrepoststr'}

# 测试是否连接成功
# for i in qqscore10.objects[:10]:
#     print(i.score)
