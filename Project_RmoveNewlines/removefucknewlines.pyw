#!/usr/bin/env python3
# -*- coding: utf8 -*- 
import sys,traceback
import PyQt5
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QClipboard,QGuiApplication,QIcon,QCursor
from PyQt5.QtWidgets import QDialog,QApplication,QPushButton,QTextBrowser,QVBoxLayout,QHBoxLayout,QMessageBox,QTextEdit,QMenu,QSystemTrayIcon
import RC_removefucknewlines
__TITLE__ = '论文复制行间断去除'
__VERSION__ = "1.0.0"
__LOG__ ="""
%s, 当前版本 ver %s<br><br>
<b>2017-12-01 版本0.6.1 更新日志：</b><br>
提供了手动和自动两种处理方式，你可以键入一些内容，系统会自动处理，当然，也可以将内容复制到剪贴板，程序会自动检测剪贴板并进行处理，结果呈现在下方的文本框中。<br><br>

<b>2017-12-20 版本1.0.0 更新日志：</b><br>
提供了一个系统托盘图标，你可以直接点击它来快速处理，不需要打开程序了，同时，处理成功后图标会添加一个绿钩，提供视觉反馈。<br><br>
...



"""%(__TITLE__,__VERSION__)
class Form(QDialog):
    def __init__(self,parent=None):
        super(Form,self).__init__(parent)
        self.info_label = '请将需要处理的文本复制到剪贴板，然后返回本程序'
        self.info_label2 = QPushButton("使用帮助")
        self.info_label3 = QPushButton("关于本程序")
        self.info_label4 = QPushButton("复制到剪贴板(&C)")
        self.pushbutton_exit = QPushButton("退出程序(&E)")
        self.setWindowTitle("%s %s - %s"%(__TITLE__,__VERSION__,self.info_label))
        self.resize(800,600)
        self.beforedoit = ''
        # self.dirty = False
        self.textbrowser2 = QTextEdit()
        self.textbrowser = QTextBrowser()
        self.setWhatsThis("这是一个快速移除论文断行的小程序，详情请查看“使用帮助”")
        layout = QVBoxLayout()
        layout_child = QHBoxLayout()

        layout_child.addStretch()
        layout_child.addWidget(self.info_label4)
        layout_child.addWidget(self.info_label2)
        layout_child.addWidget(self.info_label3)
        layout_child.addWidget(self.pushbutton_exit)
        layout.addWidget(self.textbrowser2)
        layout.addWidget(self.textbrowser)
        layout.addLayout(layout_child)
        self.setLayout(layout)

        self.info_label2.clicked.connect(self.showHelp)
        self.info_label3.clicked.connect(self.showAbout)
        self.info_label4.clicked.connect(self.pastetoClipboard)
        self.textbrowser2.textChanged.connect(self.doitByhand)
        self.pushbutton_exit.clicked.connect(self.fullClose)

        self.createTrayIcon()
        self.trayIcon.messageClicked.connect(self.traymessageClicked)

    def enterEvent(self, event = None):
        # print("SHOW!")
        clipboard=QGuiApplication.clipboard()
        try:
            self.beforedoit = clipboard.text()
            if self.textbrowser.toPlainText() == self.beforedoit:
                raise ValueError("没什么新内容需要处理")
            if self.beforedoit == '':
                raise ValueError('剪贴板为空')
            self.textbrowser2.setText(self.beforedoit)
            self.beforedoit = self.beforedoit.replace('\n',' ')
            if self.beforedoit == self.textbrowser2.toPlainText():
                # self.info_label4.setText("复制到剪贴板(&C)")
                raise ValueError("没什么需要处理的")
            else:
                self.info_label4.setText("复制到剪贴板(&C)")
                # self.dirty = True
            self.info_label = '处理完毕，更新后的文本已复制到你的剪贴板'
            clipboard.setText(self.beforedoit)
        except:
            self.info_label = '[未检测到内容]请将需要处理的文本复制到剪贴板，然后返回本程序'
            
        self.textbrowser.setText(self.beforedoit)
        # self.textbrowser.selectAll()
        self.setWindowTitle("%s %s - %s"%(__TITLE__,__VERSION__,self.info_label))

    # def contextMenuEvent(self, event):
    #     menu = QMenu()
    #     action1 = menu.addAction("使用说明")
    #     action2 = menu.addAction("关于本软件")
    #     menu.exec_(event.globalPos())
    def doitByhand(self):
        try:
            self.textbrowser.setText(self.textbrowser2.toPlainText().replace('\n',' '))
            clipboard=QGuiApplication.clipboard()
            clipboard.setText(self.textbrowser.toPlainText())
            self.info_label4.setText("复制到剪贴板(&C)")
        except:
            traceback.print_exc()





    def showHelp(self):
        QMessageBox.about(self,"使用帮助","""
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'SimSun'; font-size:9pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">本文档适用于版本 0.6.1，当前软件版本为 %s</p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt; font-weight:600; text-decoration: underline;">简要介绍：</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">本程序可以快速去除给定文本的“\\n”标识符。</p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt; font-weight:600; text-decoration: underline;">本程序希望解决以下问题：</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">当代文献排版都是左右两栏，我们获取的电子版文献（可能你是从百度或者Google学术下载的）一般都可以复制文字，但是这些复制过的文字存在断行问题，原本就是一行的文字经过这样直接复制后粘贴到别的地方，比如Word中会出现非常麻烦的断行。这件事情很麻烦，因为当我们复制过去后需要手动去调整让这些断行变得整齐，因此有了本程序。</p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">这个问题很好解决，只需要使用Python的replace()函数就好，不过，为了处理一段文本，还需要执行一段代码，然后把文本粘贴进去、复制出来，麻烦程度不亚于手动处理。</p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt; font-weight:600; text-decoration: underline;">使用说明：</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">得益于Qt强大的工具集和Python的快速编程能力，你只用在Acrobat等PDF阅读器中选定一些文本，然后返回本程序，只要鼠标停留在本界面的任何位置即可（甚至不需要滑动，只要鼠标在窗口上就行），（其实你可以让这个窗口大一点，切换回来的时候自然鼠标就在窗口上面，什么都不用做），然后打开你的Word，直接粘贴即可，当激活本程序窗口时，行之间的间断会自动去除。一个我期望的工作流是：在阅读器中按下Ctrl+C复制文本，按下Alt+Table切换到本程序，然后继续按下Alt+Table切换到Word等你需要粘贴的地方就好。</p> 
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">当然，你也可以手动粘贴一段需要处理的文本到第一个文本框，然后处理后的结果会显示在第二个文本框，不过实际上你不需要这么做，包括下面那个“复制到剪贴板”，那个按钮没任何作用，和允许手动操作一样，设计的目的都是为了让用户更有安全感。（PS.在0.6.0版本才加入了上面那个文本框）       </p></body></html>      
        """%(__VERSION__))
        
    def showAbout(self):
        QMessageBox.about(self,"CM LOVE Python","""
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'SimSun'; font-size:9pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">%s version %s</p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Written by <span style=" font-weight:600;">Corkine Ma</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Email:cm@marvinstudio.cn</p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">本程序使用 Python 和 Qt 开发，程序遵循GPL v2开源协议，你可以在http://tools.mazhangjing.com 此网站找到程序的源代码，如果没有，请联系作者。</p></body></html>
        
        
        
        """%(__TITLE__,__VERSION__)
        )
        QMessageBox.information(self,"%s - 更新日志"%__TITLE__,"%s"%__LOG__)

    def pastetoClipboard(self):
        # clipboard = QClipboard()
        # clipboard.setText(self.textbrowser.toPlainText())
        # 这个函数只是为了让你感到安全，没功能
        self.info_label4.setText("已复制")

    def createTrayIcon(self):
        self.trayMenu = QMenu()
        showAction = self.trayMenu.addAction("打开主程序(&O)")
        showAction.triggered.connect(self.show)
        self.trayMenu.addSeparator()
        about = self.trayMenu.addAction("&关于此程序(&A)")
        about.triggered.connect(self.showAbout)
        self.trayMenu.addSeparator()
        quit = self.trayMenu.addAction("退出(&Q)")
        quit.triggered.connect(self.fullClose)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(":/Main/Media/logo.png"))
        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.activated.connect(self.iconActived)

    def iconActived(self,reason):
        mouse = QCursor()
        if reason == QSystemTrayIcon.Trigger:
            self.doIt()
        elif reason == QSystemTrayIcon.Context:
            self.trayMenu.exec_(mouse.pos())

    def doIt(self):
        try:
            clipboard=QGuiApplication.clipboard()
            beforedoit = clipboard.text()
            afterdoit = beforedoit.replace("\n"," ")
            clipboard.setText(afterdoit)
        except:
            errmessage = str(traceback.format_exc())
            self.trayIcon.showMessage("提醒",errmessage)

        # self.trayIcon.showMessage("提醒","处理完毕并且将结果复制到了你的剪贴板")
        self.trayIcon.setIcon(QIcon(":/Main/Media/logo_checked.png"))
        self.restoreTimer = QTimer()
        self.restoreTimer.start(3000)
        self.restoreTimer.timeout.connect(self.restoreLogo)
    
    def restoreLogo(self):
        self.trayIcon.setIcon(QIcon(":/Main/Media/logo.png"))

    def fullClose(self):
        self.trayIcon.hide()
        app.quit()

    def hideEvent(self,event):
        self.minWindow()
        # print("CLOSE ON")

    def minWindow(self):
        self.trayIcon.show()
        msgIcon = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Information)
        # warningIcon = QSystemTrayIcon.Warning()
        self.trayIcon.showMessage("提醒","程序已隐藏，你可以通过此重新打开程序",msgIcon)

    def traymessageClicked(self):
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setOrganizationName("Marvin Studio")
    app.setOrganizationDomain("http://www.marvinstudio.cn")
    app.setApplicationName("%s"%__TITLE__)
    app.setWindowIcon(QIcon(":/Main/Media/logo.png"))
    form = Form()
    form.show()
    app.exec_()