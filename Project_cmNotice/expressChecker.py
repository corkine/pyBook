#/usr/bin/env python3
# -*- coding:utf8 -*-

import requests
import lxml.etree
import json
import pickle,traceback,shelve,time,sys

__title__ = "快递更新查询程序"
__version__ = '0.0.2'
__log__ = """
0.0.1 2018年3月4日
0.0.2 2018-03-07 修正了数据尚未更新的404错误，返回空列表
"""

class ExpressChecker:
    """检查快递更新状态的类
    """
    def __init__(self,metadata):
        self.metadata = metadata

    def getInfo(self, rss=""):
        '''从网络API获取信息'''
        response = requests.get(rss)
        content = response.content
        xml = lxml.etree.XML(content)
        clist = xml.xpath('//channel/item/title')
        rlist = []
        for x in clist:
            if "中英字幕" in x.text:
                rlist.append(x.text)
        return rlist

    def checkExpress(self,number='12045301',type_='auto',appcode='4ec8774252c'):
        try:
            import urllib.request
            host = 'http://jisukdcx.market.alicloudapi.com'
            path = '/express/query'
            method = 'GET'
            appcode = appcode
            querys = 'number=' + number + '&type=' + type_
            bodys = {}
            url = host + path + '?' + querys
            request = urllib.request.Request(url)
            request.add_header('Authorization', 'APPCODE ' + appcode)
            response = urllib.request.urlopen(request)
            content = response.read()
            if (content):
                dict = content.decode('utf-8','ignore')
                return 1,'查询成功',dict
            else:
                return 0,'错误，未返回数据',''
        except:
            return 0, "错误，未返回数据", ""

    def checkData(self,meta):
        import json
        for x in range(3):
            code,_,result = self.checkExpress(number=str(meta.info).strip())
            if code == 1: break
        if code == 0: return [],[],1
        result = json.loads(result)
        ilist = result["result"]["list"]
        company = result["result"]["type"]
        issign = result["result"]["issign"]
        wlist = []
        plist = []
        p2list = []
        for item in ilist:
            suminfo = str(item["time"] + "::::::" + item["status"]).strip()
            wlist.append(suminfo)
        for item in wlist:
            if not item in meta.data:
                plist.append(item)
        for item in plist:
            p2list.append("[快递状态更新]"+" %s:\n"%meta.name + item.split("::::::")[0]+ " " +item.split("::::::")[1] + " | %s:%s"%(company,meta.info))
        if len(p2list) > 0:
            p2list = p2list[0]
        if isinstance(p2list,str):
            p2list = [p2list]
        #因为快递只需要更新最近状态即可 必须返回数组，因为需要遍历
        return wlist,p2list,0 if issign == "1" else 1

if __name__ == "__main__":  
    from pprint import pprint

    meta = {
        "name":"孔夫子书籍",
        "id":24322234,
        "status":1,
        "rate":30,
        "type":"express",
        "info":"5083078",
        "data":[""]
    }
    checker = ExpressChecker(metadata=meta)
    a,b,c = checker.checkData(meta=meta)  
    print(a,b,c)