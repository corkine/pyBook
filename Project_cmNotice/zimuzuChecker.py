#/usr/bin/env python3
# -*- coding:utf8 -*-

import requests
import lxml.etree
import json
import pickle,traceback,shelve,time,sys

__title__ = "字幕组美剧更新Slack提醒实用程序"
__version__ = '1.8.1'
__log__ = """Linux下编码为UTF8，和Windows的ANSI不同，因此在写入Log时可能出现一些问题，造成通知问题
0.5.0 2018年1月10日 添加此程序
1.0.0 2018年1月12日 修正了Linux下的文件编码问题，修正了新项目添加推送到Slack的问题。仍存在的Bug有：从本地数据库检索可能有问题
1.2.0 2018年1月12日 修正了增删请求数据造成的本地数据更新问题。解决了没有数据库文件时检索数据特定键值出现的错误。
1.3.0 2018年1月15日 添加了对于日志文件的检查和处理
1.8.0 2018年1月20日 添加了对于来自同一项目的多条（>3条）通知的处理。
1.8.1 2018年3月17日 添加了对于获取数据出错的处理方法。
"""

class ZMZChecker:
    """检查字幕组网站的某个电视剧的RSS订阅是否更新，如果更新则推送更新项目到我的Slack中。
    判断的标准是将RSS的XML文件和本地的数据库文件迭代比较。传递的参数有两个，分别是要检索的数据和Slack的Webhook。
    1、元数据：元数据由多个电视剧项目组成的元组构成，电视剧项目同样是一个元组，包含三个参数，一是自定义
        通知（可以为空），二是RSS地址，三是当前电视剧详情页地址（可以为空）。
    2、Slack的Webhook：前往Slack官方网站注册Slack Team，然后新建一个App，获得Webhook地址，你可以自定义
        该App的通知位置以及通知图标，将此Webhook地址作为参数传递。进一步的自定义传递你可以修改ZMZChecker的uploadtoSlack方法。
    """
    def __init__(self,metadata,autocheck=False,slackurl="",address="zmz.cdb",log="check.log"):
        self.metadata = metadata
        self.dirty = False
        self.delerr = False
        self.newitem = False
        self.url = slackurl
        if autocheck:
            self.goCheck(address=address,log=log)

    def goCheck(self,address="",log=""):
        '''进行项目检查，结果输出到标准流，你可以在这里自定义截获输出到某文件进行保存。'''
        tmp_out = sys.stdout
        tmp_err = sys.stderr
        if log == "":
            raise ValueError("LOG文件无法打开，请检查程序所在文件夹写权限")

        try:
            file = open(log,"r",encoding="utf_8",errors="ignore")
            checklen = file.read()
            if len(checklen) > 10000:
                sys.stdout = open(log,'w',encoding="utf_8",errors="ignore")
                sys.stderr = open(log,"w",encoding="utf_8",errors="ignore")
                print("之前的历史记录已清空。\n")
            else:
                sys.stdout = open(log,'a',encoding="utf_8",errors="ignore")
                sys.stderr = open(log,"a",encoding="utf_8",errors="ignore")
            file.close()
        except:
            sys.stdout = open(log,'a',encoding="utf_8",errors="ignore")
            sys.stderr = open(log,"a",encoding="utf_8",errors="ignore")
            print("你创建了日志文件。\n")
        
        print("\n++++++++++++++++++%s++++++++++++++++++\n"%str(time.ctime()))
        print("%s v%s \n%s\n"%(__title__,__version__,__author__))
        print("正在检查项目————————————>\n")

        if address == "":
            raise ValueError("本地数据库为空或无法打开，请检查写权限。")

        # 解析XML获取当前RSS信息
        webdb = (self.metadata,)
        for item in self.metadata:
            rss,webaddress = item[1],item[2]
            itemlist = self.getInfo(rss)
            webdb += (itemlist,)

        # print("互联网库为",webdb)
        # 和本地数据进行比较
        # address = "zmz.cdb"
        print("数据库地址为：",address)
        outlist = self.checkUpdate(address,webdb)

        if len(outlist) > 3:
            checklist = outlist
            checklist_out = []
            metalist = self.metadata
            ordereddict = {}
            for item in metalist:
                ordereddict[item] = []
                for subitem in checklist:
                    # print("SUBITEM",subitem)
                    if subitem[1] == item:
                        ordereddict[item].append(subitem[0])
            # print("ORDEREDDICT",ordereddict)

            for item in ordereddict:
                if len(ordereddict[item]) > 2:
                    ordereddict[item] = ordereddict[item][:2]
                    ordereddict[item].append("有多条推送，请登陆网页查看。")

            for item in ordereddict:
                if len(ordereddict[item]) != 0:
                    for subitem in ordereddict[item]:
                        checklist_out.append((subitem,item,))

            outlist = checklist_out


        print("\n———————————————比较结果输出 ————————————>>>>>>> \n",outlist)
        text_title = ""
        # 如果发生改变，则使用webhook发送到Slack并更新本地数据库，否则结束流程。
        if self.dirty != False and self.newitem == False:
            for item in outlist:
                text_title = item[1][0] +" "+ item[0]
                webaddress = item[1][2]
                text = text_title + " " +webaddress
                self.uploadtoSlack(text)
            print("正在更新——————————> ",text_title)
            self.updateLocalDB(address,webdb)
            print("通知已发送。")
        else:
            if self.newitem == True or self.delerr == True:
                self.updateLocalDB(address,webdb)
                print("检测到新项目添加/修改，已进行数据库保存，但没有将内容发送到Slack。")
            print("\n==================没有数据需要更新，完毕。===================\n")

        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = tmp_out
        sys.stderr = tmp_err

    def getInfo(self, rss=""):
        '''对网站地址进行解析，获得XML文件，根据XPATH规则获取条目，以列表形式返回'''
        response = requests.get(rss)
        content = response.content
        xml = lxml.etree.XML(content)
        clist = xml.xpath('//channel/item/title')
        rlist = []
        for x in clist:
            if "中英字幕" in x.text:
                rlist.append(x.text)
        return rlist


    def uploadtoSlack(self, text = ""):
        '''将文本打包为json格式，使用Webhook的方式POST到Slack的Webhook，返回状态码'''
        url = self.url
        payload = {'text':text}
        data = json.dumps(payload)
        response = requests.post(url, data=data)
        return response


    def checkUpdate(self, address="", webdb = None):
        '''传递两个参数，分别是本地数据地址，以及要进行比较的数据。遍历列表检查更新，如果发现要比较的数据不存在于本地数据，
        则添加到一个列表，最后将其返回'''
        try:
            db_local = shelve.open(address)
            db = db_local["info"]
            # print("+++++++++++++++++++++++++++++OLDDB",db)
            db_local.close()
        except Exception as _err:
            print("本地数据库为空,已新建数据库")
            db = db_local["info"] = webdb
            self.newitem = True
            db_local.close()
            return []
            

        # 此部分目的在于更新本地数据库，删除请求数据中没有的，但是本地数据中有的条目。
        number_web = len(webdb[0])
        print("在线元数据长度：",number_web)
        number_local = len(db[0])
        print("本地元数据长度：",number_local)
        if number_local > number_web:
            print("检测到本地数据库存在无效条目，已删除。")
            db_meta = db[0][:number_web]
            db_head = db[1:number_web+1]
            db = (db_meta,) + db_head
            self.delerr = True
            print("处理后的在线元数据长度和总长度",len(webdb[0]),len(webdb))
            print("处理后的本地元数据长度和总长度(未保存前的状态)",len(db[0]),len(db))


        outlist = []
        for id_ in range(number_web):
            id_ = id_ + 1
            try:
                list_local  = db[id_]
                if db[0][id_-1][1] != webdb[0][id_-1][1]:
                    raise ValueError("项目不匹配")
            except:
                self.newitem = True #刚添加RSS的时候肯定没更新，所以必然获得了所有的数据，这个更新量发送到Slack
                # 是很恐怖的，所以直接跳过保存到Slack这一步，下次再更新的时候才推送通知到Slack。
                list_local = ''
                

            list_web = webdb[id_]

            for item_web in list_web:
                if not item_web in list_local:
                    outlist.append((item_web,webdb[0][id_ - 1]))
                    self.dirty = True
        return outlist
    
    
    def updateLocalDB(self, address = "", webdb = None):
        '''更新本地文件，传入参数为本地文件地址以及要写入的数据'''
        try:
            db = shelve.open(address)
            db["info"] = webdb
        except Exception as _err:
            print("Save Pickle Failed. \n%s"%_err)
        finally:
            db.close()
            print("\n","="*20 + "更新本地文件成功!" + "="*20,"\n")
            print("处理后的本地元数据长度和总长度(更新并保存)",len(webdb[0]),len(webdb))

    def checkData(self,meta):
        import re
        rule = re.compile("[Ss]\d+[Ee]\d+")
        # print("rss is",meta.info.split(" ")[1])
        try:
            result = self.getInfo(rss=meta.info.split(" ")[1])
        except:
            raise BufferError("%s: XML信息不能被正确解析"%meta.name)
        slist = []
        wlist = []
        plist = []
        p2list = []
        # print("result is",result)
        for item in result:
            if "中英字幕" in item:
                slist.extend(rule.findall(item))
        # print("slist list is",slist)
        for item in slist:
            if not item in meta.data:
                wlist.append(item)
        # print("wlist is", wlist)
        for item in wlist:
            if not item in meta.data:
                plist.append(item)
        # print("plist is",plist)
        for item in plist:
            res = meta.info.split(" ")[0] + " 现已更新至 " + item + "，快去看看吧。 " + meta.info.split(" ")[2]
            p2list.append(res)
        if len(p2list) > 2:
            p2list = p2list[:2]
            moreinfo = meta.info.split(" ")[0] + " 有多条推送，请前往网页查看。" + meta.info.split(" ")[2]
            p2list.append(moreinfo)
        # print("the wlist bilibili will send is",wlist)
        return wlist,p2list,1

if __name__ == "__main__":  

    SHIELD = "[神盾局特工更新]","http://diaodiaode.me/rss/feed/30675","http://www.zimuzu.tv/resource/30675"
    DESCOVERY = "[星际迷航更新]","http://diaodiaode.me/rss/feed/35640","http://www.zimuzu.tv/resource/35640"
    MIND = "[犯罪心理更新]","http://diaodiaode.me/rss/feed/11003","http://www.zimuzu.tv/resource/11003"
    #TIANFU = "[天赋异禀更新]","http://diaodiaode.me/rss/feed/35668","http://www.zimuzu.tv/resource/35668"
    XDYZ = "[相对宇宙更新]","http://diaodiaode.me/rss/feed/35840","http://www.zimuzu.tv/resource/35840"
    #CARBON = "[副本更新]","http://diaodiaode.me/rss/feed/35833","http://www.zimuzu.tv/resource/35833"
    HL = "[国土安全更新]","http://diaodiaode.me/rss/feed/11088","http://www.zimuzu.tv/resource/11088"

    METADATA = (SHIELD,DESCOVERY,MIND,XDYZ,HL)
    # METADATA = (SHIELD,DESCOVERY,MIND,TIANFU)
    # print(METADATA)

    # data = ()
    # for item in open("checkitem.txt",'r'):
    #     item = item.replace("\n",'')
    #     if item != None and item != "" and len(item) != 0:
    #         items = item.split(",")
    #         if len(items) != 3:
    #             raise ValueError("数值不匹配")
    #         else:
    #             items_set = ()
    #             for x in items:
    #                 items_set += (x,)
    #             data += (items_set,)
    # # print(data)
    # # 需要注意，checkitem文件逗号为英文逗号，并且逗号前后没有间隔，换行符之前没有空白。
    # # print("相等？",data == METADATA)
    # METADATA = data




    checker = ZMZChecker(autocheck=True,metadata=METADATA,slackurl="https://hooks.slack.com/services/T3P92AF6F/B")  