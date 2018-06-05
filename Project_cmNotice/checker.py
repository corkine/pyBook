#!/usr/bin/env python3
"""此模块用来进行各项目的检查。但不涉及具体检查方式和API调用，而是直接运行子模块获得一个返回值。
"""

__model__ = "checker"
__version__ = "0.2.5"
__log__ = """
0.0.0 START AT 2018-03-03
0.0.1 2018-03-04 服务器测试部署本
0.0.2 2018-03-05 添加了config文件，用以保存数据库密码、数据结构类型以及函数调用方法，这样的话，本模块就无需再进行更改。
顺便删除了在每个项目中进行频率判定的代码，现在在metalist即进行判断。删除了在每个项目中判断status==1的代码，
因为在数据库获取信息时即可过滤status!=1的项目。
0.0.3 2018-03-05 更改了日志记录策略，如果没有更新或者没有错误消息则不记录日志。如果在数据库发现一条新记录(状态为-1)，则不会默认推送
前三条消息，而是推送一条“将会继续保持更新的消息”,然后将此条目标记为开始。
0.0.4 2018-03-05 修正了一个bug，现在新添加的项目会立即收到测试推送的通知，而不是等到rate到达的时候
0.0.5 2018-03-07 服务器自动化更新版本，上线测试
0.0.6 2018-03-14 程序重构，基于完全的OOP模型，添加了几个装饰器方法。
0.0.7 2018-03-15 单元测试和bug修复
0.2.0 2018-03-15 上线测试。修正了新添加项目的推送时间判断问题。
0.2.1 2018-03-15 修正了打印空白行日志的问题，添加了定时范围检查类型
0.2.2 2018-03-16 修正了有推送但是没有保存信息下保存导致的报错信息
0.2.3 2018-03-17 修正了关于检索数据出错的日志记录
0.2.4 2018-03-18 修复了当没有push时错误调用getwritedata发生的错误。
0.2.5 2018-03-19 修复了没有goPost就调用getStatus发生的错误。"""

import time,traceback,sys,pymongo
from frame import MetaItem, Schedule, Checker, Updater, TransDB
import config


def linkToDatabase():
    address, user, passwd, retry, dbname, tablename= config.data["database"]["address"],config.data["database"]["auth"][0], \
    config.data["database"]["auth"][1],config.data["database"]["retry"], \
    config.data["database"]["name"][0],config.data["database"]["name"][1]
    check = TransDB(address, dbname, tablename, user, passwd, retry)
    metalist = check.queryInfo(limit=True)
    # 第一次获取的时候只需要获取identity和rate两个值。
    return check,metalist

def controlLog(log):
    rlog = ""
    try:
        file = open(log,"r",encoding="utf_8",errors="ignore")
        checklen = file.read()
        if len(checklen) > 20000:
            sys.stdout = open(log,'w',encoding="utf_8",errors="ignore")
            sys.stderr = open(log,'w',encoding="utf_8",errors="ignore")
            rlog = "之前的历史记录已清空。\n"
        else:
            sys.stdout = open(log,'a',encoding="utf_8",errors="ignore")
            sys.stderr = open(log,'a',encoding="utf_8",errors="ignore")
        file.close()
    except:
        sys.stdout = open(log,'a',encoding="utf_8",errors="ignore")
        sys.stderr = open(log,'a',encoding="utf_8",errors="ignore")
        rlog = "你创建了日志文件。\n"
    finally:
        return rlog

def readyToCheck(check,metalist):
    sublog = ""; subhead = ""
    if metalist != []:
        subhead += "\n\n++++++++++++++++++%s++++++++++++++++++\n\n"%str(time.ctime())
        subhead += "【主进程】readyToCheck:项目进程准备就绪————————————>\n"
        now_metalist = []

        for meta in metalist:
            metaitem = MetaItem(meta["id"])
            metaitem.setNew(True if meta["status"] == -1 else False)
            metaitem.setSchedule(rate=meta["rate"])
            if Schedule(metaitem).checkSchedule():
                now_metalist.append(metaitem)

        for metaitem in now_metalist:
            try:
                log = mainCheck(metaitem,check)
                sublog += str(log)
            except:
                print("【子进程】mainCheck:在获取数据或者保存数据时出错，错误如下：\n")
                print(str(traceback.format_exc()))

        # 如果子项目没有更新则不返回数据
        if sublog == "": return ""
        else: return subhead + sublog 
    else: return ""

def mainCheck(meta:MetaItem,db:TransDB):
    log = ""
    """接受项目元信息、数据库句柄以进行面向过程的更新查询、数据库写入、推送通知以及项目终止和日志记录类"""
    trans = db
    isset = False; ischeck = False
    data = trans.queryOne({"id":meta.getId()})
    meta.setData(data)
    isset = True
    log += "\n====================正在处理：%s/%s/%s====================\n"%(meta.name,meta.type,meta.rate)
    log += "\n基本信息：\n%s\n"%meta.info
    
    #进行数据检查
    try:
        meta.goCheck()
        ischeck = True
    except:
        log += "【子进程】mainCheck:在检索本项目数据时出错，错误如下：\n"
        log += str(traceback.format_exc())

    #进行数据推送
    pushlog = ""; pushcode = 0
    try:
        pushlog = meta.goPost()
    except:
        pushlog += "\n[在推送时发生错误]，错误详情如下：\n"
        pushlog += "\n%s\n"%traceback.format_exc()
    finally:
        if "推送消息成功" in pushlog: pushcode = 1
        else: pushcode = 0
        log += pushlog

    # 进行数据库保存
    savelog = ""; savecode = 0
    if pushcode == 1:
        # meta.getWriteData()面向过程，当pushcode为0，也就是前一阶段数据尚未处理完毕的时候，不要调用依赖上一阶段处理结果的函数。
        wdata = meta.getWriteData()
        # 当新建项目时，存在有推送消息但是不需要写回数据库的情况
        if wdata != []:
            try:
                code = trans.writeData({"id":meta.identity},wdata)
                if code != 1:raise pymongo.errors.InvalidOperation("pymongo无法保存此项目，可能是没有新数据或者网络连接失败")
                savelog += "\n保存到数据库成功。\n"
            except:
                savelog += "\n[在保存时发生错误]，错误详情如下：\n"
                savelog += "\n%s\n"%traceback.format_exc()
            finally:
                if "保存到数据库成功" in savelog: savecode = 1
                else: savecode = 0
                log += savelog
        else: pass

    # 有时候需要开始处理计划/当开始计划时，只有最初从数据库获取信息时知道，而在checker进行检查后返回的status已经改变。
    startlog = ""
    if isset == True and meta.isNew():
        try:
            meta_dict = {"id":meta.identity}
            code = trans.startItem(filter=meta_dict)
            if code != 1 : raise pymongo.errors.InvalidOperation("pymongo无法开始此项目")
            startlog += "\n已开始此项目。\n"
        except:
            startlog += "\n[在开始时发生错误]，错误详情如下：\n"
            startlog += "\n%s\n"%traceback.format_exc()
        finally:
            log += startlog

    # 这里有时候需要更改以终止计划
    endlog = ""
    if ischeck == True and meta.getStatus() == 0:
        try:
            meta_dict = {"id":meta.identity}
            code = trans.endItem(filter=meta_dict)
            if code !=1:raise pymongo.errors.InvalidOperation("pymongo无法终止此项目")
            endlog += "\n已终止此项目。\n"
        except:
            endlog += "\n[在终止时发生错误]，错误详情如下：\n"
            endlog += "\n%s\n"%traceback.format_exc()
        finally:
            log += endlog

    log += "\n整体流程处理完毕。\n"
    if endlog == "" and startlog == "" and pushcode == 0:
        log = "" #如果没有任何更新则不返回数据
    return log

def main(log="check.log"):
    tmp_out = sys.stdout
    tmp_err = sys.stderr

    # 测试时请注释此处以保证输出不重定向文件
    rlog = controlLog(log)
    if rlog != "":print(rlog)

    try:
        check, metalist = linkToDatabase()
    except:
        print("\n\n++++++++++++++++++%s++++++++++++++++++\n\n"%str(time.ctime()))
        print("【主进程】linkToDatabase:在连接数据库并获取元数据时出错，错误如下：\n")
        print(str(traceback.format_exc()))
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = tmp_out
        sys.stderr = tmp_err
        return 0
        
    try:
        rlog = readyToCheck(check,metalist)
        if rlog != "":print(rlog)
    except:
        print("\n\n++++++++++++++++++%s++++++++++++++++++\n\n"%str(time.ctime()))
        print("【主进程】readyToCheck:在检索和更新数据时出错，错误如下：\n")
        print(str(traceback.format_exc()))
        
    sys.stdout.close()
    sys.stderr.close()
    sys.stdout = tmp_out
    sys.stderr = tmp_err
    return 1

if __name__ == "__main__":  

    main()
