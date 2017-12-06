#!/usr/bin/env python3
from checkandsend import *
import os
# os.chdir("C:/Users/Administrator/Desktop")

try:
    loadfile = open('daily.setting','r')
    thefile = loadfile.read()
    # print(thefile)
    address=str(thefile.split(",")[0])
    dbaddress=str(thefile.split(",")[1])
    alertaddress = str(thefile.split(",")[4])
    emailaddress=str(thefile.split(",")[2])
    regular=str(thefile.split(",")[3])
except:
    print(address,dbaddress,alertaddress,emailaddress,regular)
    QMessageBox.warning(self,"WARN",'配置读取出错')

result,infomation,list,notedict= checkDaily(address=address+'/',
        regular=regular,dbaddress=dbaddress)
if result == True:
    if list != []:
        print('需要写入的数据',list)
        result_2,result_num,result_txt,processinfo,errinfo= sendMail(list,address=address+'/',emailaddress=emailaddress,
                    dbaddress=dbaddress,preparenotedict=notedict)
        print(result_2,'\n',processinfo,'\n',errinfo,'\n',result_txt)
    else:
        print("成功检索数据，但未发现新数据")
        print(infomation,list)
        try:
            os.startfile(alertaddress)
        except:
            Tk().withdraw()
            warn_last=showwarning("提示","未检测到日记文件，未检测到提醒程序，请检查")
            warn_last

