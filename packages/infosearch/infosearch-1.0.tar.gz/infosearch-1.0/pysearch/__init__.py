#!/usr/bin/env python		
#coding:utf-8


"""
search api (chinaz,engines,riskiq,virustotal)
~~~~~~~~~~~~~~~~~~~~~
Pysearch is an Search API library, written in Python, tornado
Basic GET usage:
   >>> from pysearch import Engines, Chinaz, Riskiq, VirusTotal
   >>> search = Engines()
   >>> res = yield search.baidu("site:sangfor.com.cn",10,[])
   >>> print len(res),res
"""

# from search.Engines import Engines
# from search.Chinaz import ChinazAPI
# from search.Riskiq import Riskiq
# from search.VirusTotal import VirusTotal

#!/usr/bin/python
#coding=utf8

import sys
reload(sys)
# 重设python编码
sys.setdefaultencoding('utf8')

from search.Engines import Engines
from search.Chinaz import ChinazAPI
from search.Riskiq import Riskiq
from search.VirusTotal import VirusTotal