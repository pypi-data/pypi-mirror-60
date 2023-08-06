#!/usr/bin/python
#coding=utf8

import sys
reload(sys)
# 重设python编码
sys.setdefaultencoding('utf8')

import logging
import tornado.gen
import tornado.ioloop
import urlparse,pprint

from common.asynchttp import AsyncHttp
from search.Engines import Engines
from search.Chinaz import ChinazAPI
import common.utils as Function

headers = Function.get_random_header()
search = Engines(headers = headers)

@tornado.gen.coroutine
def test_bing():
    res = yield search.bing("site:360.cn",10,[])
    logging.info("bing result:%s,%s", len(res), res)

@tornado.gen.coroutine
def test_bing_api():
    res = yield search.bing_api("site:sangfor.com.cn",10,["title"])
    logging.info("bing api result:%s,%s", len(res), res)

@tornado.gen.coroutine
def test_baidu():
    res = yield search.baidu("site:sangfor.com.cn",10,[])
    print len(res),res
    subdomains = []
    for item in res:
        subdomains.append(item[0])
    subdomains = Function.grep_host_from_url_list(subdomains)
    logging.info("baidu result:%s,%s", len(res), res)

@tornado.gen.coroutine
def test_censys():
    proxies = {'proxy_host': '127.0.0.1', 'proxy_port': 1080} #socks5代理
    proxies = { 'proxy_host': '89.187.181.123','proxy_port': 3128} #https代理
    search = Engines()
    #res = yield search.censys(query="parsed.names: sangfor.com.cn",index="certificates",pages=1, fields=['parsed.subject_dn','parsed.names'])
    #res = yield search.censys(query="80.http.get.headers.server: Apache", index="ipv4", pages=1, fields=["ip"])
    res = yield search.censys(query='80.http.get.title: "{0}" or 443.https.get.title: "{0}" or 8080.http.get.title: "{0}"'.format( \
                "精彩回顾_2019深信服创新大会 SANGFOR INNOVATION SUMMIT 2019"), index="ipv4", pages=1, fields=["ip"])
    #res = yield search.censys(query="80.http.get.headers.server: Apache",index="ipv4",fields=["ip"])
    logging.info("censys result:%s,%s", len(res), res)

@tornado.gen.coroutine
def test_fofa():
    res = yield search.fofa(query='domain="sangfor.com.cn"',size=100,fields=["host","title"])
    #res = yield search.censys(query="80.http.get.headers.server: Apache",index="ipv4",fields=["ip"])
    logging.info("fofa result:%s,%s", len(res), res)

@tornado.gen.coroutine
def test_google():
    search = Engines()
    res = yield search.google(query='site:sangfor.com.cn')
    #res = yield search.censys(query="80.http.get.headers.server: Apache",index="ipv4",fields=["ip"])
    logging.info("google result:%s,%s", len(res), res)

@tornado.gen.coroutine
def test_chinaz():
    search = ChinazAPI()
    res = yield search.alexa("sangfor.com.cn")
    logging.info("%s", res)
    res = yield search.query_icp("sangfor.com.cn")
    logging.info("%s", res)
    res = yield search.query_whois("sangfor.com.cn")
    logging.info("%s", res)
    res = yield search.query_whois_reverse("tan2088t@163.com", "Email")
    logging.info("%s", res)
    pprint.pprint(res)
    res = yield search.query_ip("123.206.65.167")
    logging.info("%s", res)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(pathname)s/%(filename)s:%(lineno)d][%(levelname)s]:%(message)s',
                        datefmt='%Y-%m-%d %a %H:%M:%S')

    #>> 导入待测试的
    import time
    start = time.time()
    # test_bing()
    # test_baidu()
    # test_bing_api()
    # test_censys()
    # test_fofa()
    test_chinaz()
    # test_google()
    tornado.ioloop.IOLoop.instance().start()
