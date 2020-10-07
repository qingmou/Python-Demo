# -*- coding:utf-8 -*-
import requests
import re
import execjs
import time
from urllib import parse
import os
import hashlib
import pyperclip
import datetime

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
        print('直播间号错误')
        return
    else:
        print('直播间id：' + rid)

    get_js(rid, dy_did, nowtime, source)


def get_js(rid, did, t10, source):
    try:
        result = re.search(r'(function ub98484234.*)\s(var.*)', source).group()
        # print(result)
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
        # print(func_sign)
    except Exception as e:
        print(e)
        return

    try:
        params = js.call('sign', rid, did, t10)
        params += '&ver=219032101&rid=' + rid + '&rate=1'
        params = dict(parse.parse_qsl(params))
        # print(params)
    except Exception as e:
        print(e)
        return

    try:
        s = requests.Session()
        res = s.post("https://m.douyu.com/api/room/ratestream", params)
        res = res.text
        # print(res)
    except Exception as e:
        print(e)
        return

    try:
        key = re.search(r'(\d{1,7}[0-9a-zA-Z]+)_?\d{0,4}(.m3u8|/playlist)', res).group(1)
        live_vurl = 'http://tx2play1.douyucdn.cn/live/' + key + '.flv'
        t = datetime.datetime.now()
        tc = str(t.year) + '.' + str(t.month) + '.' + str(t.day) + '.' + str(t.hour) + str(t.minute) + str(t.second)
        filename = validateTitle(get_zhubo_filename('直播间' + rid + '_' + tc, source) + '.flv')
        _filename = filename
        savepath = os.getcwd() + '\download'
        _savepath = savepath

        aria2c_path = os.getcwd() + r'\aria2c.exe'
        if os.path.exists(aria2c_path):
            if filename != '':
                filename = "-o" + str(filename)
            if savepath != '':
                savepath = "-d" + str(savepath)
            other = '--referer="https://www.douyu.com/"'
            cmd_data = aria2c_path + r' -s16 -x10 {} {} {} {} '.format('"' + live_vurl + '"', filename, savepath, other)
            print(r'下载视频文件名：{}\{}'.format(_savepath, _filename))
            print('正在下载直播间{}直播视频，直播流地址：{}'.format(rid, live_vurl))
            print('如果要停止下载，请关闭本窗口即可')
            os.system(cmd_data)
        else:
            print('执行程序所在文件夹aria2c.exe不存在，无法下载')
            return

    except Exception as e:
        print('主播未开播或其他错误')
        return

def crypto_md5(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def get_zhubo_filename(rid_time_info, source):
    try:
        result = re.findall(r'"nickname":"(.*?)"', source)
        nick = result[0]
        return '{}_{}'.format(nick, rid_time_info)
    except Exception as e:
        print(e)
        return ''

'''
过滤文件路径非法字符
'''
def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


if __name__ == '__main__':
    while True:
        roomid = input('请输入斗鱼直播间号：')
        if roomid.strip() == '':
            print('直播间号不能为空...')
            continue
        get_douyu_vurl(roomid)

