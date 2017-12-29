#!/usr/bin/env python3
'''Written by Corkine Ma
这个模块的大部分是子类化了一个QDialog，用来接受用户的输入，并且将其保存到daily.setting文件夹中
除此之外，还有一个函数，这个函数负责从daily.setting读取数据，并且使用checkandsend.py模块中的
两个函数来判断在数据库位置是否存在监视文件夹中符合正则表达式规则的文件，如果文件夹中有这样的文件
但是数据库中没有，就判定是一篇新日记，然后调用邮件发送程序发送邮件，其会返回一个bool值，大部分情况，
只要参数文件和日志文件不出问题，返回的都是true，至于发送邮件出错，依旧会返回true（因为考虑到可能存在
发送多个文件，并且有些文件可能无法打开，有些不能发送，所以统一返回true，不过对于每个文件的处理信息
都会保存在stdout中，如果你打开了log，则会保存在daily.log中），第四个参数会返回详细的处理信息，
包括成功和失败的。

'''
import sys,os,io,shelve,traceback,time
from tkinter import Tk
from tkinter.messagebox import showwarning

import PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import ui_setting

from checkandsend import *
# os.chdir(r"C:\Users\Administrator\Desktop\pyBook\Project_EveryDayNotice")

__VERSION__ = '0.2.6'

class Form(QDialog,ui_setting.Ui_Dialog):
    def __init__(self,parent=None):
        super(Form,self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.selectDb)
        self.pushButton_2.clicked.connect(self.selectCWD)
        # self.pushButton_4.clicked.connect(self.selectAlert)
        self.address=''
        self.dbaddress =''
        # self.alertaddress = ''
        self.buttonBox.accepted.connect(self.saveIt)
        
        try:
            loadfile = open('daily.setting','r')
            thefile = loadfile.read()
            # print(thefile)
            self.address=str(thefile.split(",")[0])
            self.dbaddress=str(thefile.split(",")[1])
            # self.alertaddress = str(thefile.split(",")[4])
            self.label_3.setText(self.dbaddress)
            self.label_4.setText(self.address)
            self.lineEdit.setText(str(thefile.split(",")[2]))
            self.lineEdit_2.setText(str(thefile.split(",")[3]))
            # self.label_5.setText(self.alertaddress)
        except:
            QMessageBox.warning(self,"WARN",'从之前的文件中读取出错，如果你第一次使用此程序，请忽略此条消息')


    def selectCWD(self):
        address=QFileDialog.getExistingDirectory(self,"选择需要监视的文件夹",os.getcwd(),QFileDialog.ShowDirsOnly)
        if address != None:
            self.address = address
            self.label_4.setText(self.address)
        else:
            self.label_4.setText('未选择')

    def selectDb(self):
        choose = QMessageBox.information(self,'选项',"你是否需要新建一个数据库文件？如果没有，请点击'OK',否则点击'Cancel'选择你的数据库问卷",QMessageBox.Ok|QMessageBox.Cancel)
        if choose == QMessageBox.Ok:
            address=QFileDialog.getExistingDirectory(self,"选择需要监视的文件夹",os.getcwd(),QFileDialog.ShowDirsOnly)
            db=shelve.open(address+'/mydailydata')
            db['1999年1月1日.docx']='Update at NOTIME'
            self.dbaddress = address+'/mydailydata'
            self.label_3.setText(self.dbaddress)
        else:
            filename,type = QFileDialog.getOpenFileName(self,"选择你的数据库文件",'',"cmData files (*.dat)")
            # print(filename)
            if filename != None:
                if '.bak' in filename[-4:] or '.dat' in filename[-4:] or '.dir' in filename[-4:]:
                    filename = filename[:-4]
                    self.dbaddress = filename
                    self.label_3.setText(self.dbaddress)
                    # print(self.dbaddress)
                else:
                    self.label_3.setText('未选择')
                    QMessageBox.warning(self,"WARN",'无效文件，请重新选取')
        
    def contextMenuEvent(self, event):
        menu1 = QMenu()
        runAction = menu1.addAction("测试程序运行情况(&R)")
        runAction.triggered.connect(self.runTest)
        menu1.exec_(event.globalPos())

    def runTest(self):
        result_bool,result_1,result_2,result_txt = runCheck()
        QMessageBox.information(self,'输出测试',result_txt)

    # def selectAlert(self):
    #     filename,type = QFileDialog.getOpenFileName(self,"选择你的提醒程序",'',"cmEXE files (*.exe)")
    #     if filename != None:
    #         self.alertaddress = filename
    #         self.label_5.setText(self.alertaddress)
            
    def saveIt(self):
        emailaddress = str(self.lineEdit.text())
        regularexp = str(self.lineEdit_2.text())
        if emailaddress == '' or regularexp == '' or self.dbaddress =='' or self.address == '' :#不对提醒程序判断
            QMessageBox.warning(self,"WARN",'输入数据无效，请检查后再试')
        else:
            try:
                # print(emailaddress,regularexp,self.address,self.dbaddress,self.alertaddress)
                savedata = open('daily.setting','w')
                savedata.write('%s,%s,%s,%s'%(self.address,self.dbaddress,emailaddress,regularexp))
                savedata.close()
                QMessageBox.information(self,"Info",'设置数据保存在daily.setting文件中')
                # print(os.getcwd())
            except Exception as _err:
                print(traceback.format_exc())
                QMessageBox.warning(self,"WARN",'数据保存失败')
                # print(os.getcwd())
        

def runCheck(settingsfile='daily.setting',log=True,logfile='daily.log',sendmail=True):
    '''runCheck()用来自动调用checkandsend.py中的函数，使用给定文件载入函数所需参数并且进行查找，其会
    返回一个bool值，并且还有处理结果。此方法接受一个bool值和一个输出地址来判断是否允许相关处理日志保存
    在给定参数的文件中，比如true，daily.log，表示接受输出，保存在daily.log参数中。
    '''
    try:
        if log == True:
            tmp = sys.stdout
            sys.stdout = open(logfile,'a')
        else:
            pass

        print('\n\n','='*100)
        print('=============================================',time.ctime(),'======================================')
        print('='*100,'\n\n')
        loadfile = open(settingsfile,'r')
        thefile = loadfile.read()
        address=str(thefile.split(",")[0])
        dbaddress=str(thefile.split(",")[1])
        # alertaddress = str(thefile.split(",")[4])
        emailaddress=str(thefile.split(",")[2])
        regular=str(thefile.split(",")[3])
        result,infomation,clist,notedict= checkDaily(address=address+'/',
                regular=regular,dbaddress=dbaddress)
        processinfo = errinfo = result_txt = ''
        if result == True:
            if clist != []:
                if sendmail == True:
                    print('需要写入的数据',clist)
                    
                    result_2,result_num,result_txt,processinfo,errinfo= sendMail(clist,address=address+'/',emailaddress=emailaddress,
                                dbaddress=dbaddress,preparenotedict=notedict)
                    print(result_2,'\n',processinfo,'\n',errinfo,'\n',result_txt)

                    if log == True:
                        sys.stdout.close()
                        sys.stdout = tmp
                    else:pass

                    return True,processinfo,errinfo,result_txt
                else:
                    return True,'','','成功检索并发现新数据，但你选择了不发送邮件'
            
            else:
                print("成功检索数据，但未发现新数据")
                print(infomation,clist)
                
                if log == True:
                    sys.stdout.close()
                    sys.stdout = tmp
                else:pass

                return True,'','','成功检索数据，但未发现新数据'
                # 此处修改需要更改noticedlg相关判断语法
        else:
            return False,'','','未能成功调用checkDaily()函数，可能是因为参数传递错误。'
    except:
        return False,'','',str(traceback.format_exc())

    











if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Daily Notice")
    app.setOrganizationName("Marvin Studio")
    app.setOrganizationDomain("http://www.marvinstudio.cn")
    form = Form()
    form.show()
    # runCheck()
    # print(runCheck(sendmail=False)
    app.exec_()