#!/usr/bin/env python3
# -*- coding:utf8 -*-
import sys,traceback,time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import UI_main,RC_main
import postit
import time

__title__ ="CCNU校园网自动登录器"
__version__ = "0.3.6"
__log__ = """0.0.1 \n完成了大致的UI设计，用户名和密码会根据设置自动保存。现在你可以使用静默登录功能, 在Windows开机的时候进行登录, 登录成功后程序会自动退出。
\n0.0.2 \n修改了默认的连接时间，静默模式下系统会在程序加载5s后开始POST请求，之后10s内如果返回200状态，并登录成功且不进行其它操作则自动退出。
\n0.0.3 \n程序在静默模式下如果没有得到200状态码，则会重复POST10次，最后返回结果。
\n0.1.0 \n添加了一个自己绘制的图标，灵感来源于“网”字，以及华大的Logo。静默登陆次数更改为15次。
\n0.1.2 \n静默登录时打开界面后可以在信息栏了解当前进行的每次重连信息了。
\n0.2.0(2018-01-21) \n程序优化和重构,使用了信号和QTextbrowser代替QLabel显示连接信息。
\n0.3.0(2018-01-25) \n程序第二次重构，增加了一堆功能，最后又全部删掉了，现在更简洁。具体来说，就是，增加了有线和无线两种连接，提供一个登录失败自动\
切换的选项，提供了几个可以供测试人员测试当前连接的按钮，这几个按钮写的很漂亮，登录后按钮会被选中，注销后则自动弹起。
\n0.3.3(2018-01-25) \n提供了帮助文档。优化了连接的逻辑，界面UI等。解决了自动从旧服务器跳转连接到新服务器中出现的错误，\
现在默认会自动选择“校园网账号”继续新服务器连接。同时我们对之前未成功的POST连接提供了注销的操作，以免出现其他问题。
\n0.3.4(2018-01-25) \n修复了连接过程自动切换连接服务器时对于是否连接上网判断的一个Bug。
\n0.3.5(2018-01-25) \n在新网/旧网×正确/错误连接×直接登录/静默登录这八种情况下进行了单元测试，解决了一些出现的问题，\
现在系统可以在连接失败的情况下自动切换网络进行重新测试，在静默条件下这两个服务器的测试都是多次进行的，在直接登录条件下只进行一次（由于POST后立即GET Baidu会有一些问题，\
因此在这种情况下，程序在打不开百度的情况下也会进行4次重试）。
\n0.3.6(2018-01-26) \n修复一些BUG，优化了部分性能，测试互联网连通性超时更改为0.8s，判断次数更改为3次，之前为1s、5次。由于有时候POST返回200和正常登录成功界面，但是依旧通不过连接测试，\
所以程序对每次POST都进行了连通性的检查，在点击“登录”按钮时甚至也进行了多次POST与检查，以避免将请求错误的转移到其它服务器，这可能造成一些UI显示上的卡死问题（尚未通过多线程解决此问题）。\
在goPost()进行检查的时候，添加了1s的延迟以备服务器端准备完毕。

"""
__help__ = """<html><head/><body><p>本程序适用于华中师范大学无线网络（SSID名为&quot;CCNU&quot;）以及有线网络（包括校园有线、移动、联通和电信），提供一个方便快捷的账号认证服务。</p>
<p><span style=" font-weight:600;">自动登录指南：</span></p>
<p>1、本程序设计的一个重要目的是为了计算机的开机自动登录。您必须确认勾选了“保存密码到注册表”、正确填写了您的用户名和密码并且选择了“不显示界面自动登录”选项。为保证登录的可靠性和方便性，建议您勾选“允许自动切换服务器进行登录”。之后请按下“Windows + R”组合按键，输入“shell:startup”,将程序移动到此文件夹中即可实现开机登录。</p>
<p>敬告：如果您不允许“自动切换服务器进行登录”，则您需要手动指定登录才可以正常联网。比如，当您使用笔记本在田家炳楼（旧服务器）登录时，您选择了“校园WLAN”选项，但是如果您在图书馆登录时（使用的是新服务器），如果不勾选“自动切换服务器”，将不会顺利登录。</p>
<p><span style=" font-weight:600;">调试指南：</span></p>
<p>1、点选“测试”按钮可以打开调试界面，在此你可以对不同服务器进行登录，对当前联网状态进行测试。当进行某个服务器的登录后，登录按钮将被选中，只有点击其右边的“注销”后选中状态才会解除。</p>
<p><span style=" font-weight:600;">安全须知：</span></p>
<p>1、使用“自动登录”需打开“保存密码到注册表”选项，您的密码只会保存在本地，不会被上传。您可以使用抓包工具对此承诺进行验证。</p>
<p>2、本程序使用的“测试登录”会向“https://www.baidu.com”发送包含文件头部的Get请求，其中不包含任何隐私和统计数据。您可以使用抓包工具对此承诺进行验证。</p>
<p><span style=" font-weight:600;">程序范围</span></p><p>本程序适用于Windows NT内核，XP以上64位操作系统，包括Windows XP、Windows Vista、Windows 7、8、8.1、10。</p></body></html>"""

class Main(QDialog,UI_main.Ui_Dialog):
    postit_callback = pyqtSignal(str)
    def __init__(self,parent =None):
        super(Main,self).__init__(parent)
        self.setupUi(self)

        self.notshow = True
        self.index = 1

        settings = QSettings()
        self.userrole = settings.value("UserRole")
        setting_geo = settings.value("MainWindow/Geometry")
        if setting_geo is not None:
            self.restoreGeometry(setting_geo)

        
        # 默认配置和用户配置载入
        self.checkBox_keeppasswd.setChecked(True)
        self.checkBox_keeppasswd.setToolTip("""选择此项后将会自动保存密码到注册表。\n如果您要启用“不显示界面直接登陆”功能，请确保此项打开。""")
        self.checkBox_auth.setToolTip("选择此项后，你可以将程序添加到开机任务中，系统会自动尝试多次登录")
        self.checkBox_server.setToolTip("选择此项后，当使用指定服务器无法登录时系统会切换到其他服务器进行尝试\n当从旧服务器切换到新服务器时，会默认使用校园网账号进行连接。")
        self.radioButton_school.setToolTip("图书馆CCNU WLAN和有线（包含三家运营商和校园有线）采用的是新服务器")
        self.radioButton_wlan.setToolTip("除了图书馆的其余地方的CCNU WLAN采用的是旧服务器")
        self.pushButton_test.hide()
        self.pushButton_lanlogin.hide()
        self.pushButton_lanlogout.hide()
        self.pushButton_wlanlogin.hide()
        self.pushButton_wlanlogout.hide()
        QTimer.singleShot(0,self.loadInitialSettings)

        # 信号处理，系统脚标
        self.pushButton_test.clicked.connect(self.testLogin)
        self.pushButton_lanlogin.clicked.connect(self.testLogin)
        self.pushButton_lanlogout.clicked.connect(self.testLogin)
        self.pushButton_wlanlogin.clicked.connect(self.testLogin)
        self.pushButton_wlanlogout.clicked.connect(self.testLogin)
        self.pushButton_login.clicked.connect(self.goLogin)
        # self.pushButton_login.setToolTip("进行登录\n按下此按钮只会登录一次")
        self.pushButton_about.clicked.connect(self.aboutMe)
        self.pushButton_about.setToolTip("关于此程序和其作者")
        self.postit_callback.connect(self.updateInfo)
        self.createTrayIcon()
        self.trayIcon.messageClicked.connect(self.traymessageClicked)
        self.pushButton_exit.clicked.connect(self.fullClose)
        # self.pushButton_exit.setToolTip("退出程序而不是变成一个托盘隐藏到后台")
        self.pushButton_help.clicked.connect(self.showHelp)
        self.pushButton_help.setToolTip("帮助")
        self.pushButton_more.clicked.connect(self.showMore)
        self.pushButton_more.setToolTip("网络连接测试")

        # 细节UI
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle("%s v%s"%(__title__,__version__))

    def showMore(self):
        if isinstance(self.sender(),QPushButton):
            if self.pushButton_more.text() == "简要(&S)":
                self.pushButton_more.setText("测试(&T)")
                self.pushButton_test.hide()
                self.pushButton_lanlogin.hide()
                self.pushButton_lanlogout.hide()
                self.pushButton_wlanlogin.hide()
                self.pushButton_wlanlogout.hide()
            else:
                self.pushButton_more.setText("简要(&S)")
                self.pushButton_test.show()
                self.pushButton_lanlogin.show()
                self.pushButton_lanlogout.show()
                self.pushButton_wlanlogin.show()
                self.pushButton_wlanlogout.show()

    def updateInfo(self,info = ""):
        # print(self.sender()) <__main__.Main object at 0x00000160EF4BCC18>
        old = self.textBrowser_info.toHtml()
        if len(old) > 2000:
            old = ""
        new = old + "<p>" + info
        new = new.replace("[第1次连接]","[尝试连接]")
        # tail = new.split("\n")[-1]
        self.textBrowser_info.setHtml(new)
        self.textBrowser_info.moveCursor(QTextCursor.End)

    def loadInitialSettings(self):
        try:
            self.restoreUserrole()
            self.trayIcon.show()
            self.postit_callback.emit("读取设置成功")
            if self.userrole[4] == True:
                self.notshow = True
                QTimer.singleShot(2000,self.goSlience)
                return 0
            self.show()
            return 0
                
        except:
            # QMessageBox.warning(self,"warn",str(traceback.format_exc()))
            self.postit_callback.emit("欢迎使用")
            self.show()

    def loadUserrole(self):
        user = self.lineEdit_user.text()
        passwd = self.lineEdit_passwd.text()
        choose = (self.radioButton_school.isChecked(),self.radioButton_wlan.isChecked(),
                self.radioButton_ct.isChecked(),self.radioButton_cmcc.isChecked(),self.radioButton_cu.isChecked())
        keeppasswd = self.checkBox_keeppasswd.isChecked()
        slience = self.checkBox_auth.isChecked()
        autologin = self.checkBox_server.isChecked()
        self.userrole = [user,passwd,choose,keeppasswd,slience,autologin]

    def restoreUserrole(self):
        self.lineEdit_user.setText(self.userrole[0])
        self.lineEdit_passwd.setText(self.userrole[1])
        choose = self.userrole[2]
        self.radioButton_school.setChecked(choose[0])
        self.radioButton_wlan.setChecked(choose[1])
        self.radioButton_ct.setChecked(choose[2])
        self.radioButton_cmcc.setChecked(choose[3])
        self.radioButton_cu.setChecked(choose[4])
        self.checkBox_keeppasswd.setChecked(self.userrole[3])
        self.checkBox_auth.setChecked(self.userrole[4])
        self.checkBox_server.setChecked(self.userrole[5])

    def testLogin(self):
        if self.sender() == self.pushButton_lanlogin:
            self.pushButton_lanlogin.setChecked(True)
            self.goPost(choose = "lan",check_link_userrole=False)
        elif self.sender() == self.pushButton_lanlogout:
            self.pushButton_lanlogin.setChecked(False)
            code,_,_ = postit.loginoutCCNU()
            if code == "200":
                self.postit_callback.emit("[200] 成功注销您的新服务器登录。")
        elif self.sender() == self.pushButton_wlanlogin:
            self.pushButton_wlanlogin.setChecked(True)
            self.goPost(choose = "wlan",check_link_userrole=False)
        elif self.sender() == self.pushButton_wlanlogout:
            self.pushButton_wlanlogin.setChecked(False)
            code,_,info = postit.loginoutCCNUWLAN()
            if code == "200":
                self.postit_callback.emit("[200] 成功注销您的旧服务器登录。")
        elif self.sender() == self.pushButton_test:
            self.checkLink(show = 1)

    def goLogin(self):
        if self.checkLink(show = 0) == 1:
            self.postit_callback.emit("已连接互联网，已取消登录请求（可在“测试”选项注销服务器登录后再试）")
        else:
            r,code,_,check = self.goPost(choose = "",check_link_userrole=False)
            # 有可能存在没有连上网但是正确登录到服务器的情况。
            if code == "0" and r == "200":
                r,code,_,check = self.goPost(choose = "",check_link_userrole=True)
            if str(check) != "1":
                r,code,_,check = self.goPost(choose = "",check_link_userrole=True)
            if str(check) != "1":
                r,code,_,check = self.goPost(choose = "",check_link_userrole=True)
            if str(check) != "1":
                r,code,_,check = self.goPost(choose = "",check_link_userrole=True)
            if str(check) != "1":
                self.loadUserrole()
                autoserver = self.userrole[5]
                iswlan = self.userrole[2][1]
                userrole_temp = self.userrole
                if iswlan:
                    try:
                        postit.loginoutCCNUWLAN()
                    except Exception as err:
                        print("在旧服务器登出过程中发生错误")
                else:
                    try:
                        postit.loginoutCCNU()
                    except Exception as err:
                        print("在新服务器登出过程中发生错误")
                if autoserver:
                    if iswlan:
                        self.radioButton_school.setChecked(True)
                        self.postit_callback.emit("旧服务器无响应，正尝试其他服务器")
                        r,code,_,check= self.goPost(choose = "lan",check_link_userrole=True)
                        if str(check) != "1":
                            self.userrole = userrole_temp
                            self.restoreUserrole()
                            self.postit_callback.emit("""[FINAL]<span style=" color:#ff0000;"> 无法连接互联网。</span>""") 
                    elif not iswlan:
                        self.postit_callback.emit("新服务器无响应，正尝试其他服务器")
                        r,code,_,check = self.goPost(choose = "wlan",check_link_userrole=True)
                        if str(check) != "1":
                            self.postit_callback.emit("""[FINAL]<span style=" color:#ff0000;"> 无法连接互联网。</span>""")          
                else:
                    self.postit_callback.emit("""[FINAL]<span style=" color:#ff0000;"> 无法连接互联网。</span>""")

    def goSlience(self):
        if self.checkLink(show=0) == 1:
            self.postit_callback.emit("已连接互联网，已取消登录请求（可在“测试”选项注销服务器登录后再试）")
            msgIcon_info = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Information)
            self.trayIcon.showMessage("已连接互联网","您已在线，已取消登录请求。",msgIcon_info)
            QTimer.singleShot(10000,self.autoClose)
        else:
            r,code,_,check = self.loginSlience(choose = "")
                
            # 有可能存在没有连上网但是正确登录到服务器的情况。
            # code = self.checkLink(show=0)
            # print("OUTCODE",code)
            if str(check) != "1":
                self.loadUserrole()
                autoserver = self.userrole[5]
                iswlan = self.userrole[2][1]
                userrole_temp = self.userrole
                if iswlan:
                    try:
                        postit.loginoutCCNUWLAN()
                    except Exception as err:
                        print("在旧服务器登出过程中发生错误")
                else:
                    try:
                        postit.loginoutCCNU() 
                    except Exception as err:
                        print("在新服务器登出过程中发生错误")
                if autoserver:
                    if iswlan:
                        self.radioButton_school.setChecked(True)
                        self.postit_callback.emit("旧服务器无响应，正尝试其他服务器")
                        r,code,_,check = self.loginSlience(choose = "lan")
                        # 如果尝试更换服务器依然失败，那么换回更换之前的设置。
                        if str(check) != "1":
                            self.userrole = userrole_temp
                            self.restoreUserrole()
                    elif not iswlan:
                        # 因为使用wlan方式登陆不需要额外参数，因此只需要进行POST即可
                        print("here")
                        self.postit_callback.emit("新服务器无响应，正尝试其他服务器")
                        r,code,_,check = self.loginSlience(choose = "wlan")
                else:
                    self.postit_callback.emit("""[FINAL]<span style=" color:#ff0000;"> 无法连接互联网。</span>""")
      
        # QApplication.processEvents()
    def goPost(self,choose = "",check_link_userrole=True,show_check=True):
        # self.postit_callback.emit("登录中...")
        # 应该先判断是否当前有互联网连接，如果没有再继续下去。
        # 优先使用choose，如果没有choose字段，则使用userrole设置
        info = ""
        self.tryinfo = "[第%s次连接]"%self.index
        othererr = False
        checklink = False
        self.loadUserrole()
        user,passwd,choose_list = self.userrole[0],self.userrole[1],self.userrole[2]

        if choose == "wlan":
            print("旧服务器登录中...(来自于指定的登录方式)")
            response,code,errmesage = postit.loginCCNUWLAN(user,passwd)
        elif choose == "lan":
            print("新服务器登录中...(来自于指定的登录方式)")
            response,code,errmesage = postit.superLogin(user,passwd,choose_list)
        elif choose_list[1] == True:
            print("旧服务器登录中...(来自于用户自定义的登录方式)")
            response,code,errmesage = postit.loginCCNUWLAN(user,passwd)
        elif choose_list[1] != True:
            print("新服务器登录中...(来自于用户自定义的登录方式)")
            response,code,errmesage = postit.superLogin(user,passwd,choose_list)
            
        # print(response,code,errmesage)
        if response == "200":
            info += """<span style=" color:#00aa00;"> [200]网站已响应,</span>"""
            if code == "0":
                info = """<span style=" color:#ff0000;"> [200]网站已响应,但服务器返回了一个错误。</span>"""
            elif code == "1":
                info += """<span style=" color:#00aa00;">登录成功</span>"""
                self.index = 1
                self.tryinfo = "[连接成功]"
                checklink = check_link_userrole
        elif response == "403":
            info += """<span style=" color:#ff0000;"> [403]数据提交不完整,请重试</span>"""
        elif response == "502":
            info += """<span style=" color:#ff0000;"> [502]物理网络设备未正确设置</span>"""
        else:
            info += """<span style=" color:#ff0000;"> [ERR]其它错误。</span>"""
            othererr = True

        if othererr:
            # errmsg = QErrorMessage(self)
            # QErrorMessage.showMessage(errmsg,errmesage)
            print(errmesage)

        self.postit_callback.emit(self.tryinfo + info)
        if checklink and show_check:
            time.sleep(1)
            check = self.checkLink(show=1)
        elif checklink and not show_check:
            time.sleep(1)
            check = self.checkLink(show=0)
        elif not checklink:
            check = 2
        return response,code,errmesage,check

    def loginSlience(self,choose = "",loop = 5):
        index = 1
        response = code = errmessage = check =  None
        msgIcon_info = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Information)
        msgIcon_warn = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Warning)
        msgIcon_err = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Critical) 
        while index < loop:
            # 根据UserRole进行自动选择，所以说这里的choose为空
            response,code,errmessage,check = self.goPost(choose = choose,check_link_userrole=True,show_check=False)
            print("LOGINSLIENCE",response,code,check)
            
            print("第%s次尝试登录"%index)
            index = index + 1
            if response == "200" and code == "1" and str(check) == "1":
                break
        if response == "200" and code == "1":
            self.trayIcon.showMessage("登录成功","状态码[200]，登录成功",msgIcon_info)
            QTimer.singleShot(10000,self.autoClose)
        elif response == "200" and code == "0":
            self.trayIcon.showMessage("登录失败","[200]网站已响应,但服务器返回了一个错误。",msgIcon_err)
        elif response == "403":
            self.trayIcon.showMessage("登录失败","[403]数据提交不完整，请重新输入。",msgIcon_err)
        elif response == "502":
            self.trayIcon.showMessage("登录失败","[502]网络未联通，请检查硬件连接。",msgIcon_warn)
        else:
            self.trayIcon.showMessage("登录失败","[ERR]硬件故障",msgIcon_err)
        return response,code,errmessage,check


    def checkLink(self,show=1):
        state,code,info = postit.testNet(3)
        if state == "200" and code == "1":
            if show != 0:
                self.postit_callback.emit("[测试连接] " + info)
            return 1
        elif state == None and code == "0":
            if show != 0:
                self.postit_callback.emit("[测试连接] " + info)
            return 0
        else:
            QMessageBox.information(self,"Website Checker",str(info)) 

    def autoClose(self):
        if not self.isVisible():
            QTimer.singleShot(1000,self.fullClose)

    def fullClose(self):
        self.trayIcon.hide()
        self.close()
        app.quit()

    def hideEvent(self, event):
        msgIcon = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Information)
        self.trayIcon.showMessage("提醒","程序已隐藏，你可以通过此重新打开程序",msgIcon)

    def closeEvent(self, event):
        # close not quit also triggered this Event
        self.loadUserrole()
        if not self.userrole[3]:
            self.userrole[1] = ""
        settings = QSettings()
        settings.setValue("UserRole",self.userrole)
        settings.setValue("MainWindow/Geometry",QVariant(self.saveGeometry()))

    def createTrayIcon(self):
        self.trayMenu = QMenu()
        showAction = self.trayMenu.addAction("打开主程序(&O)")
        showAction.triggered.connect(self.show)
        about = self.trayMenu.addAction("关于此程序(&A)")
        about.triggered.connect(self.aboutMe)
        self.trayMenu.addSeparator()
        quit = self.trayMenu.addAction("退出(&Q)")
        quit.triggered.connect(self.fullClose)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(":/Main/Media/logo.png"))
        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.activated.connect(self.iconActived)
        
    def traymessageClicked(self):
        self.show()

    def iconActived(self,reason):
        mouse = QCursor()
        if reason == QSystemTrayIcon.Trigger:
            self.show()
        elif reason == QSystemTrayIcon.Context:
            self.trayMenu.exec_(mouse.pos())
    
    def aboutMe(self):
        # QMessageBox.aboutQt(self,"About Qt")
        aboutDlg = QMessageBox()
        aboutDlg.about(self,"%s - About"%__title__,
        """<html><head/><body>
        <p>%s version %s    </p><p/>
        <p>Written by <span style=" font-weight:600;">Corkine Ma</span></p>
        <p>Email:cm@marvinstudio.cn    </p><p/>
        <p>本程序使用 Python 和 Qt 开发，程序遵循GPL v2开源协议，你可以在<a href="http://tools.mazhangjing.com"><span style=" text-decoration: underline; color:#0000ff;">http://tools.mazhangjing.com</span></a> 此网站找到程序的源代码，如果没有，请联系作者。</p>
        </body></html>
        """%(__title__,__version__)
        
        )
        # QMessageBox.information(self,"%s - 更新日志"%__title__,"%s"%__log__)
        box = AboutBox("%s"%__log__,"%s - 更新日志"%__title__,self)
        box.show()

    def showHelp(self):
        box = AboutBox("%s"%__help__,"%s - 帮助"%__title__,self)
        box.show()

class AboutBox(QDialog):
    def __init__(self, text = "" ,title = "", parent =None):
        super(AboutBox,self).__init__(parent)
        self.info = QTextBrowser()
        self.info.setText(text)
        self.okbutton = QPushButton("确定(&O)")
        self.okbutton.clicked.connect(self.close)
        self.aboutbutton = QPushButton("官方网站(&W)")
        self.aboutbutton.clicked.connect(self.showWebsite)
        self.aboutqt = QPushButton("About &Qt")
        self.aboutqt.clicked.connect(self.aboutQt)

        layout = QVBoxLayout()
        layout.addWidget(self.info)
        blayout = QHBoxLayout()
        blayout.addWidget(self.aboutqt)
        blayout.addStretch()
        blayout.addWidget(self.aboutbutton)
        blayout.addWidget(self.okbutton)
        layout.addLayout(blayout)
        self.setLayout(layout)
        self.resize(QSize(500,400))
        self.setWindowTitle(title)

    def showWebsite(self):
        QDesktopServices.openUrl(QUrl("http://www.marvinstudio.cn"))
        
    def aboutQt(self):
        QMessageBox.aboutQt(self,"About Qt")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("CCNU Internet AutoLogin")
    app.setWindowIcon(QIcon(":/Main/Media/logo.png"))
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Marvin Studio")
    app.setOrganizationDomain("http://www.marvinstudio.cn")
    app.setQuitOnLastWindowClosed(False)
    form = Main()
    if form.notshow == False:
        form.show()
    # box = AboutBox("fefe","fewf")
    # box.show()
    app.exec_()
    