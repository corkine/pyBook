#!/usr/bn/env python3
import requests,json
import traceback
def loginCCNU(username="",passwd="",suffix=""):
    errmessage = None
    try:
        url = "http://10.220.250.50/0.htm"
        payload = {"DDDDD":"%s"%username,
                "upass":"%s"%passwd,
                "suffix":"%s"%suffix,
                "0MKKey":"123"}
        headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
                    "Content-Type": "application/x-www-form-urlencoded",}
        r = requests.post(url, data=payload ,headers = headers)
        # print(r.text)
        if "您已登录成功，欢迎使用！请不要关闭本页。" in r.text:
            return str(r.status_code),"1",errmessage
        else:
            return str(r.status_code),"0",errmessage
    except:
        errmessage = str(traceback.format_exc())
        return None,"0",errmessage

def loginoutCCNU(username="",passwd="",suffix=""):
    errmessage = None
    try:
        url = "http://10.220.250.50/F.htm"
        headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
                    "Content-Type": "application/x-www-form-urlencoded",}
        r = requests.get(url ,headers = headers)
        # print(r.text)
        if "华中师范大学无线校园网登录" in r.text:
            return str(r.status_code),"0","已注销"
        else:
            return str(r.status_code),"0","返回未知网页"
    except:
        errmessage = str(traceback.format_exc())
        return None,"0",errmessage

def loginoutCCNUWLAN(username="",passwd="",suffix=""):
    errmessage = None
    try: 
        url = "http://securelogin.arubanetworks.com/cgi-bin/login?cmd=logout"
        headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
                    "Content-Type": "application/x-www-form-urlencoded",}
        r = requests.get(url ,headers = headers)
        # print(r.text)
        if "Logout Successful" in r.text:
            return str(r.status_code),"0","已注销"
        else:
            return str(r.status_code),"0","返回未知网页"
    except:
        errmessage = str(traceback.format_exc())
        return None,"0",errmessage

def loginCCNUWLAN(username="",passwd=""):
    errmessage = None
    try:
        url = "http://securelogin.arubanetworks.com/auth/index.html/uauth/index.html/u"
        payload = {"user":"%s"%username,
                "password":"%s"%passwd}
        headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
                    "Content-Type": "application/x-www-form-urlencoded",}
        r = requests.post(url, data=payload ,headers = headers)
        # print(r.text)
        if "External Welcome Page" in r.text:
            return str(r.status_code),"1",errmessage
        elif """Internal Server Error""" in r.text:
            # return str(r.status_code),"1",errmessage
            return str(200),"1",errmessage
        else:
            return str(r.status_code),"0",errmessage
    except:
        errmessage = str(traceback.format_exc())
        return None,"0",errmessage
# 502 0 电缆未连通
# 403 0 用户错误
# 200 0 账户错误
def testNet(number = 1):
    initnumber = number
    errmessage = None
    code = 0
    headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
    if not str(number).isdigit() or number < 1:
        raise ValueError("设置的循环次数错误")
    try:
        while number >= 1:
            try:
                r = requests.get("http://www.blibili.com",timeout=0.8,headers=headers,verify=False)
                code = r.status_code
                # print(r.text)
                # print("refresh" in r.text)
                if r.status_code == 200:
                    if not "Dr.COMWebLoginID_0.htm" in r.text and not """meta http-equiv='refresh' content='1;""" in r.text:
                        break
                    else:
                        code = 0
            except:
                pass
                # print(str(traceback.format_exc()))
            number -= 1
    except:
        errmessage = str(traceback.format_exc())
    finally:
        if errmessage != None:
            return None,"0",errmessage
        elif code != 0:
            return str(code),"1","测试%s次，最终通过测试。"%(initnumber - number + 1)
        else:
            return None,"0","测试%s次，均未通过测试。"%initnumber

def superLogin(username="",passwd="",choose=""):
    username = str(str(username).split("@")[0])
    if choose == (True,False,False,False,False):
        suffix = "0"
    elif choose == (False,False,True,False,False):
        username += "@chinanet"
        suffix = "1"
    elif choose == (False,False,False,True,False):
        username += "@cmcc"
        suffix = "2"
    elif choose == (False,False,False,False,True):
        username += "@unicom"
        suffix = "3"
    else:
        return None,0,"POST的字段不合法，请重试。"
    # print(username,passwd,suffix)
    return loginCCNU(username,passwd,suffix)

if __name__ == "__main__":
    # print(testNet(5))
    # print(loginCCNUWLAN("2017110",""))
    print(loginoutCCNUWLAN("2017110",""))
    # # a,b,c=superLogin("2017110","",(False,False,True,False))
    # # print(a,type(a))
    # print(loginoutCCNU("2017110","","2"))

    # print(testNet(5))
