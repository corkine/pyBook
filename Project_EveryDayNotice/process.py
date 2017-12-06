#!/usr/bin/env python3
# -*- coding:utf8 -*-

import sys,traceback
import PyQt5
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import ui_processdlg
from checkandsend import checkDaily
from PyQt5.QtPrintSupport import QPrinter,QPrintDialog
import appsetting
from docx import *
PageSize = (595, 842)

__modelversion__ = '0.0.1'

class ProcessForm(QDialog,ui_processdlg.Ui_processDlg):
    def __init__(self,settingsfile='daily.setting',parent=None):
        super(ProcessForm,self).__init__(parent)
        self.setupUi(self)
        

        settingsfile=settingsfile
        loadfile = open(settingsfile,'r')
        thefile = loadfile.read()
        self.address=str(thefile.split(",")[0])
        dbaddress=str(thefile.split(",")[1])
        emailaddress=str(thefile.split(",")[2])
        regular=str(thefile.split(",")[3])
        result,infomation,clist,notedict= checkDaily(address=self.address+'/',
                regular=regular,dbaddress=dbaddress)


        self.listWidget_files.clear()
        self.items = clist
        self.resize(400,300)
        # print(self.items)
        self.showItems()
        self.pushButton_next.hide()

        self.pushButton_quickview.clicked.connect(self.showPrintPreview)
        self.pushButton_setting.clicked.connect(self.callSetting)
        self.pushButton_print.clicked.connect(self.print_)
        self.pushButton_sendmail.clicked.connect(self.callSendmail)
        self.pushButton_printdlg.clicked.connect(self.callPrint)
        self.pushButton_next.clicked.connect(self.showMore)


        self.printer = QPrinter(QPrinter.HighResolution)
        self.printer.setPageSize(QPrinter.A4)

        # self.view = QGraphicsView()
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0,0,PageSize[0],PageSize[1])
        self.graphicsView_print.setScene(self.scene)
        self.scene2 = QGraphicsScene(self)
        self.scene2.setSceneRect(0,0,PageSize[0],PageSize[1])
        # self.graphicsView_print.setScene(self.scene2)




    def showPrintPreview(self,window='show'):
        try:
            self.graphicsView_print.setScene(self.scene)
            filename = self.listWidget_files.currentItem().text()
            fulladdress = self.address +'/'+ filename
            # print("地址是",fulladdress)
            subject,text_body,status,error = self.readText(fulladdress)
            # print(subject,text_body,status,error)
            if window == 'notshow':
                self.showCurrentPage(subject,text_body)
            else:
                if self.pushButton_quickview.text()=='预览(&V)':
                    self.stackedWidget.setCurrentIndex(1)
                    self.resize(self.scene.width()+50,self.scene.height()+100)
                    self.pushButton_quickview.setText("取消预览(&V)")
                    
                    self.showCurrentPage(subject,text_body)
                elif self.pushButton_quickview.text()=='取消预览(&V)':
                    self.stackedWidget.setCurrentIndex(0)
                    self.resize(400,300)
                    self.pushButton_quickview.setText('预览(&V)')
                    self.pushButton_next.hide()
                else:
                    pass
        except:
            pass

    def callSetting(slef):
        settingdlg = appsetting.Form()
        if settingdlg.exec_():
            pass

    def callPrint(self):
        self.showPrintPreview(window='notshow') # 防止不经预览直接打印空白
        dialog = QPrintDialog(self.printer)
        if dialog.exec_():
            self.print_()

    def callSendmail(self):
        pass

    def showItems(self):
        self.listWidget_files.addItems(self.items)
        self.listWidget_files.setCurrentRow(0)

    def showCurrentPage(self,subject='',text_body=''):
        try:
            self.scene.clear()
            
            self.scene2.clear()
            item = QGraphicsTextItem()
            # item.setboundingRect(QRectF(0,0,PageSize[0],PageSize[1]))
            item.setFont(QFont('宋体',16))
            item.setX(50)
            item.setY(50)
            item.setFont(QFont('Times New Roman',16))
            item.setPlainText(subject)
            self.scene.addItem(item)

            item = QGraphicsTextItem()
            item.setY(100)
            item.setX(50)
            item.setTextWidth(PageSize[0]-100)

            item.setFont(QFont('宋体',8))
            item.setFont(QFont('Times New Roman',8))
            item.setPlainText(text_body.replace('\n','\n\n'))
            # print(item.sceneBoundingRect().x(),item.sceneBoundingRect().y())
            # print(item.boundingRect())
            if item.boundingRect().height() > 722:
                i = 1
                while True:
                    item.setPlainText("")
                    try_it = text_body.split("\n")
                    try_it = try_it[:-i]
                    # print(try_it)
                    adjust_content_A = "\n\n".join(try_it)
                    # print("最后调整",'+'*100,adjust_content_A)
                    item.setPlainText(adjust_content_A)
                    if item.boundingRect().height() < 740:
                        adjust_content_B = "\n\n".join(text_body.split("\n")[-i:])
                        # print('**'*100,adjust_content_B)
                        break
                    else:pass
                    i = i + 1
                self.scene.addItem(item)

                item2 = QGraphicsTextItem()
                item2.setY(50)
                item2.setX(50)
                item2.setTextWidth(PageSize[0]-100)
                item2.setFont(QFont('宋体',8))
                item2.setFont(QFont('Times New Roman',8))
                item2.setPlainText(adjust_content_B)
                

                self.scene2.addItem(item2)

                self.label_print.setText("打印预览(多页...)")
                # self.label_print.clicked.connect(self.showMore)
                self.pushButton_next.show()
                self.pushButton_next.setText("预览第2页(&N)")
            else:
                self.scene.addItem(item)
        except:
            pass
    
    
    def showMore(self):
        self.graphicsView_print.setScene(self.scene2)
        self.pushButton_next.hide()



    def print_(self):
        self.showPrintPreview(False) # 防止不经预览直接打印空白
        painter = QPainter(self.printer)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        self.scene.render(painter)
        # painter2 = QPainter(self.printer)
        # painter2.setRenderHint(QPainter.Antialiasing)
        # painter2.setRenderHint(QPainter.TextAntialiasing)
        # self.scene2.render(painter2)

    def readText(self,fulladdress=''):
        try:
            document=Document(fulladdress)
            text_body=''
            text_article = [ paragraph.text for paragraph in document.paragraphs]
            subject=str(text_article[:1])[2:-2]
            for pargh in text_article[1:]:
                text_body+=pargh+'\n'
            return subject,text_body,'1','成功获取文本'
        except:
            return '','','2',traceback.format_exc()


if __name__=="__main__":


    # settingsfile='daily.setting'
    # # log=True
    # # logfile='daily.log'
    # # sendmail=False
    # loadfile = open(settingsfile,'r')
    # thefile = loadfile.read()
    # address=str(thefile.split(",")[0])
    # dbaddress=str(thefile.split(",")[1])
    # # alertaddress = str(thefile.split(",")[4])
    # emailaddress=str(thefile.split(",")[2])
    # regular=str(thefile.split(",")[3])
    # result,infomation,clist,notedict= checkDaily(address=address+'/',
    #         regular=regular,dbaddress=dbaddress)
    # print(111111111111111111111,result,222222222222222222222,infomation,333333333333333333333,
        # clist,44444444444444444444,notedict)

    # notefile=str(address+'/'+clist[2])
    # print(notefile)
    # # from docx import *
    # document=Document(notefile)
    # mail_text_body=''
    # text_article = [ paragraph.text for paragraph in document.paragraphs]
    # mail_subject=str(text_article[:1])[2:-2]
    # for pargh in text_article[1:]:
    #     mail_text_body+=pargh+'\n'
    # print(mail_subject)
    # print(mail_text_body)

    # data = {}
    app = QApplication(sys.argv)
    form = ProcessForm('daily.setting')
    form.show()
    app.exec_()