#!/usr/bin/env python3
#! -*- coding:utf8 -*-

__model__ = "config"
__version__ = "0.0.3"
__log__ = """
0.0.3 2018年3月22日 添加dapentiChecker
"""


# 需要注意，撰写子类时应该在此进行导入，否则lambda函数无法正常工作。

import bilibiliChecker
import zimuzuChecker
import expressChecker
import weatherChecker
import dapentiChecker
"""这是项目的配置文件，包括slack通知Webhook地址以及数据库用户名和密码，在上传Github和服务器前请确认此处信息。"""

data = {
    "model":{
        "bilibili":{
            "type":"bilibili",
            "slack_url":"https://hooks.slack.com/serviceLHp",
            "func": lambda meta:getattr(bilibiliChecker.BiliChecker(metadata={}),"checkData")(meta)
            },
        "zimuzu":{
            "type":"zimuzu",
            "slack_url":"https://hooks.slack.com/servicesghoFX",
            "func": lambda meta:getattr(zimuzuChecker.ZMZChecker(metadata={}),"checkData")(meta)
            },
        "express":{
            "type":"express",
            "slack_url":"https://hooks.slack.com/servicehcDxpwpk9HAX",
            "func": lambda meta:getattr(expressChecker.ExpressChecker(metadata={}),"checkData")(meta)
            },
        "weather":{
            "type":"weather",
            "slack_url":"https://hooks.slack.com/serviceISE7h0pCh",
            "func": lambda meta:weatherChecker.checkWeather(meta),
            "appcode":"bc5cf43ec23e40ccbf7424ec8774252c"
            },
        "dapenti":{
            "type":"dapenti",
            "slack_url":"https://hooks.slack.com/servicgffRpTRJ",
            "func": lambda meta:dapentiChecker.checkTugua(meta)
            },
        "test":{
            "type":"test",
            "slack_url":"https://hooks.slack.com/servicEiejBR3"
            },
        },
    "database":{
        "retry":3,
        "address":"localhost",
        "port":27017,
        "name":["dbname","colname"],
        "auth":["username","passwd"],
        },
}