#!/usr/bin/env python3
#! -*- coding:utf8 -*-
#本模块存放整个框架的基础：MetaItem类和继承自Connection的TransDB类。
#MetaItem类使用了Checker和Updater装饰器，分别用来连接子模块Checker来获取更新数据以及推送
#到各个平台。
import config
import json, requests
from connect import Connection

__model__ = "frame"
__version__ = "0.2.1"

class Checker:
    """装饰器类，用来连接config配置中对应的子模块的Checker类以返回从服务器获取的数据
    所有获取逻辑在子模块Checker类处理，不在此处处理。"""
    def __init__(self,func):
        self.goCheck = func    

    def __call__(self,*args,**kwargs):
        # 在这里截获MetaItem的goCheck调用
        return self.checkSave(*args,**kwargs)
        # return self.goCheck(*args,**kwargs)

    def __get__(self,instance,owner):
        self.metaitem = instance
        # 类似于__init__
        self.metadata = self.metaitem.getData()

        def wrapper(*args,**kwargs):
            return self(instance,*args,**kwargs)
        return wrapper

    def check(self):
        meta = self.metaitem
        func = config.data["model"][meta.type]["func"]
        return func(meta)
        #返回三个参数分别是保存列表、推送列表以及状态

    def checkSave(self,*args,**kwargs):
        writeitems, pushitems, status = self.check()
        ##将获取到的数据（推送、保存、状态更新）写回metaitem类。
        # print("check result is",writeitems,pushitems,status)
        self.metaitem.setPushData(pushitems)
        self.metaitem.setWriteData(writeitems)
        self.metaitem.setStatus(status)

class Updater:
    """装饰器类，用以将MetaItem中的更新项目推送到WebHook和多个平台。"""
    def __init__(self,func):
        self.goPost = func

    def __get__(self,instance,owner):
        self.metaitem = instance

        def wrapper(*args,**kwargs):
            return self(instance,*args,**kwargs)
        return wrapper

    def __call__(self,*args,**kwargs):
        return self.goPush(*args,**kwargs)
        # return self.goPost(*args,**kwargs)

    def toSlack(self, url = "" , text = ""):
        if url == "":
            url = self.url
        payload = {'text':text}
        data = json.dumps(payload)
        response = requests.post(url, data=data)
        return response.text

    def pushData(self,url):
        self.pushlog = ""
        pushlist = self.metaitem.getPushData()
        for x in pushlist:
            for y in range(3):
                r = self.toSlack(url=url,text=x)
                if r == "ok": 
                    self.pushlog = "\n推送消息成功。\n"
                    break
        return self.pushlog
        
    def goPush(self,*args,**kwargs):
        url = self.metaitem.getPushUrl()
        return self.pushData(url=url)


class MetaItem:
    """当从数据库获取信息后，用以构造子类的类。此类仅提供基础接口，所有
    变量不得直接调用。此类方法主要供checker的面向过程流程调用（推送、判断和写入数据库）。

    用以连接配置文件，请修改Checker装饰器。
    用以推送更新，请修改Updater装饰器。
    这个两个装饰器连接config用户配置和子模块"""
    
    def __init__(self,identity:int):
        self.identity = identity

    def getId(self):
        return self.identity
    
    def setSchedule(self,*args,**kwargs):
        """Schedule API 用以检查是否在当前时段进行检查,调用后"""
        if "rate" in kwargs:
            self.rate = kwargs["rate"]

    def setNow(self,now:bool):
        if isinstance(now,bool):
            self.isnow = now
        else:
            raise TypeError("setNow: Type is not bool")

    def setData(self,data):
        """TransDB API 用以初始化数据信息"""
        self.data = data["data"]
        self.type  = data["type"]
        self.info = data["info"]
        self.isnew = True if data["status"] == -1 else False
        self.name = data["name"]
        self.setPushUrl(config.data["model"][self.type]["slack_url"])

    def isNow(self):
        """Checker API 用以返回是否当前时间需要检查，
        如果是，则进一步从数据库获取信息并开始检查"""
        return self.isnow

    def getData(self):
        """Checker API 用以获取元数据并进行检查"""
        return self.data

    def setPushUrl(self,url):
        """Updater API 用以确定是否需要推送"""
        self.pushurl = url

    def getPushUrl(self):
        """Updater API"""
        return self.pushurl

    @Checker
    def goCheck(self,*args,**kwargs):
        pass

    @Updater
    def goPost(self,*args,**kwargs):
        pass

    def setPushData(self,pdata):
        """Checker API 用以保存需要推送的信息"""
        if self.isnew:
            pdata = ["[%s] 已保存设置，Slack将会推送其更新消息。"%(self.name)]
        self.pushdata = pdata

    def getPushData(self):
        """Update API调用"""
        return self.pushdata
    
    def setWriteData(self,wdata):
        """Checker API 用以保存需要写入数据库的信息"""
        self.writedata = wdata

    def getWriteData(self):
        """保存到数据库API接口"""
        return self.writedata

    def setStatus(self,status:int):
        """Checker API 用以保存项目状态信息"""
        self.status = status

    def getStatus(self):
        return self.status

    def isNew(self):
        return self.isnew

    def setNew(self,new:bool):
        if isinstance(new,bool):
            self.isnew = new
        else:
            raise TypeError("setNew Error")
        


        
class Schedule:
    """判断rate以及时间来控制是否传递data以开始检查，不涉及停止推送的项目
    停止推送的项目甚至不构造metaitem项目。"""
    
    def __init__(self,metaitem:MetaItem):
        self.metaitem = metaitem
        
        # self.saveSchedule()

    def checkSchedule(self):
        if hasattr(self.metaitem,"isnew"):
            isnew = self.metaitem.isNew()
            if isnew:
                return True
        if hasattr(self.metaitem,"rate"):
            rate_str = self.metaitem.rate
            if not str(rate_str).startswith("@"):
                return self.rateNow(rate=rate_str)
            else:
                if not "@" in rate_str[1:]:
                    return self.timingNow(rate=rate_str)
                else:
                    return self.limitRateNow(rate=rate_str)
            # print("\t the meta item is now? ",now)
            # 此处注释以保证所有项目均通过检查开始执行更新检测
            # return True
        else:
            raise AttributeError("No attr named rate")
    
    def rateNow(self,rate=None,now=None):
        """根据查询项的查询频率判断当前时间是否要进行项目的查询"""
        if not rate:
            raise ValueError("From isNow function: You must intro a rate.")
        if not now:
            now = self.nowIs()
        hour = []
        for x in range(24):
            x = str(x)
            if len(x) == 1:
                x = "0" + x
            hour.append(x)
        minute = []
        for x in range(60):
            x = str(x)
            if len(x) == 1:
                x = "0" + x
            minute.append(x)
        times = []
        for x in hour:
            for y in minute:
                times_sum = x + y
                times.append(times_sum)
        count = 0
        for x in times:
            if count % rate == 0:
                # print(x,count)
                if x == now:
                    return True
            count += 1
        return False
    
    def timingNow(self,rate:"@17:20"):
        if not rate.startswith("@"):
            raise ValueError("timeingNow: structure Error")
        rate = rate[1:].split(":")
        hour = rate[0]
        mint = rate[1]
        if int(hour) > 23 or int(hour) < 0 or int(mint) > 59 or int(mint) < 0:
            raise ValueError("timeingNow: 无法解析时间")
        if len(hour) == 1:
            hour = "0"+str(hour)
        else:
            hour = str(hour)
        if len(mint) == 1:
            mint = "0"+str(mint)
        else:
            mint = str(mint)
        rate = hour + mint
        if rate == self.nowIs():
            return True
        else:
            return False

    def limitRateNow(self,rate:"@17:20@20:30@5"):
        try:
            _, start_time, end_time, rate_real = rate.split("@")

            start_item = start_time.split(":")
            hour = start_item[0]
            mint = start_item[1]
            if int(hour) > 23 or int(hour) < 0 or int(mint) > 59 or int(mint) < 0:
                raise ValueError("timeingNow: 无法解析时间")
            if len(hour) == 1:
                hour = "0" + hour
            if len(mint) == 1:
                mint = "0" + mint
            start_time = hour + mint

            end_item = end_time.split(":")
            hour = end_item[0]
            mint = end_item[1]
            if int(hour) > 23 or int(hour) < 0 or int(mint) > 59 or int(mint) < 0:
                raise ValueError("timeingNow: 无法解析时间")
            if len(hour) == 1:
                hour = "0" + hour
            if len(mint) == 1:
                mint = "0" + mint
            end_time = hour + mint

            rate = int(rate_real)
        except:
            raise ValueError("timeingNow: structure Error")

        if self.nowIs() >= start_time and self.nowIs() <= end_time:
            return self.rateNow(rate=rate)
        else:
            return False
        
    def nowIs(self):
        import time
        hm = time.strptime(time.ctime())[3:5]
        if len(str(hm[0])) == 1:
            hour = "0" + str(hm[0])
        else:
            hour = str(hm[0])
        if len(str(hm[1])) == 1:
            mint = "0" + str(hm[1])
        else:
            mint = str(hm[1])
        now = hour + mint
        return now
        
        

class TransDB(Connection):
    """用于数据库的连接、查询和写入以及修改，继承自Connection类"""
    
    def __init__(self,address,dbname,tablename,username,passwd,retry):
        super().__init__(address=address,dbname=dbname,username=username,passwd=passwd,retry=0)
        self.notice = getattr(self.db,tablename)

    def queryInfo(self,limit=True):
        if limit:
            result = self.notice.find(filter={"status":{"$in":[1,-1]}},projection={"_id":False,"id":True,"rate":True,"status":True})
        else:
            result = self.notice.find(filter={"status":{"$in":[1,-1]}})
        result = list(result)
        return result

    def queryOne(self,filter={}):
        result = self.notice.find(filter)
        result = list(result)[0]
        return result

    def writeData(self,filter={},data=[]):
        if filter == {} or data == []:
            return 0
        r = self.notice.update_many(filter,{"$push":{"data":{"$each":data}}})
        if r.modified_count == 1:return 1
        else: return 0

    def endItem(self,filter={}):
        if filter == {}:
            return 0
        r = self.notice.update_one(filter,{"$set":{"status":0}})
        if r.modified_count == 1: return 1
        else: return 0

    def startItem(self,filter={}):
        if filter == {}:
            return 0
        r = self.notice.update_one(filter,{"$set":{"status":1}})
        if r.modified_count == 1: return 1
        else: 
            return 0

if __name__ == "__main__":
    pass