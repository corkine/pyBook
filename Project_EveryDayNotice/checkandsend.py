#!/usr/bin/env python3
import sys,os,traceback,shelve
try:
    from docx import *
except:
    raise ImportError("You need install Pydocx by run 'pip install python-docx' \
                        in Bash/CMD if you have python3 and pip installed")
try:
    from tkinter import Tk
    from time import sleep
    from tkinter.messagebox import showwarning
    import win32com.client as win32
except Exception as err_:
    raise ImportError("Maybe you do not have PyPiWin32 components installed, please \
                    use 'python -m pip install pypiwin32' to install and try again. %s"%err_)


def checkDaily(address='',regular='',dbaddress=''):
    '''address地址使用Unix风格斜杠，包含最后斜杠，为日记文件夹地址，regular为正则语法，dbaddress为数据库地址
        精确到文件
    '''
    try:



        #读取文件列表，更新文件信息到词典，保存词典，从词典中读取已有信息，交叉对比文件列表更新，如果存在更新，更新词典并保存，并且触发发送到Outlook这一任务
        import os,re,time,shelve
        # notelist=os.listdir('E:/Windows_WorkFolder/工作文件夹')
        notelist=os.listdir(address)
        # reobj=re.compile(r"\b201\d年\d+月.*?日.*?.doc.*?",re.S)
        reobj=re.compile(regular,re.S)
        notedict={}
        # db_old=shelve.open('E:/Windows_WorkFolder/工作文件夹/daily_update_data/update_data')
        db_old=shelve.open(dbaddress)
        for key in db_old:
            notedict[key]=db_old[key]

        showbefore = '\n这是之前词典中保存的数据======================>\n%s'%notedict


        notefile_list=[]


        for x in notelist[:]:
            if reobj.search(x):
                if x not in notedict:
                    the_time=str(time.localtime()[0])+'/'+str(time.localtime()[1])+'/'+str(time.localtime()[2])+' '+str(time.localtime()[3])+":"+str(time.localtime()[4])
                    notedict[x]='Update at '+ the_time
                    notefile_list.append(str(x))
                else:
                    pass
            else:
                pass
        showafter = '\n这是准备写入词典中的数据======================>\n%s'%notedict

        return True,'%s\n\n%s'%(showbefore,showafter),notefile_list,notedict
    except:
        return False,traceback.format_exc(),notefile_list,notedict


def sendMail(notefile_list=[],address='',emailaddress='',dbaddress='',preparenotedict={}):
    '''存在两种错误，文件读不出来，邮件发不出去，这两种错误不触发异常，只需要记录并且给用户弹窗就好，但至于其他错误，比如数据库无法读写，则强制报错
        程序接受一个文件夹地址参数，此参数包含最后的斜杠，使用Unix风格斜杠；emailaddress为邮件地址，dbaddress为数据库文件地址；notefile_list为需要写入的目录
    '''
    processinfo = ''
    errinfo = ''
    try:
        if notefile_list:
            for notefile_real in notefile_list:
                processinfo += "\n=====================================[%s] PROCESSINFO====================================\n"%notefile_real
                errinfo += "\n=====================================[%s] ERRORINFO====================================\n"%notefile_real
                send_successful=False
                notefile=str(address+notefile_real)
                try:
                    document=Document(notefile)
                    text_article = [ paragraph.text for paragraph in document.paragraphs]
                except Exception as _err:
                    processinfo += "\n读取错误，详情请查看ERRORINFO。\n"
                    errinfo += "\n检测到的文件读取出错，因此不进行更新，已跳过此文件。\n详细信息:%s\n"%_err
                    continue

                mail_text_body=''
                mail_subject=str(text_article[:1])[2:-2]
                print('正在处理===>',mail_subject) #调试打开
                for pargh in text_article[1:]:
                    mail_text_body+=pargh+'\n'


                def outlook():
                    app='Outlook'
                    olook=win32.gencache.EnsureDispatch('%s.Application'%app)
                    mail=olook.CreateItem(win32.constants.olMailItem)
                    recip=mail.Recipients.Add(emailaddress)
                    subj=mail.Subject=mail_subject
                    mail.Body=mail_text_body
                    mail.Send()
                    olook.Quit()

                cpobject=document.core_properties
                def runprop(attr,cpobject,processinfo):
                    try:
                        val_=getattr(cpobject,attr)
                        if val_ !='':processinfo += (attr,'==>',val_)
                    except Exception as err_:
                        processinfo += "\nError:%s\n"%err_
                for attr in ['author','language','revision','version','last_printed','modified','keywords','comments','category']:
                    runprop(attr,cpobject,processinfo=processinfo) 

                    

                try:
                    outlook()
                    send_successful=True
                    processinfo += "邮件发送成功。"
                except Exception as err_:
                    if send_successful==True:
                        processinfo += '提示[%s]: 发送成功。但Outlook程序配置错误，请允许程序调用Outlook发送邮件。\n错误详情：%s'%(notefile_real,err_)
                    else:
                        processinfo += "发送失败，详情请查看ERRORINFO"
                        errinfo += '提示[%s]: 发送失败。Outlook程序配置错误，请允许程序调用Outlook发送邮件。\n错误详情：%s'%(notefile_real,err_)

                if send_successful==True: #如果发送成功再写入文件到数据库，否则不写入
                    # db=shelve.open('E:/Windows_WorkFolder/工作文件夹/daily_update_data/update_data')
                    try:
                        db=shelve.open(dbaddress)
                        for key in preparenotedict.keys():
                            db[key]=preparenotedict[key]
                        db.close()
                        processinfo += "\n数据库更新成功\n"
                    except:
                        processinfo += "\n数据库更新失败，详情请查看ERRORINFO\n"
                        errinfo += "\n邮件发送成功但数据库更新失败。\n"
                        raise ValueError("数据库更新失败")
                else:
                    pass
                
            return True,2,'完成数据处理',processinfo,errinfo
        else:
            return True,1,"未检测到新增的日记文件",processinfo,errinfo
    except:
        return False,0,traceback.format_exc(),processinfo,errinfo

if __name__=="__main__":
    #程序测试开始
    result,infomation,list,notedict= checkDaily(address='E:/Windows_WorkFolder/工作文件夹/',
            regular=r"\b201\d年\d+月.*?日.*?.doc.*?",dbaddress='E:/Windows_WorkFolder/工作文件夹/daily_update_data/update_data')
    if result == True:
        if list != []:
            print('需要写入的数据',list)
            result_2,result_num,result_txt,processinfo,errinfo= sendMail(list,address='E:/Windows_WorkFolder/工作文件夹/',emailaddress='dayone@mazhangjing.com',
                        dbaddress='E:/Windows_WorkFolder/工作文件夹/daily_update_data/update_data',preparenotedict=notedict)
            print(result_2,'\n',processinfo,'\n',errinfo,'\n',result_txt)
        else:
            print("成功检索数据，但未发现新数据")
            print(infomation,list)




    