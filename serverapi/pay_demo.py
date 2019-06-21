#coding=UTF-8
'''
微信小程序支付统一下单demo
'''
import requests
import hashlib
import xmltodict
import time
import random
import string
import datetime
import redis
from django.shortcuts import render,HttpResponse
from django_redis import get_redis_connection
from django.core.cache import cache

from . config import APPID, MCHID, KEY, NOTIFY_URL
    
class PayMe(object):

    def __init__(self, openid, fee):
    #def __int__(self, openid, fee):
        #self.openid = jscode['openid']
        #self.fee = jscode['fee']
        self.openid = openid
        self.fee = fee
        self.nonce_str = ''

    # 生成订单号
    def generate_out_trade_no(self):
        # 20位
        seeds = '1234567890'
        random_str = []
        for i in range(6):
            random_str.append(random.choice(seeds))
        subfix =  ''.join(random_str)
    
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S") + subfix
    
    
    # 生成nonce_str
    def generate_randomStr(self):
        return ''.join(random.sample(string.ascii_letters + string.digits, 32))
    
    # 生成签名
    def generate_sign(self, param):
        stringA = ''
    
        ks = sorted(param.keys())
        # 参数排序
        for k in ks:
            stringA += k + "=" + str(param[k]) + "&"
        # 拼接商户KEY
        stringSignTemp = stringA + "key=" + KEY
        print('stringSignTemp: ' + stringSignTemp)
        # md5加密
        hash_md5 = hashlib.md5(stringSignTemp.encode('utf8'))
        sign = hash_md5.hexdigest().upper()
    
        return sign
    
    # 发送xml请求
    def send_xml_request(self, url, param):
        # dict 2 xml
        param = {'root': param}
        xml = xmltodict.unparse(param)
        print('xxxxxxxxxxxxxxxxxxxxmmmmmmmmmmmmmmmmmllllllllllllllllll')
        print(xml)
    
        response = requests.post(url, data=xml.encode('utf-8'), headers={'Content-Type': 'text/xml'})
        # xml 2 dict
        msg = response.text
        xmlmsg = xmltodict.parse(msg)
    
        return xmlmsg
    
    # 统一下单
    def generate_bill(self):
        fee = self.fee
        openid = self.openid
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        nonce_str = self.generate_randomStr()		# 订单中加nonce_str字段记录（回调判断使用）
        out_trade_no = self.generate_out_trade_no()     # 支付单号，只能使用一次，不可重复支付
        
        self.nonce_str = nonce_str

        '''
        order.out_trade_no = out_trade_no
        order.nonce_str = nonce_str
        order.save()
        '''
    
        # 1. 参数
        param = {
            "appid": APPID,
            "mch_id": MCHID,    # 商户号
            "nonce_str": nonce_str,     # 随机字符串
            "body": '录取线VIP',     # 支付说明
            "out_trade_no": out_trade_no,   # 自己生成的订单号
            "total_fee": self.fee,
            "spbill_create_ip": '129.28.142.81',    # 发起统一下单的ip
            "notify_url": NOTIFY_URL,
            "trade_type": 'JSAPI',      # 小程序写JSAPI
            "openid": openid,
        }
        # 2. 统一下单签名
        sign = self.generate_sign(param)
        param["sign"] = sign  # 加入签名
        # 3. 调用接口
        print(param)
        xmlmsg = self.send_xml_request(url, param)
        print('////////////////')
        print(xmlmsg)
        # 4. 获取prepay_id
        if xmlmsg['xml']['return_code'] == 'SUCCESS':
            if xmlmsg['xml']['result_code'] == 'SUCCESS':
                prepay_id = xmlmsg['xml']['prepay_id']
                # 时间戳
                timeStamp = str(int(time.time()))
                # 5. 根据文档，六个参数，否则app提示签名验证失败，https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_12
                data = {
                    "appId": APPID,
   #                 "partnerid": MCHID,
                    "package": "prepay_id=" + prepay_id,
                    "nonceStr": nonce_str,
                    "timeStamp": timeStamp,
                    "signType": "MD5",
                }
                # 6. paySign签名
                paySign = self.generate_sign(data)
                data["paySign"] = paySign  # 加入签名
                cache.set(out_trade_no, nonce_str + '_' + self.openid, 60*10)
                print(data)
                # 7. 传给前端的签名后的参数
                return data
