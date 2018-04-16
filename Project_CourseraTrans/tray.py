#!/usr/bin/env python3
# -*- coding:utf8 -*-
import PyQt5,sys,traceback
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from tkinter import Tk
from tkinter.messagebox import showinfo
import RC_tray
import os,sys
from googletrans import Translator
def showbug(message):
    Tk().withdraw()
    info = showinfo('提示信息',str(message))

version = "1.0.2"
log = "1.0.2 2018年4月16日 仅使用translate.google.cn服务器"

class Form(QDialog):
    def __init__(self,parent=None):
        super(Form,self).__init__(parent)
        self.createTrayIcon()
        self.trayIcon.show()
        self.processing = False
        msgIcon = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Information)
        self.trayIcon.showMessage("Coursera 字幕中文翻译助手","请复制字幕文件(txt格式)到剪贴板并直接点击图标即可翻译。",msgIcon)
#        self.trayIcon.messageClicked.connect(self.traymesageClicked)

        self.setWindowTitle("Coursera字幕中文翻译助手")

    def createTrayIcon(self):
        self.trayMenu = QMenu()
        trans = self.trayMenu.addAction("处理剪贴板中的文件")
        trans.triggered.connect(self.transProcess)
        self.trayMenu.addSeparator()
        about = self.trayMenu.addAction("使用说明")
        about.triggered.connect(self.aboutBox)
        self.trayMenu.addSeparator()
        quit = self.trayMenu.addAction("退出")
        quit.triggered.connect(self.fullClose)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(":/Main/Media/normal.png"))
        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.activated.connect(self.iconActived)
        self.trayIcon.setToolTip("Coursera 字幕中文翻译助手")


    def fullClose(self):
        self.trayIcon.hide()
        app.setQuitOnLastWindowClosed(True)
        self.close()

    def showMenu(self):
        self.trayMenu.exec_()

    def iconActived(self,reason):
        mouse = QCursor()
        if self.processing:
            return 0
        if reason == QSystemTrayIcon.DoubleClick:
            self.trayMenu.exec_(mouse.pos())
        if reason == QSystemTrayIcon.Trigger:
            self.transProcess()

    def transProcess(self):
        clipboard = QGuiApplication.clipboard()
        if str(clipboard.text()).startswith("file:///"):
            if not str(clipboard.text()).endswith(".txt"):
                self.showInfo("剪贴板文件并非TXT格式文本。")
                return 0
            else:
                self.uri = clipboard.text()[8:]
                print(self.uri)
                if self.processing == False:
                    self.processing = True
                    self.changeIcon()
                    self.transGo(self.uri)
                    self.processing = False
                    self.changeIcon()
        else:
            self.showInfo("没有文件需要处理，请复制文本文件到剪贴板。")

    def changeIcon(self):
        if self.processing:
            self.trayIcon.setIcon(QIcon(":/Main/Media/working.png"))
            self.trayIcon.setToolTip("Coursera 字幕中文翻译助手 - 正在翻译中")
        else:
            self.trayIcon.setIcon(QIcon(":/Main/Media/normal.png"))
            self.trayIcon.setToolTip("Coursera 字幕中文翻译助手")
        
    def transIt_free(self,f):
        translator = Translator(service_urls=[
        'translate.google.cn'
        ])
        translations = translator.translate(f,dest="zh-CN",src="en")
        r = []
        for t in translations:
            r.append(t.text)
        return r

    def transGo(self,uri):
        try:
            print("START...")
            file = open(uri,"r",encoding="utf-8",errors="ignore")
            f = file.read()
            f= f.replace("\n"," ")
            f = f.replace("?","?\n").replace(".",".\n")
            f = f.split("\n")

            data = self.transIt_free(f)
            of = ""
            for x in data:
                of += x
            of = of.replace("？","？\n").replace("。","。\n")
            open(uri,"a+",encoding="utf-8",errors="ignore").write("\n\n\n"+of)
            en_list = f
            cn_list = []
            for x in of.split("\n"):
                cn_list.append(x)
            out = ""
            i = 0
            for en in en_list:
                link = str(i) + en + "\n" + cn_list[i] + "\n\n" 
                i = i + 1
                out += link
            open(uri,"a+",encoding="utf-8",errors="ignore").write("\n\n\n"+out)
            print("DONE!")
            try:
                os.startfile(self.uri)
            except Exception as e2:
                self.showInfo("翻译完毕，但是无法打开目标文件。"+str(e2))

        except Exception as e:
            self.showInfo("翻译出错，可能是文件格式错误或者连接故障。"+str(e))
            print(traceback.format_exc())

    def showInfo(self,info):
        msgIcon = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Information)
        self.trayIcon.showMessage("Coursera 字幕中文翻译助手",info,msgIcon)


    def aboutBox(self):
        msg = QMessageBox()
        msg.information(self,"关于本程序","Coursera 字幕中文翻译助手 %s\nWriten by Corkine Ma\n\n本程序基于PyQt5和googletrans包。\n\n将txt格式字幕文件复制到剪贴板，点击托盘图标会调用Google翻译API，将其余语言翻译为中文，文件会被自动写入，使用默认打开方式自动打开。当程序正在运行时，变为红色，此时正在连接服务器并进行翻译，当完毕后图标变为蓝色。\n"%version)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/Main/Media/normal.png"))
    if QSystemTrayIcon.isSystemTrayAvailable() != True:
        showbug("系统不支持托盘图标")
    form = Form()

    app.exec_()

