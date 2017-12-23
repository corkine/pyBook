#!/usr/bin/env python3
# -*- coding:utf8 -*-
import sys,time,platform,traceback,os
from tkinter import Tk
from tkinter.messagebox import showwarning
try:
    import PyQt5
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    import UI_noticedlg
    import appsetting
    import process
    from checkandsend import checkDaily
    import RC_everydaynotice
except:
    Tk().withdraw()
    warn = showwarning("WARNING",traceback.format_exc())
    warn

# os.chdir("C:/Users/Administrator/Desktop\pyBook/Project_EveryDayNotice")
# 对于首层框架的import最好调用try语句，打印错误，不用在各个模块调用即可。
# 这两行是为了check后如果更新程序输出结果用的，因为在那里还没有实例化qdialog因此不能用pyqt
__VERSION__ = '0.2.9d'
# 0.2.6 更改了一个逻辑错误：先判断，再更改值输出，这样写入到注册表的值不会出错。
__UDATA__ ="""
<html><head/><body>
<p><span style=" font-weight:600; text-decoration: underline;">版本 0.2.9</span></p>
<p>1、增加了一个统一处理文件的对话框，可以对其进行打印预览、批量发送邮件。</p>
<p>2、添加和更新了一个新的图标作为Logo。</p><p><span style=" font-weight:600; text-decoration: underline;">版本 0.2.6</span></p><p>1、修复了点击右上角关闭按钮的时候，注册表记录当日日记状态为“完成”这一错误。</p>
<p>2、添加了“更新日志”菜单和对话框，程序更加完善。</p>
<p><span style=" font-weight:600; text-decoration: underline;">版本 0.2.5</span></p>
<p>1、添加了“检测日记文件”功能，现在程序不仅会在运行前检查日记文件，当弹出提醒，用户点击“完成了”之后，只有在相应目录找到日记文件，提醒程序才会自动关闭，否则，你只有强制关闭。</p>
<p><span style=" font-weight:600; text-decoration: underline;">版本 0.2.0</span></p>
<p>1、添加了“完成了”按钮，不再将这个选项隐藏到菜单中了。</p>
<p><span style=" font-weight:600; text-decoration: underline;">版本 0.1.0</span></p>
<p>1、程序由VB.NET语言迁移到Python + Qt语言开发。</p>
<p><span style=" font-weight:600; text-decoration: underline;">即将更新功能：</span></p>
<p>- 积分和奖励系统 [预计1.0.0]</p><p>- 对一个文件包含几天日记的算法的判断 [预计0.3.0]</p>
</body></html>
"""
StyleSheet="""
QLabel#label_num{
    color:red;
}

"""
class Form(QDialog,UI_noticedlg.Ui_Dialog):
    def __init__(self,parent=None):
        super(Form,self).__init__(parent)
        self.setupUi(self)
        self.starttime=time.ctime()
        self.label_num.setText(" 1")
        self.setStyleSheet(StyleSheet)
        self.culc = 1
        self.timer = QTimer()
        self.finalstate = 0
        self.time = ''
        for ele in time.localtime()[0:3]:
            self.time += str(ele)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint)
        self.setWindowFlag(Qt.WindowCloseButtonHint,False)
        
        settings =QSettings()
        self.re_lastinfo = settings.value("MainWindow/LastDay")
        # print(self.re_lastinfo)
        if self.re_lastinfo != None:
            if str(self.re_lastinfo.split(",")[2]) == '1':
                pass
            elif str(self.re_lastinfo.split(",")[2]) == '2':
                self.label_Info.setText("昨天没有写日记，那么今天呢？")
            elif str(self.re_lastinfo.split(",")[2]) == '0':
                self.label_Info.setText("检测到上次程序异常退出，请及时记录日记")
        self.infomation = "确认离开程序？"
        # self.label_hide.setText("确认离开程序？")
        self.pushButton.clicked.connect(self.startNow)
        self.timer.timeout.connect(self.test)
        self.pushButton_ok.clicked.connect(self.finishLoop)
        # self.finalstate.valuechanged.connect(self.callClose)
        # self.label_hide.textChanged.connect(self.callClose)
    def startNow(self):
        self.hide()
        self.timer.start(2400000)
        self.culc += 1
        self.label_num.setText(str(self.culc) if len(str(self.culc)) > 1 else ' '+str(self.culc))
    
    def test(self):
        # print("ONE LOOP")
        self.show()

    def finishLoop(self):
        
        self.infomation = "咆哮吧，咆哮，怒斥那光的退缩"

        result_bool,result_1,result_2,result_txt = appsetting.runCheck(sendmail=False)
        if result_bool == True:
            if result_txt == '成功检索数据，但未发现新数据':
                QMessageBox.warning(self,"提示","未发现新的日记文件,请检查后再试。")
            else:
                # QMessageBox.information(self,"处理完毕",'%s\n%s\n%s\n%s'%('处理结果：',result_1,result_2,result_txt),
                #     QMessageBox.Ok)
                processdlg = process.ProcessForm('daily.setting')
                if processdlg.exec_():
                    pass
                self.finalstate = 1 # 不能放前面，只有当检查过后才更改值
                self.infomation = "不废话，直接退出"
                self.close()
        elif result_bool == False:
            if QMessageBox.warning(self,"提示","读取设置文件出错，你想要打开设置配置对话框进行配置吗？",
                    QMessageBox.Ok|QMessageBox.Cancel) == QMessageBox.Ok:
                self.showSettingDlg()
            else:
                pass


    def unfinishLoop(self):
        self.finalstate = 2
        self.infomation = "好好休息"
        self.close()


    def contextMenuEvent(self,event):
        menu = QMenu()
        finishedAction = menu.addAction("写完了(&F)")
        finishedAction.triggered.connect(self.finishLoop)
        if self.re_lastinfo != None:
            if str(self.re_lastinfo.split(",")[2]) == '1': 
                #因为有三个值，0为异常，1为昨日成功记日记，2为昨日跳过
                unfinishedAction = menu.addAction("今天太累，明天补上(&T)")
                unfinishedAction.triggered.connect(self.unfinishLoop)
        else:pass
        menu.addSeparator()
        settingAction = menu.addAction("配置程序(&S)")
        settingAction.triggered.connect(self.showSettingDlg)
        processAction = menu.addAction("数据处理对话框(&D)")
        processAction.triggered.connect(self.showProcessDlg)
        aboutAction = menu.addAction("关于此程序(&A)")
        aboutAction.triggered.connect(self.showMe)   
        updateAction = menu.addAction("更新日志(&U)")
        updateAction.triggered.connect(self.showUpdate)  
        menu.exec_(event.globalPos())

    def closeEvent(self,event):
        if self.infomation == "不废话，直接退出":
            pass
        else:
            if QMessageBox.information(self,"提示",self.infomation,QMessageBox.Ok|QMessageBox.Cancel) == QMessageBox.Cancel:
                event.ignore()

        settings = QSettings()
        settings.setValue("MainWindow/LastDay",QVariant(self.writeInfo()))
        settings.setValue('Data/'+self.time,QVariant(self.writeInfo()))

    def writeInfo(self):
        info = "%s,%s,%s,%s"%(str(time.ctime()),str(self.culc),str(self.finalstate),str(self.starttime))
        return str(info)

    def showSettingDlg(self):
        settingdlg = appsetting.Form(self)
        if settingdlg.exec_():
            pass

    def showProcessDlg(self):
        try:
            processdlg = process.ProcessForm('daily.setting')
            if processdlg.exec_():
                pass
        except:
            Tk().withdraw()
            warn_info = showwarning("WARN","没有检测到daily.setting文件或者从此文件中读取信息出错，请在“配置程序”中进行正确配置。")

    def showMe(self):
        QMessageBox.about(self,"关于此程序",
                        """<b>cmDaily 日记提醒程序</b> v%s
                        <p>     
                        <p>Written by Corkine Ma (cm@marvinstudio.cn)
                        <p>此程序主要功能为日记提醒。程序检查文件夹中是否有符合正则表达式的日记文件，如果有
                        则自动发送到指定邮箱，相关参数可使用右键进行配置。此程序遵守GPL v2协议开源。
                        <p>本程序引用库：Python %s , Qt %s , PyQt %s
                        <p>Copyright &copy; 2017 Marvin Studio. All Right Reserved.
                        
                        """%(__VERSION__,platform.python_version(),QT_VERSION_STR,PYQT_VERSION_STR))

    def showUpdate(self):
        QMessageBox.information(self,"更新日志",
                        """<b>cmDaily 日记提醒程序</b> v%s
                        <p>%s
                        <br>
                        <p>本程序引用库：Python %s , Qt %s , PyQt %s
                        <p>Copyright &copy; 2017 Marvin Studio. All Right Reserved.
                        
                        """%(__VERSION__,__UDATA__,platform.python_version(),QT_VERSION_STR,PYQT_VERSION_STR))

    def writeSettings(self):
        self.finalstate = 1
        settings = QSettings()
        settings.setValue("MainWindow/LastDay",QVariant(self.writeInfo()))
        settings.setValue('Data/'+self.time,QVariant(self.writeInfo()))

if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Daily Notice")
    app.setOrganizationName("Marvin Studio")
    app.setOrganizationDomain("http://www.marvinstudio.cn")
    app.setWindowIcon(QIcon(":/Main/Media/logo.png"))
    form = Form()
    # from checkandsend import *
    # 系统会自动导入依赖，所以不用在这里继续导入，只用负责处理appsetting中传递过来的东西就好

    result_bool,result_1,result_2,result_txt = appsetting.runCheck(sendmail=False)
    # print('字符串1\n\n\n\n\t'+str(result_bool),'字符串2\n\n\n\n\t'+result_1,'字符串3\n\n\n\n\t'+result_2,'字符串4\n\n\n\n\t'+result_txt)
    # checkDaily()
    if result_bool == True:
        if result_txt == '成功检索数据，但未发现新数据':
            form.show()
            app.exec_()
        # else:
        #     Tk().withdraw()
        #     warn_info = showwarning("处理完毕",'%s\n%s\n%s\n%s'%('处理结果：',result_1,result_2,result_txt))
        #     warn_info

            # Python 自动回收了程序
        else:
            # print("hello")

            form.writeSettings()
            processdlg = process.ProcessForm('daily.setting')
            if processdlg.exec_():
                pass
    elif result_bool == False:
        print("读取设置出错,请打开程序后右键选择“配置程序”\n详细信息:%s"%result_txt)
        settingdlg = appsetting.Form()
        if settingdlg.exec_():
            form.show()
            app.exec_()
        else:
            form.show()
            app.exec_()
    

    