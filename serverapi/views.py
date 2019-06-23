from django.shortcuts import render
from django.core import serializers

# Create your views here.

#导入HttpResponse，用来向网页返回内容的，像print一样，不过HttpResponse是把内容显示到网页上。
from django.http import HttpResponse
# Create your views here.
from .models import QQscore10Model
from .models import QQscoreModel
from .models import UserRepost
from .models import UserRepostStr
from django.http import JsonResponse
import json
# import obtain_openid_demo

import redis
from django.shortcuts import render,HttpResponse
from django_redis import get_redis_connection
from django.core.cache import cache
#from serverapi.pay_demo import PayMe
from . pay_demo import PayMe
#from . import pay_demo2
#import pay_demo2 
#from . config import APPID, MCHID, KEY, NOTIFY_URL
from serverapi.obtain_openid_demo import OpenidUtils

import xmltodict

def index(request):#定义一个函数，第一个参数必须是request
    print('lalala')
    return HttpResponse("Hello, world. Hello，python.")#返回HttpResonse对象，最终将这行字符显示在页面上

def qqscorefree(request):
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print(request.META.get("HTTP_COOKIE"))
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print(request.GET['score'], request.GET['local_type_id'], request.GET['province_id'])
    res = {}
#    res = QQscoreModel.objects.get(score=request.GET['score'], local_type_id=request.GET['local_type_id'], province_id=request.GET['province_id'])
    if (int(request.GET['isvip']) == 1):
        res = QQscoreModel.objects.get(score=request.GET['score'], local_type_id=request.GET['local_type_id'], province_id=request.GET['province_id'])
    else:
        res = QQscore10Model.objects.get(score=request.GET['score'], local_type_id=request.GET['local_type_id'], province_id=request.GET['province_id'])
    # res = QQscore10Model.objects.get(score=520, local_type_id=1)
#    print(res.data)
    
    return JsonResponse({
        'score':res.score, 
        'local_type_id':res.local_type_id, 
        'counts': res.counts, 
        'srank':res.srank, 
        'data':res.data,
        'nuniv':res.nuniv,
        'nsp':res.nsp,
        'total':res.total,
        'descvip': str(res.total) + ' 条信息'
    }, safe=False)

def getuseropenid(code):
    resopenid = ''
    print('code:' + code)
    if cache.has_key(code):
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        resopenid = cache.get(code)
    else:
        useropenidClass = OpenidUtils(code)
        resopenid = useropenidClass.get_openid()
        print('openid222222:' + resopenid)
        cache.set(code, resopenid, 60*10)
    print('resopenid:' + resopenid)
    return resopenid
    

def logincode(request):
    print('func logincode start.')
    print(request.GET['code'])
    resopenid = getuseropenid(request.GET['code'])
    print(resopenid)
    print('--------------------')
    return JsonResponse({'cc': resopenid})

def storeuser(openid, userinfo):
    res = UserRepostStr.objects.filter(openid=openid)
    print(userinfo)
    if (len(res) == 0 ):
#        UserRepost.objects.create(
#            openid = openid,
#            avatarUrl = userinfo.avatarUrl,
#            city = userinfo.city,
#            country = userinfo.country,
#            gender = userinfo.gender,
#            language = userinfo.language,
#            nickName = userinfo.nickName,
#            province = userinfo.province)
        UserRepostStr.objects.create(openid=openid, info=userinfo, vip=1, isvip=0)
        return 0
    return int(UserRepostStr.objects.get(openid=openid)['isvip'])
    
def storeuserF(repostFid, userinfo, openid):
    #print(UserRepostStr.objects.filter(openid=repostFid).values_list('friends')[0])
    #res = list(UserRepostStr.objects.filter(openid=repostFid).values_list('friends'))[0]
#    print(UserRepostStr.objects.get(openid=repostFid))
#    print(UserRepostStr.objects.get(openid=repostFid)['friends'])
    res = UserRepostStr.objects.get(openid=repostFid)['friends']
    # print(type(res))
    ans = []
    npcount = int(UserRepostStr.objects.get(openid=repostFid)['vip'])
    for item in res:
        if item['openid'] == openid:
            return 0
        ans.append(item)
        npcount = npcount + 1
    if (npcount >= 5):
        UserRepostStr.objects.filter(openid=repostFid).update(isvip=1)
    #userinfo.openid = openid
    ans.append({'openid': openid, 'info': userinfo})
    UserRepostStr.objects.filter(openid=repostFid).update(friends=ans, vip=npcount)
    return int(UserRepostStr.objects.get(openid=repostFid)['isvip'])

def regiuserinfo(request):
#    print('cache.get:' + cache.get('071jBuE51MUiwS1SCeE51MFwE51jBuEq'))
    openid = request.META.get("HTTP_COOKIE")
    userinfo = request.GET['userinfo']
    repostF = request.GET['repostF']
    #repostF = 'omdSp5bJWXCzPyVPN95d6S2C1Hr0'
    print('099:' + openid)
    print('100:' + userinfo)
    print('101:' + repostF)
    isvip = 0
    if openid == 'error':
        return JsonResponse({'cc': 0})
    isvip = storeuser(openid, userinfo)
    if len(repostF) > 8:
        isvip = storeuserF(repostF, userinfo, openid)
    return JsonResponse({'cc': isvip})

def getPostUsers(request):
    openid = request.GET['openid']
    res = UserRepostStr.objects.get(openid=openid)['friends']
    ans = []
    npcount = 0
    for item in res:
        if npcount == 3:
            break
        ans.append(json.loads(item['info']))
        npcount = npcount + 1
    return JsonResponse({'users': ans, 'fee': '1'})

def payme(request):
    openid = request.GET['openid']
    fee = request.GET['fee']
    params = {'fee': fee, 'openid': openid}
    Cpayme = PayMe(openid, fee)
    data = Cpayme.generate_bill() 
    print(data)
    return JsonResponse({'data': data})

def getscorelist(request):
    # provinces = ["河北", "山东", "北京", "天津", "山西", "内蒙古", "辽宁", "吉林", "黑龙江", "上海", "江苏", "浙江", "安徽", "福建", "江西", "河南", "湖北", "湖南", "广东", "广西", "海南", "重庆", "四川", "贵州", "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆"],
    provinces = ["河北", "山东", "北京", "山西", "内蒙古", "吉林", "黑龙江", "江苏", "福建", "河南", "湖南", "广西", "重庆", "贵州", "青海", "宁夏"],
    # pkeys = [37, 13, 11, 12, 14, 15, 21, 22, 23, 31, 32, 33, 34, 35, 36, 41, 42, 43, 44, 45, 46,50, 51, 52, 53, 54, 61, 62, 63, 64, 65],
    pkeys = [37, 13, 11, 14, 15, 22, 23, 32, 35, 41, 43, 45, 50, 52, 63, 64],
    return JsonResponse({'provinces': provinces, 'pkeys': pkeys})

def payed(request):
    msg = request.body.decode('utf-8')
    xmlmsg = xmltodict.parse(msg)
    print('payed!')
    return_code = xmlmsg['xml']['return_code']

    if return_code == 'FAIL':
        # 官方发出错误
        return HttpResponse("""<xml><return_code><![CDATA[FAIL]]></return_code>
                            <return_msg><![CDATA[Signature_Error]]></return_msg></xml>""",
                            content_type='text/xml', status=200)
        
    elif return_code == 'SUCCESS':
        # 拿到这次支付的订单号
        out_trade_no = xmlmsg['xml']['out_trade_no']
        # order = Order.objects.get(out_trade_no=out_trade_no)
        mayopenid = cache.get(out_trade_no)
        if xmlmsg['xml']['nonce_str'] != mayopenid.split('_')[0]:
            # 随机字符串不一致
            return HttpResponse("""<xml><return_code><![CDATA[FAIL]]></return_code>
                                        <return_msg><![CDATA[Signature_Error]]></return_msg></xml>""",
                                content_type='text/xml', status=200)

        # 根据需要处理业务逻辑
        print('updatevip')
        UserRepostStr.objects.filter(openid=mayopenid.split('_')[1]).update(isvip=1)

        return HttpResponse("""<xml><return_code><![CDATA[SUCCESS]]></return_code>
                            <return_msg><![CDATA[OK]]></return_msg></xml>""",
                            content_type='text/xml', status=200)

def descpay(request):
    return JsonResponse({'data': '邀请五位好友试用'})

def tableheader(request):
    return JsonResponse({'col1': '风险', 'col2': '专业', 'col3': '2017', 'col4': '2018(名次)', 'updatecol1': 1})