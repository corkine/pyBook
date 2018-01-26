> 本程序可用于华中师范大学无线校园网（SSID:CCNU）以及有线校园网的连接认证，可以替代网页认证。本程序适用于解决：1、开机程序自动登录网络，而无须手动干预。2、连接网络后打不开认证界面（尤其是宿舍晚上以及图书馆等人较多的地方）。由于学校网络认证复杂，新旧混乱，因此程序提供了自动切换认证服务器的功能。

比如，当你在田家炳登录，使用的是旧认证服务器，而在图书馆登录，使用的是新服务器，二者登录地址不同，传递参数不同，采用一般登录脚本，虽然可以登录，但是由于登录的服务器不是当前区域的服务器，因此亦不能上网。本程序可自动识别和判断与自动切换，一切只需要按下“登录”按钮，或者启动应用即可（静默登录模式下）。虽然说，正因如此，本来50行的程序活生生的写了500行。

![](/Media/login.png)

## 一、写作缘由

学校校园网的登录认证的主要方式是连接有线或者无线，之后等系统弹出登录网页，或者你自己上一个网站，会自动跳转到登录界面，在大多数情况下，这没有什么问题，但是在人比较多的时候，比如图书馆，或者信号覆盖不是很好的时候，就不会弹出这个页面，网络状态直接显示感叹号，网页打不开，更有甚者，即便是手动输入认证服务器网址，也有一定几率打不开登录页面。

这个程序本来是写给自己用来自动登录有线网的，在NAS里做自动开机登录使用，这个脚本写的很简单，就十几行代码。后来想要自己的笔记本也可以自动登录无线网，就扩充了下脚本，但是，当真正开始用的时候，发现了很多的问题，这些问题都是脚本难以解决的，就干脆把脚本扩展成了GUI程序，并且同时支持了无线网络和有线网络的登录，以及旧认证服务器和新认证服务器的自动切换登录。

## 二、学校网络概况
这是2018年1月份写的程序，在这个时候，学校的校园网主要包含有线和无线两种连接方式，其中有线，包括校园网有线、三家运营商的有线，这四种登录方式使用的是新的服务器，也就是2017年底部署的新的认证服务器，登录网址为login.ccnu.edu.cn，或者l.ccnu.edu.cn，或者是10.220.250.50，认证地址为：

> http://10.220.250.50/0.htm

无线的话，比较复杂，在不同地方的无线服务器不同，有些地方，比如图书馆，使用的是新的认证服务器（登陆界面包含输入用户名、密码、运营商选择三个部分），认证地址和上面的一样。但是，在大部分学校的其它地方，比如田家炳楼、宿舍无线使用的是旧的服务器，其打开界面后没有选择运营商的RadioButton，只有输入用户名和密码的地方，其认证地址为：

> http://securelogin.arubanetworks.com/auth/index.html/uauth/index.html/u

但是，有些时候，在本该属于新服务器认证的地方，偶尔会跳转到旧服务器认证，所以，如果想要正确登录，就需要尝试不同的服务器，但是，新的问题是，在旧服务器认证的时候，新服务器地址是可以POST通的，并且可以正常返回200并打开正常登录页面的，但是，其它正常外网网页是登不上的，因此，设计自动登录程序的时候当POST返回200和正确网页之后还需要测试是否可以打开外网，更有甚者，很多时候，就算是正确的服务器，POST返回200和正确网页后还是打不开外网，这极大增加了登录脚本的复杂度。

## 三、功能

程序主界面如图所示：

![](/Media/login_show.png)

### 1、静默登陆

![](/Media/login_s.png)

程序添加到开机启动项并且勾选“静默登录”后，开机时会自动登录，程序不会显示主界面，只有状态栏图标和气泡通知。

### 2、记住密码

密码会保存在注册表，只保存在本地，不会上传。

### 3、自动切换服务器登录

![](/Media/login4.png)

当新服务器无法使用时，勾选此项会自动切换服务器重试。推荐搭配静默登录一起使用。

### 4、调试网络

![](/Media/login3.png)

在“调试”按钮下，你可以测试用户名、密码到各个服务器的连通性，当登录时，按钮会被选中，当你注销后会自动取消选中。

### 5、附加

当你当前已经连接网络时，程序不会继续登录，你可以在“调试”注销相应服务器后再登录。


## 四、Logo设计

![](/Media/logo2.png)

这个程序的Logo是一个“网”字，底色采用了华大的标志色——青，构思还可以，起码比我之前自己随手从网上找的一个地球强一些，虽然这个也是在Ai里自己画的。我始终相信这一点：

> 一个花费心思制作的，并且每天都用到的东西，值得设计者让它好看一点，尽管好不好看并不是它的主要功能。

## 五、语言和依赖

Python 3.X，需要安装requests包（脚本）以及pyqt5包（GUI）。

测试平台为Windows 10 X64，macOS HS。

## 六、程序

![](/Media/loginmac.png)

直接上程序吧，具体项目参见[项目Github仓库](https://github.com/corkine/pyBook/tree/master/Project_CCNULogin)。唯一感叹一点的就是，区区四五行的POST登陆，真正实现成一个功能，竟然写了个500行的程序，其中接近400行处理相关逻辑，100行左右处理UI。一个遗憾是，没有使用多线程，因为Qt的多线程还没有开始学习，Python的多线程和PyQt兼容性不太好，并且也不安全，所以就没有用。

postit.py这个是脚本，可以直接使用，不过要实现自动登录、自动判断登录状态并且在多次登录失败的情况下切换新旧服务器，以及GUI的话，就需要另一个main.py以及资源、UI布局文件，直接运行main.py即可。

### 打包可执行（EXE）文件下载

Windows打包二进制文件适用于64位PC，不需要任何依赖，不需要Python和其依赖包，可以直接执行，程序在/dist目录下，[点击下载](https://github.com/corkine/pyBook/raw/master/Project_CCNULogin/dist/CCNULogin.rar)

## 七、程序核心代码

### 1、登录和注销API调用代码

    import requests,json
    import traceback
    def loginCCNU(username="",passwd="",suffix=""):
        errmessage = None
        try:
            url = "http://10.220.250.50/0.htm"
            payload = {"DDDDD":"%s"%username,
                    "upass":"%s"%passwd,
                    "suffix":"%s"%suffix,
                    "0MKKey":"123"}
            headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
                        "Content-Type": "application/x-www-form-urlencoded",}
            r = requests.post(url, data=payload ,headers = headers)
            # print(r.text)
            if "您已登录成功，欢迎使用！请不要关闭本页。" in r.text:
                return str(r.status_code),"1",errmessage
            else:
                return str(r.status_code),"0",errmessage
        except:
            errmessage = str(traceback.format_exc())
            return None,"0",errmessage

    def loginoutCCNU(username="",passwd="",suffix=""):
        errmessage = None
        try:
            url = "http://10.220.250.50/F.htm"
            headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
                        "Content-Type": "application/x-www-form-urlencoded",}
            r = requests.get(url ,headers = headers)
            # print(r.text)
            if "华中师范大学无线校园网登录" in r.text:
                return str(r.status_code),"0","已注销"
            else:
                return str(r.status_code),"0","返回未知网页"
        except:
            errmessage = str(traceback.format_exc())
            return None,"0",errmessage


### 2、核心登录代码

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


### 3、静默登陆和服务器自动切换代码

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

## 八、版权、作者和使用说明

![](/Media/login_cp.png)

本程序使用 Python 和 Qt 开发，程序遵循GPL v2开源协议，你可以在 http://tools.mazhangjing.com 此网站找到程序的源代码，如果没有，请联系作者。