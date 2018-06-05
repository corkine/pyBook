#/usr/bin/env python3
# -*- coding:utf8 -*-

import requests
import lxml.etree
import json
import pickle,traceback,shelve,time,sys
# from frame import MetaItem

__title__ = "Bilibili更新Slack提醒实用程序"
__version__ = '0.1.2'
__log__ = """
0.1.0 2018年1月14日 根据ZMZChecker改编而来，使用JSON.LOADS函数而非LXML的XPATH获取列表
0.1.1 2018年1月14日 修复了JSON不能识别Bytes的问题
0.1.2 2018年1月15日 添加了对日志的处理
"""

class BiliChecker:
    """检查Bilibili订阅是否更新，如果更新则推送更新项目到我的Slack中。
    判断的标准是将Bilibili API获取到的JSON文件和本地的数据库文件迭代比较。传递的参数有两个，分别是要检索的数据和Slack的Webhook。
    1、元数据：元数据由多个电视剧项目组成的元组构成，电视剧项目同样是一个元组，包含三个参数，一是自定义
        通知（可以为空），二是RSS地址，三是当前电视剧详情页地址（可以为空）。
    2、Slack的Webhook：前往Slack官方网站注册Slack Team，然后新建一个App，获得Webhook地址，你可以自定义
        该App的通知位置以及通知图标，将此Webhook地址作为参数传递。进一步的自定义传递你可以修改ZMZChecker的uploadtoSlack方法。
    """
    def __init__(self,metadata,autocheck=False,slackurl="",address="bili.cdb",log="check.log"):
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
                sys.stderr = open(log,'w',encoding="utf_8",errors="ignore")
                print("之前的历史记录已清空。\n")
            else:
                sys.stdout = open(log,'a',encoding="utf_8",errors="ignore")
                sys.stderr = open(log,'a',encoding="utf_8",errors="ignore")
            file.close()
        except:
            sys.stdout = open(log,'a',encoding="utf_8",errors="ignore")
            sys.stderr = open(log,'a',encoding="utf_8",errors="ignore")
            print("你创建了日志文件。\n")

        
        print("\n++++++++++++++++++%s++++++++++++++++++\n"%str(time.ctime()))
        print("%s v%s \n%s\n"%(__title__,__version__,__author__))
        print("正在检查项目————————————>\n")

        if address == "":
            raise ValueError("本地数据库为空或无法打开，请检查写权限。")

        # 解析在线数据获取当前RSS信息
        webdb = (self.metadata,)
        for item in self.metadata:
            rss,webaddress = item[1],item[2]
            itemlist = self.getInfo(rss)
            webdb += (itemlist,)
        # .encode(encoding='utf_8',errors='ignore')

        print("数据库地址为：",address)
        outlist = self.checkUpdate(address,webdb)
        # str(outlist)

        print("\n———————————————比较结果输出 ————————————>>>>>>> \n",outlist)

        # 如果发生改变，则使用webhook发送到Slack并更新本地数据库，否则结束流程。
        if self.dirty != False and self.newitem == False:
            for item in outlist:
                text_title = item[1][0] +" "+ item[0][0] + " [" + item[0][1] + " , " + item[0][2] + "] " 
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
        content = content.decode("utf-8")
        data = json.loads(content)
        vlist = data['data']['vlist']
        rlist = []
        for vitem in vlist:
            time_ = time.gmtime(int(vitem['created']))
            rtime = "%s-%s-%s %s:%s"%(time_[0],time_[1],time_[2],time_[3],time_[4])
            item = vitem['title'],vitem['length'],rtime
            rlist += (item,)
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
                list_local = ()
                

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
        """checkDB接受数据库项目元数据，调用网页查询函数，返回两个列表，其一为数据库需更新的字符串文本，其二为准备推送的格式化文本。"""
        result = self.getInfo(rss=meta.info.split(" ")[1])
        litem = []
        for item in result:
            nitem = ""
            for sitem in item:
                nitem += sitem + "::::::"
            litem.append(nitem)
        ritems = []
        pitems = []
        for item in litem:
            if not item in meta.data:
                ritems.append(item)
        for item in litem:
            if not item in meta.data:
                result = item.split("::::::")
                pitems.append(meta.info.split(" ")[0]+" "+result[0]+" "+result[1]+" "+result[2]
                +" "+meta.info.split(" ")[2])
        if len(pitems) > 2:
            pitems = pitems[:2]
            pitems.append(meta.info.split(" ")[0]+" "+"有多条推送，请访问网页查看。"
                +" "+meta.info.split(" ")[2])
        return ritems,pitems,1

if __name__ == "__main__":  


    MOZHE = "[BiliBili墨者更新推送]","https://space.bilibili.com/ajax/member/getSubmitVideos?mid=845921&pagesize=30&tid=0&page=1&keyword=&order=pubdate","https://space.bilibili.com/845921#/video"
    JUZUO = "[张召忠说更新推送]","https://space.bilibili.com/ajax/member/getSubmitVideos?mid=33683045&pagesize=30&tid=0&page=1&keyword=&order=pubdate","https://space.bilibili.com/33683045#/video"
    NUBANI = "[努巴尼守望先锋更新推送]","https://space.bilibili.com/ajax/member/getSubmitVideos?mid=20990353&pagesize=30&tid=0&page=1&keyword=&order=pubdate","https://space.bilibili.com/20990353/#/video"
    ABU = "[阿布垃圾手册更新推送]","https://space.bilibili.com/ajax/member/getSubmitVideos?mid=13127303&pagesize=30&tid=0&page=1&keyword=&order=pubdate","https://space.bilibili.com/13127303/#/"
    SKYTI = "[FROM SKYTI]","https://space.bilibili.com/ajax/member/getSubmitVideos?mid=14527421&pagesize=30&tid=0&page=1&keyword=&order=pubdate","https://space.bilibili.com/14527421/#/"
    AIFOU = "[爱否科技更新推送]","https://space.bilibili.com/ajax/member/getSubmitVideos?mid=7458285&pagesize=30&tid=0&page=1&keyword=&order=pubdate","https://space.bilibili.com/7458285/#/"
    KJMX = "[科技美学更新推送]","https://space.bilibili.com/ajax/member/getSubmitVideos?mid=3766866&pagesize=30&tid=0&page=1&keyword=&order=pubdate","https://space.bilibili.com/3766866?from=search&seid=7562537744771981035#/video"
    
    METADATA = (MOZHE,JUZUO,ABU,NUBANI,SKYTI)

    checker = BiliChecker(autocheck=True,metadata=METADATA,slackurl="https://hooks.slack.com/services/p")  