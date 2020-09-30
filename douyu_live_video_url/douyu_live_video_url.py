# -*- coding:utf-8 -*-
import requests
import re
import execjs
import time
from urllib import parse
import os
import hashlib

# roomid 直播间id，不一定是真实id，例如：https://m.douyu.com/88888，真实id并非88888
def get_douyu_vurl(roomid):
    dy_did = '3179e930f45e2d6e6cba653200071501'  # cookies中的dy_did
    nowtime = int(time.time())
    try:
        source = requests.request("GET", "https://m.douyu.com/" + roomid)
        source = source.text
    except Exception as e:
        print(e)
        return

    # get real rid
    try:
        rid_res = re.search(r'rid":(\d{1,10}),"vipId', source)
        rid = rid_res.group(1)
    except Exception as e:
        print('房间号错误')
        return
    else:
        print(rid)

    get_js(rid, dy_did, nowtime, source)


def get_js(rid, did, t10, source):
    try:
        result = re.search(r'(function ub98484234.*)\s(var.*)', source).group()
        print(result)
        func_ub9 = re.sub(r'eval.*;}', 'strc;}', result) # re.sub 正则表达式替换，参数1表达式 参数2被替换的字符串 参数3被搜寻的字符串
        js = execjs.compile(func_ub9)
        res = js.call('ub98484234')
    except Exception as e:
        print(e)
        return

    try:
        v = re.search(r'"v.*?=\s*(\d+)', res).group(1)
        rb = crypto_md5(rid + did + str(t10) + v)
        func_sign = re.sub(r'return rt;}\);?', 'return rt;}', res)
        func_sign = func_sign.replace('(function (', 'function sign(')
        func_sign = func_sign.replace('CryptoJS.MD5(cb).toString()', '"' + rb + '"')
        js = execjs.compile(func_sign)
        print(func_sign)
    except Exception as e:
        print(e)
        return

    try:
        params = js.call('sign', rid, did, t10)
        params += '&ver=219032101&rid=' + rid + '&rate=1'
        params = dict(parse.parse_qsl(params))
        print(params)
    except Exception as e:
        print(e)
        return

    try:
        s = requests.Session()
        res = s.post("https://m.douyu.com/api/room/ratestream", params)
        res = res.text
        print(res)
    except Exception as e:
        print(e)
        return

    try:
        key = re.search(r'(\d{1,7}[0-9a-zA-Z]+)_?\d{0,4}(.m3u8|/playlist)', res).group(1)
        live_vurl = 'http://tx2play1.douyucdn.cn/live/' + key + '.flv'
        print('获取直播流地址成功，地址为：' + live_vurl)
        os.system('ffplay ' + live_vurl)  # 使用ffplay播放视频
    except Exception as e:
        print('主播尚未开播')
        return

def crypto_md5(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()

while True:
    roomid = input('请输入斗鱼直播间号：')
    get_douyu_vurl(roomid)
