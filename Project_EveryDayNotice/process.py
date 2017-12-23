#!/usr/bin/env python3
# -*- coding:utf8 -*-
'''此模块接收一个文件，从中接收参数：监控文件、数据库地址、判断的正则表达式，然后输出一个对话框'''
import sys,traceback,os
import PyQt5
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import ui_processdlg
from checkandsend import checkDaily,sendMail
from PyQt5.QtPrintSupport import QPrinter,QPrintDialog
import appsetting
from docx import *
PageSize = (595, 842)
# 调试模块关闭此条注释，其余情况应注释掉此语句。此语句被用来寻找daily.setting文件。
# os.chdir(r"C:\Users\Administrator\Desktop\pyBook\Project_EveryDayNotice")
__modelversion__ = '0.0.3'
__UDATA__ = '''
0.0.1 存在问题：没有写邮件系统；不能打印多页；
0.0.2 存在问题：不能打印多页，进行的修改如下：
    2017年12月7日修改：
        - 添加了对于大小和位置的判断，现在显示的对话框会根据屏幕尺寸改变
        - 增强了程序的健壮性
        - 添加了全部打印命令
    2017年12月8日修改：
        - 现在发送邮件后可以直接查看结果了，不会弹出对话框，而是使用的STACKEDWIDGHT显示信息
0.0.3 解决问题：现在可以打印最多两页了，因为对于日记我自己有限制，所以两页够了。修正了点击“设置”按钮并更改设置后程序不会更新列表的问题。

'''

class ProcessForm(QDialog,ui_processdlg.Ui_processDlg):
    def __init__(self,settingsfile='daily.setting',parent=None):
        super(ProcessForm,self).__init__(parent)
        self.log = '' 
        self.setupUi(self)
        self.maxrect = QApplication.desktop().availableGeometry()
        self.checkFromFile(settingsfile=settingsfile)
        self.settingsfile = settingsfile # 调用设置更新后需要使用
        self.listWidget_files.clear()
        self.resize(400,300)
        self.showItems()
        self.pushButton_next.hide()

        self.pushButton_quickview.clicked.connect(self.showPrintPreview)
        self.pushButton_setting.clicked.connect(self.callSetting)
        self.pushButton_print.clicked.connect(self.print_)
        self.pushButton_sendmail.clicked.connect(self.callSendmail)
        self.pushButton_printdlg.clicked.connect(self.callPrint)
        self.pushButton_next.clicked.connect(self.showMore)
        self.pushButton_printall.clicked.connect(self.printAll)


        self.printer = QPrinter(QPrinter.HighResolution)
        self.printer.setPageSize(QPrinter.A4)

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0,0,PageSize[0],PageSize[1])
        self.graphicsView_print.setScene(self.scene)
        self.scene2 = QGraphicsScene(self)
        self.scene2.setSceneRect(0,0,PageSize[0],PageSize[1])
        self.graphicsView_print.setScene(self.scene2)

        self.showbefore_x = self.x()
        self.showbefore_y = self.y()
        self.setWindowTitle("EveryDayNotice - 文件处理程序[模块版本:%s]"%__modelversion__)

    def checkFromFile(self,settingsfile=''):
        try:
            settingsfile=settingsfile
            loadfile = open(settingsfile,'r')
            thefile = loadfile.read()
            self.address=str(thefile.split(",")[0])
            self.dbaddress=str(thefile.split(",")[1])
            self.emailaddress=str(thefile.split(",")[2])
            self.regular=str(thefile.split(",")[3])
            self.result,self.infomation,self.clist,self.notedict= checkDaily(address=self.address+'/',
                    regular=self.regular,dbaddress=self.dbaddress)
            self.items = self.clist
        except:
            raise ImportError("相关参数没有设置")
            # QMessageBox.information(self,"WARN",str(traceback.format_exc()))

    def showPrintPreview(self,window='show'):
        try:
            self.graphicsView_print.setScene(self.scene)
            filename = self.listWidget_files.currentItem().text()
            fulladdress = self.address +'/'+ filename
            # print("地址是",fulladdress)
            try:
                subject,text_body,status,error = self.readText(fulladdress)
            except:
                subject = text_body = status = error = ''
            # print(subject,text_body,status,error)
            if window == 'notshow':
                self.showCurrentPage(subject,text_body)
            else:
                if self.pushButton_quickview.text()=='预览(&V)':
                    self.stackedWidget.setCurrentIndex(1)
                    # self.resize(the_width+50,the_height)
                    if self.scene.width() < self.maxrect.width():
                        the_width = self.scene.width()
                    else:
                        the_width = self.maxrect.width()
                    if self.scene.height() < self.maxrect.height():
                        the_height = self.scene.height()
                    else:
                        the_height = self.maxrect.height()
                    self.resize(the_width+50,the_height-40)
                    self.showbefore_x = self.x()
                    self.showbefore_y = self.y()
                    self.move(self.x(),self.maxrect.y()+40)
                    self.pushButton_quickview.setText("取消预览(&V)")
                    
                    self.showCurrentPage(subject,text_body)
                elif self.pushButton_quickview.text()=='取消预览(&V)':
                    self.stackedWidget.setCurrentIndex(0)
                    self.resize(400,300)
                    self.move(self.showbefore_x,self.showbefore_y)
                    self.pushButton_quickview.setText('预览(&V)')
                    self.pushButton_next.hide()
                else:
                    pass
        except:
            pass

    def printAll(self):
        # self.listWidget_files.setCurrentRow(0) # 防止用户更改顺序，从0开始打印
        for x in range(self.listWidget_files.count()):
            self.listWidget_files.setCurrentRow(x)
            self.showPrintPreview(window='notshow')
            self.print_()

    def callSetting(self):
        settingdlg = appsetting.Form()
        if settingdlg.exec_():
            self.checkFromFile(settingsfile=self.settingsfile)
            self.showItems()

    def callPrint(self):
        self.showPrintPreview(window='notshow') # 防止不经预览直接打印空白
        dialog = QPrintDialog(self.printer)
        if dialog.exec_():
            self.print_()

    def callSendmail(self):
        self.callCurrentSendmail()
        self.showLog()
        # 一次性全部发送，不允许单个发送
    def showLog(self):
        logpanel = LogPanel()
        height,width = self.size().height(),self.size().width()
        # print(width,height)
        self.stackedWidget.insertWidget(3,logpanel)
        self.stackedWidget.setCurrentIndex(self.stackedWidget.count()-1)
        logpanel.infolabel.setText(str(self.log))
        # logpanel.infolabel.setText(str("这里展示的是输出信息"))
        def backNow():
            if QMessageBox.information(self,"退出程序？","处理完毕，是否要退出程序？",QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                self.close()
            else:
                self.stackedWidget.setCurrentIndex(0)
                self.stackedWidget.removeWidget(logpanel)
                self.resize(width,height)
            # print(self.size())
        logpanel.backbutton.clicked.connect(backNow)      
        
    def callCurrentSendmail(self):
        self.log = ''
        try:
            result_2,result_num,result_txt,processinfo,errinfo=sendMail(self.clist,
                self.address+'/',self.emailaddress,self.dbaddress,self.notedict)
        except:
            self.log += "发送失败"
        finally:
            self.log += str(result_2)+'\n'+processinfo+'\n'+errinfo+'\n'+result_txt

    def showItems(self):
        self.listWidget_files.clear()
        self.listWidget_files.addItems(self.items)
        self.listWidget_files.setCurrentRow(0)

    def showCurrentPage(self,subject='',text_body=''):
        try:
            self.label_print.setText("打印预览")
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
                # print("发生多页情况")
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

                self.printMore = True
                # self.scene.addItem(item)
            else:
                self.printMore = False
                self.scene.addItem(item)
        except:
            QMessageBox.information(self,"WARN",str(traceback.format_exc()))
        
    
    
    def showMore(self):
        self.graphicsView_print.setScene(self.scene2)
        self.pushButton_next.hide()



    def print_(self):
        self.showPrintPreview(False) # 防止不经预览直接打印空白
        painter = QPainter(self.printer)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        self.scene.render(painter)
        if self.printMore == True:
            result = self.printer.newPage()
            # print("打印机调用结果----->",result,"\n\nprintMore属性为","%s"%self.printMore)
        # painter2 = QPainter(self.printer)
        # painter2.setRenderHint(QPainter.Antialiasing)
        # painter2.setRenderHint(QPainter.TextAntialiasing)
        self.scene2.render(painter)

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

class LogPanel(QWidget):
    def __init__(self,parent=None):
        super(LogPanel,self).__init__(parent)
        self.infolabel = QLabel("无信息")
        self.backbutton = QPushButton("确定(&O)")
        self.backnow = False
        layout = QVBoxLayout()
        childlayout = QHBoxLayout()
        childlayout.addWidget(self.backbutton)
        childlayout.addStretch()
        layout.addWidget(self.infolabel)
        layout.addLayout(childlayout)
        layout.addStretch()
        self.setLayout(layout)
        self.setWindowTitle("处理程序")


if __name__=="__main__":

    app = QApplication(sys.argv)
    form = ProcessForm('daily.setting')
    form.show()
    # form2 = LogPanel()
    # form2.show()
    app.exec_()