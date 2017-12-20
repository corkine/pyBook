# Python Qt GUI 编程 - PyQt5 资源和UI文件自动转换器

## 使用说明

这个程序是用来将Qt设计师制作的.ui设计文件和.qrc资源文件转换成为python模块。使用时简单的将UI文件和QRC资源文件拖拽到对应的TextEdit框内即可，然后点击右边的命令，可以单个生成，也可以点击最下面的“Make ALL”全部生成，生成的文件在项目文件夹中，即你拖拽过来的那些文件的相同文件夹中。

单击“关闭”不会关闭程序，你需要点击“Exit”按钮才能退出。点击右上角只会将程序隐藏到系统托盘，托盘图标单击可以快速调出程序，托盘图标右键可以直接根据上次结果重新生成UI和QRC文件，如果某个生成错误，则自动跳过，最后的结果和处理流程展示在一个对话框里。

![](/Media/rccuic.png)

![](/Media/rccuic2.png)

## 依赖

二进制文件（dist目录下）可在Windows XP 以上的 ×64 Windows 操作系统运行

python文件可以在任何安装了PyQt5和SIP的绝大部分现代计算机系统上运行，比如Linux，Windows，macOS等。

## 亮点

- 托盘菜单快速生成文件
- 自定义拖拽组件
- 子进程和输出流的截取与呈现

> [查看项目和文件](https://github.com/corkine/pyBook/tree/master/Project_PyQt5_RCC_UIC_Maker)