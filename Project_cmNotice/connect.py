#!/usr/bin/env python3
"""
author: Corkine Ma (cm@marvinstudio.cn)
summary: 本脚本用于CRON定时执行，从MongoDB数据库中进行数据查询和整合，并且返回一个JSON文件供前端JavaScript调用。
"""
try:
    import pymongo, sys, time, random, datetime, json
    from pprint import pprint
except Exception as e: raise ImportError(e)

class Connection():
    """用来进行数据库连接的类，主要功能为健壮连接过程、从数据库中查询数据，经过计算后
    进行JSON文件的输出以供前端调用"""
    def __init__(self,address,dbname,username,passwd,retry=0):
        """初始化连接过程，尝试连接数据库"""
        code = 0
        for x in range(retry+1):
            code = self.connectDB(address,dbname,username,passwd,retry)
            if code == 1:break
            sleep(3)
        if code != 1 : raise ConnectionError('Connection Failed')
                
    def connectDB(self,address,dbname,username,passwd,retry=False):
        """连接数据库的主要方法"""
        self.connect = pymongo.MongoClient(str(address))
        code,self.logininfo,self.status = self.getDBInfo()
        if code == 1:
            self.db = getattr(self.connect,dbname)
            if self.db.authenticate(username,passwd): pass 
            else: 
                if retry: return 0
                else: raise ValueError("Wrong Authenticate Info")
        else: 
            if retry : return 0 
            else: raise ConnectionError("Can't link to Database")
        return 1
                
    def getDBInfo(self):
        """供connectDB调用：判断数据库连接是否正常"""
        self.dbinfo = self.connect.server_info()
        if type(self.dbinfo) == dict and "ok" in self.dbinfo:
            if self.dbinfo["ok"] == 1:
                return 1,"Login Success",self.dbinfo
            else:
                return 0,"Login Failed",self.dbinfo

    def getStatus(self):
        """供connectDB连接后输出状态信息"""
        print(self.logininfo)
        pprint(self.status)

    def getFuture(self,days=5,today="0-0-0"):
        """供checkDB调用：生成最近n天的date格式和时间戳格式结果"""
        if today == "0-0-0":
            today = datetime.date.today()
        else:
            today = datetime.date(today.split("-")[0],today.split("-")[1],today.split("-")[2])
        delta = datetime.timedelta(days)
        future = delta + today
        today_s = time.mktime(time.strptime(today.ctime()))
        future_s = time.mktime(time.strptime(future.ctime()))
        r_time =  today,today_s,future,future_s

        r_list = []
        for day in range(days):
            delta_i = datetime.timedelta(day)
            future_i = delta_i + today
            future_is = time.mktime(time.strptime(future_i.ctime()))
            r_list.append((future_i,future_is,))

        return r_time,r_list

    def checkDB(self,db=pymongo.database.Collection,days=5):
        """检查一个数据库集合中“booking_date”为今天、明天和n天之内的所有文档，返回三个列表"""
        a,timelist = self.getFuture(days)
        todayList = []; tomorrowList = []; futureList = []
        all = db.find()
        for item in all:
            booking_date = int(item["booking_date"])
            index = 0
            for i in timelist:
                check_date = int(i[1])
                if booking_date == check_date:
                    if index == 0: todayList.append(item)
                    elif index == 1: tomorrowList.append(item)
                    else: futureList.append(item)
                index += 1
        return todayList,tomorrowList,futureList

    def getJSON(self,thelist=[]):
        """供sumJSON将保存在列表中的从数据库中获得的文档经过计算转化为聚合字典"""
        morning_items = []; afternoon_items = []; night_items = [];
        morning_items_c = []; afternoon_items_c = []; night_items_c = [];
        total_num = len(thelist)
        for item in thelist:
            if "booking_time" in item and "booking_id" in item and type(item["booking_time"]) == list:
                for q in item["booking_time"]:
                    if q in [1,2,3,4]:
                        morning_items_c.append(item["booking_id"])
                        if not item["booking_id"] in morning_items:
                            morning_items.append(item["booking_id"])
                    elif q in [5,6,7,8]:
                        afternoon_items_c.append(item["booking_id"])
                        if not item["booking_id"] in afternoon_items:
                            afternoon_items.append(item["booking_id"])
                    elif q in [9,10]:
                        night_items_c.append(item["booking_id"])
                        if not item["booking_id"] in night_items: 
                            night_items.append(item["booking_id"])

        block_total_num_c = len(morning_items_c) + len(afternoon_items_c) + len(night_items_c)
        block_total_num = len(morning_items) + len(afternoon_items) + len(night_items)

        theday_dict = {"total":{"num":block_total_num,"state":"full" if block_total_num_c >= 10 else "almost" if block_total_num >= 6 else "fine"},
        "morning":{"num":len(morning_items),"state":"full" if len(morning_items_c) >= 4 else "almost" if len(morning_items_c) >= 2 else "fine"},
        "afternoon":{"num":len(afternoon_items),"state":"full" if len(afternoon_items_c) >= 4 else "almost" if len(afternoon_items_c) >= 2 else "fine"},
        "night":{"num":len(night_items),"state":"full" if len(night_items_c) >= 2 else "almost" if len(night_items_c) >= 1 else "fine"}}    

        return theday_dict

    def sumJSON(self,todaylist=[],tomorrowList=[],futureList=[]):
        """用来将从数据库中获得的信息整理成JSON格式"""
        item = {}
        item["booking_state"] = {}
        item["booking_state"]["today"] = self.getJSON(todayList)
        item["booking_state"]["tomorrow"] = self.getJSON(tomorrowList)
        item["booking_state"]["week"] = self.getJSON(futureList)
        item["update_time"] = int(time.time())
        return item

if __name__ == "__main__":
    import sys, traceback, os
    if os.path.isfile("data.log"):
        read_log = open("data.log","r")
        log_old = read_log.read().split("\n")
        if len(log_old) > 1000: 
            log = open("data.log","w")
        else: 
            log = open("data.log","a+")
    else: 
        log = open("data.log","a+")
        
    tmp_o = sys.stdout
    tmp_e = sys.stderr
    sys.stdout = log
    sys.stderr = log
    try:
        print("\n\n\n","=="*60,"\n",time.ctime())
        con = Connection("","","",retry=3)
        con.getStatus()
        lab = con.db.lab
        todayList, tomorrowList, futureList = con.checkDB(lab)
        item = con.sumJSON(todayList,tomorrowList,futureList)
        pprint(item)
        r = json.dumps(item)
        f = open("data.json",mode="w")
        f.write(r)
    except:
        print(traceback.format_exc())