import traceback,os,subprocess,shlex
import sys
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import RC_rcc_uic_maker

__version__ = "0.1.0"
__title__ = "PyQt5 RCC & UIC Maker"
__log__ = """
%s, 当前版本 ver %s<br><br>
<b>2017-12-19 版本0.0.1 更新日志：</b><br>

提供了一个整合的拖拽框，可以接收UI和RCC文件，点击按钮后可以在原始目录生成对应文件。<br><br>
<b>2017-12-20 版本0.1.0 更新日志：</b><br>
整合了子进程的输出，添加了托盘以及快速更新菜单，添加了注册表信息恢复，修复了Bug，提高了稳定性<br><br>
...

"""%(__title__,__version__)

class Maker(QDialog):
    def __init__(self,parent=None):
        super(Maker,self).__init__(parent)
        self.buttonGo = QPushButton("&Make UIC")
        self.buttonGo_2 = QPushButton("Ma&ke RCC")
        self.buttonGo_3 = QPushButton("Make &All")
        self.dropArea = DropTextEdit("将UIC文件拖放至此<br><br>生成的文件在原始程序目录下")
        self.dropArea_2 = DropTextEdit("将RCC文件拖放至此<br>")
        self.label_UIC = QLabel("&UIC Maker")
        self.label_UIC.setBuddy(self.dropArea)
        self.label_RCC = QLabel("&RCC Maker")
        self.label_RCC.setBuddy(self.dropArea_2)
        self.buttonHelp = QPushButton("&Help")
        self.check_path = QLineEdit()
        self.label_path = QLabel("&Path: ")
        self.label_path.setBuddy(self.check_path)
        self.trayButton = QPushButton("&Exit")
        self.aboutButton = QPushButton("A&bout")
        layout = QGridLayout()
        layout.addWidget(self.dropArea,1,0,8,5)
        layout.addWidget(self.dropArea_2,10,0,8,5)
        layout.addWidget(self.buttonHelp,16,5,1,1)
        layout.addWidget(self.aboutButton,15,5,1,1)
        layout.addWidget(self.trayButton,17,5,1,1)
        layout.addWidget(self.buttonGo,1,5,1,1)
        layout.addWidget(self.buttonGo_2,10,5,1,1)
        layout.addWidget(self.label_UIC,0,0,1,2)
        layout.addWidget(self.label_RCC,9,0,1,2)
        pathLayout = QHBoxLayout()
        pathLayout.addWidget(self.label_path)
        pathLayout.addWidget(self.check_path)
        pathLayout.addWidget(self.buttonGo_3)
        layout.addLayout(pathLayout,18,0,1,6)
        self.setLayout(layout)

        self.dropArea.setAcceptDrops(True)
        self.dropArea.textChanged.connect(self.updateUIAddress)
        self.dropArea_2.textChanged.connect(self.updateRCAddress)
        self.buttonGo.clicked.connect(self.checkandGo)
        self.buttonGo_2.clicked.connect(self.checkandGo)
        self.buttonGo_3.clicked.connect(self.checkandGo)
        self.trayButton.clicked.connect(self.fullClose)
        self.aboutButton.clicked.connect(self.aboutMe)
        self.type =""
        self.address = ""
        self.restoreData()
        self.setWindowTitle("%s ver %s"%(__title__,__version__))
        self.createTrayIcon()
        self.trayIcon.messageClicked.connect(self.traymessageClicked)
        
        self.log = self.log_err = ""
        self.temp_out = sys.stdout
        self.temp_error = sys.stderr
        sys.stdout = open("result.log","w+")
        sys.stderr = open("error.log","w+")

    def aboutMe(self):
        # QMessageBox.aboutQt(self,"About Qt")
        aboutDlg = QMessageBox()
        aboutDlg.about(self,"%s - About"%__title__,
        """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
    <html><head><meta name="qrichtext" content="1" /><style type="text/css">
    p, li { white-space: pre-wrap; }
    </style></head><body style=" font-family:'SimSun'; font-size:9pt; font-weight:400; font-style:normal;">
    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">%s version %s</p>
    <p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Written by <span style=" font-weight:600;">Corkine Ma</span></p>
    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Email:cm@marvinstudio.cn</p>
    <p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">本程序使用 Python 和 Qt 开发，程序遵循GPL v2开源协议，你可以在http://tools.mazhangjing.com 此网站找到程序的源代码，如果没有，请联系作者。</p></body></html>
        """%(__title__,__version__)
        
        )
        QMessageBox.information(self,"%s - 更新日志"%__title__,"%s"%__log__)

    def createTrayIcon(self):
        self.trayMenu = QMenu()
        showAction = self.trayMenu.addAction("打开主程序(&O)")
        showAction.triggered.connect(self.show)
        self.updateallAction = self.trayMenu.addAction("重新生成UI和RC文件(&R)")
        self.updateallAction.triggered.connect(self.checkandGo)
        self.trayMenu.addSeparator()
        about = self.trayMenu.addAction("&关于此程序(&A)")
        about.triggered.connect(self.aboutMe)
        # setting = self.trayMenu.addAction("设置(&S)")
        self.trayMenu.addSeparator()
        quit = self.trayMenu.addAction("退出(&Q)")
        quit.triggered.connect(self.fullClose)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(":/Main/Media/uic_rcc_logo.png"))
        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.activated.connect(self.iconActived)

    def fullClose(self):
        # app.setQuitOnLastWindowClosed(True)
        # self.close()
        self.trayIcon.hide()
        app.quit()

    def iconActived(self,reason):
        mouse = QCursor()
        if reason == QSystemTrayIcon.Trigger:
            self.show()
        elif reason == QSystemTrayIcon.Context:
            self.trayMenu.exec_(mouse.pos())
    
    def hideEvent(self,event):
        self.minWindow()
        # print("CLOSE ON")

    def minWindow(self):
        self.trayIcon.show()
        msgIcon = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Warning)
        # warningIcon = QSystemTrayIcon.Warning()
        self.trayIcon.showMessage("提醒","程序已隐藏，你可以通过此重新打开程序",msgIcon)

    def traymessageClicked(self):
        self.show()
    # def areadropEvent(QDropEvent,)
    def updateUIAddress(self):
        address_UI = self.dropArea.address
        if address_UI == "":
            address_UI = self.dropArea.toPlainText()
        if str(address_UI)[:8] == "file:///":
            address_UI = address_UI[8:]
            if address_UI[-3:] == ".ui":
                self.address_UI = address_UI
                print("\n[UI ADDRESS IS]: \n",self.address_UI)
            else:
                QMessageBox.warning(self,"WARN","错误，不是UI文件")
        else:
            QMessageBox.warning(self,"WARN","错误，不是文件")

    def updateRCAddress(self):
        address_RC = self.dropArea_2.address
        if address_RC == "":
            address_RC = self.dropArea_2.toPlainText()
        if str(address_RC)[:8] == "file:///":
            address_RC = address_RC[8:]
            if address_RC[-4:] == ".qrc":
                self.address_RC = address_RC
                print("\n[RC ADDRESS IS]: \n",self.address_RC)
            else:
                QMessageBox.warning(self,"WARN","错误，不是RC文件")
        else:
            QMessageBox.warning(self,"WARN","错误，不是文件")

    def checkandGo(self):
        try:
            def run():
                if self.check_path.text() == "":
                    QMessageBox.information(self,"警告","请输入Qt路径")
                else:
                    path = self.check_path.text()
                    filename = str(self.address.split("/")[-1])
                    newname = str(self.type)+"_"+str(filename.split(".")[0])+".py"
                    # print(path)
                    print("\n[FILENAME]: \n",filename,newname)

                    pyfile = self.address.split(filename)[0]+newname 
                    localfile = self.address.split(filename)[0]+filename
                    if self.type == "RC":
                        command = "pyrcc5 -o "+pyfile+" "+localfile
                    elif self.type == "UI":
                        command = "pyuic5 -o "+pyfile+" "+localfile

                    # print("执行的命令是: ",command)
                    # command ="dir"
                    # arg1=shlex.split(command)
                    # print(arg1)
                    
                    command = command.replace("/","\\")
                    arg1 = command
                    print("\n[Windows Style Command]: \n",command,"\n\n[Traceback]: \n")

                    if sys.platform[:3] == "win":
                        si = subprocess.STARTUPINFO()
                        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                        p = subprocess.Popen(arg1,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT,startupinfo=si)
                    else:
                        p = subprocess.Popen(arg1,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    self.setWindowTitle("%s ver %s [完成]"%(__title__,__version__))
                    print(p.communicate())

            sender = self.sender()
            # print(sender)
            if sender == self.buttonGo:
                print("\nGO UI ------------------------------>\n")
                self.type = "UI"
                self.address = self.address_UI
                run()
            elif sender == self.buttonGo_2:
                print("\nGO RC ------------------------------>\n")
                self.type = "RC"
                self.address = self.address_RC
                run()
            elif sender == self.buttonGo_3:
                print("\nUpdate ALL ---------------------------->\n")
                self.type = "UI"
                self.address = self.address_UI
                run()
                self.type = "RC"
                self.address = self.address_RC
                run()
            elif sender == self.updateallAction:
                print("\nUpdate ALL At context---------------------------->\n")
                try:
                    self.type = "UI"
                    self.address = self.address_UI
                    run()
                finally:
                    self.type = "RC"
                    self.address = self.address_RC
                    run()
                    print("在UI文件生成中发生错误，已跳过")

            try:
                sys.stdout.close()
                sys.stderr.close()
                result = open("result.log","r").read()
                result_err = open("error.log","r").read()
                QMessageBox.information(self,"RESULT",str(result)+"\n"+str(result_err))
                sys.stdout = open("result.log","w+")
                sys.stderr = open("error.log","w+")
            except:
                QMessageBox.warning(self,"WARN",traceback.format_exc())
            
            
                
        except:
            
            QMessageBox.warning(self,"WARN",traceback.format_exc())

    def restoreData(self):
        try:
            settings = QSettings()
            setting_geo=settings.value("MainWindow/Geometry")
            if setting_geo is not None:
                self.restoreGeometry(setting_geo)
            self.check_path.setText(str(settings.value("RecentPath")))
            self.dropArea.setText(str(settings.value("RecentUIC")))
            self.dropArea_2.setText(str(settings.value("RecentRCC")))
        except:
            QMessageBox.warning(self,"WARN",str(traceback.format_exc()))

    def closeEvent(self,event):
        settings = QSettings()
        data = self.check_path.text()
        rccdata  = self.dropArea_2.toPlainText()
        uicdata = self.dropArea.toPlainText()
        settings.setValue("RecentPath",data)
        settings.setValue("MainWindow/Geometry",QVariant(self.saveGeometry()))
        settings.setValue("RecentRCC",rccdata)
        settings.setValue("RecentUIC",uicdata)





class DropTextEdit(QTextEdit):
    
    def __init__(self, parent=None):
        super(DropTextEdit, self).__init__(parent)
        self.setAcceptDrops(True)
        self.address = ''
    def dropEvent(self, event):
        try:
            self.address = event.mimeData().text()
            self.setText(self.address)
        except:
            self.setText("参数传递出错，请重试")
            

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setOrganizationName("Marvin Studio")
    app.setOrganizationDomain("http://www.marvinstudio.cn")
    app.setApplicationName("RCC & UIC Marker")
    app.setWindowIcon(QIcon(":/Main/Media/uic_rcc_logo.png"))
    app.setQuitOnLastWindowClosed(False)
    form = Maker()
    form.show()
    app.exec_()
