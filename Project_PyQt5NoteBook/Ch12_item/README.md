# 第12章 基于项的图形重点概要

> CORKINE MA (CM@MARVINSTUDIO.CN) @ 2017年12月10日(第十五周)

## 简介

本章的主要内容是使用QGraphicsItem/View/Scene三个类来绘制自定义窗口部件，相比较前一章调用QObject的PaintEvent，本章提供的框架功能更加完善，操作也更加简单。

Qt文档中给出了使用QGraphics系统绘制图案的流程，使用QGraphicsScene创建场景，使用QGraphicsView将场景添加到QObject中去。对于场景而言，其可以包含很多Item，你可以子类化Item来对单个Item进行设置。每个Item都是二维的，但有三个坐标，z轴用来判断层叠。其次，碰撞检测基于二维的x,y坐标。对项目的变换和操作会应用到其自身和子、孙对象上。对于整体的绘制，一个重要的知识点就是坐标，Qt包含一个ViewPoint也就是视口作为物理坐标，对于每一个Item都有其逻辑坐标，左上角为（0，0），子类化对象使用其父的逻辑坐标，孙类化则使用子类的逻辑坐标。

## A、页面设计器

![](/Media/1201.png)

本章包含两个例子，第一个会介绍一个简单的类似于Adobe Indesign的Page Designer程序。此程序子类化了QGraphicsView子类以实现滚轮的缩放事件和选中项目时的橡皮筋效果。在主程序窗口，此程序展示了如何将QGraphicsView和QGraphicScene联系起来，并且定义了Scene的大小（通过设置SizeHint）。

### 1、主程序主要流程以及QGraphicsScene类主要方法

QGraphicsScene中包含了很多方法，有快速添加线条、方框、线段、图片、文本的addXXX()方法，也有碰撞检测(collidingItems)、选中(items)、删除(removeItems)、更新(update)、列举(scene.view)这样对各Item进行管理的方法，更有非常好用的针对于打印机的render(p)方法。

主程序还提供了一系列和Item连接的接口，比如添加边框、图片、文字这些功能，在各方法中，程序调用了各类Item，如果此Item可以满足需求，也就是说，官方提供了快速的添加方法，比如addPixmap()，则可以直接调用，否则就需要自己子类化QGraphicsItem()类来实现特殊的自定义的功能。将一个项目添加到场景主要涉及一些操作，首先要子类化一个Item，比如添加pixmap的时候就要子类化一个QgraphicsPixmapItem()，然后使用setPos()来设置添加的位置（局部逻辑坐标），使用addItem来添加到场景，在此过程中还可以实现对transform、setFlags、setSelected这些选项进行设置。对于一个添加到场景中的项目来说，获取其坐标是一个重要的问题，可以自定义一个Position()方法，放到主窗口代码中进行主窗口和场景的坐标变换，使用mapFromGlobal(QCursor.pos())可以从物理坐标转换到逻辑坐标，这个坐标是QGraphicsView的，需要继续转换到Scene，使用mapToScene进行转换。

### 2、QgraphicsItem子类化要点

最主要的是QGraphicsItem的子类化自定义方法的编写，在初始化中最重要的是设置一个更改标记，设置字体、位置、颜色、变换、是否选中等等，一般需要重新实现的方法有：itemChange(self,change,variant)，如果发生了QGraphicsItem.ItemSelectChange,则设置标记更改，并且返回QGraphicsTextItem。itemChange(self,change,variant)这个父类的实现。

另一个比较常用的是mouseDoubleClickEvent()，在这里可以调用一个对话框或者别的，需要注意的是，如果调用对话框则必须使用父类，因此需要另外新建一个方法来说明此类的父类是什么，一般推荐新建一个parentWidget(self)，然后返回self.scene.view[0]，这个就是父类（一般来说），在双击鼠标事件中可以使用此作为父类进行调用。另外一个用的比较多的是contextMenuEvent()，keyPressEvent()用来实现键盘控制部件移动。最后，一个很重要的方法是boundingRect()，此方法表明了一个框，可以用来选择此组件。

对于QGGraphicsItem也有很多的预先设置的方法，比如_boundingRect_和_scnenbouningRect_，还有collidesWithPath、collidingItems这些碰撞检测相关函数、contains判断是否包含QPointF这个点、isSelected判断是否选中、moveBy进行偏移。_itemChange_是一个很重要的子类化方法，它什么都不做，充当信号，一般禁止使用Item.setPos()而使用itemChange进行坐标变换。_paint_方法子类化可以重绘自己，和QObj的PaintEvent很像，基于逻辑坐标系。pos返回未知、resetTransform重设变换，scale进行缩放、setCursor设置光标类型、setFocus设置焦点、setPos、setTransform、setZValue进行位置、变换、层次的设置。_shape_用来返回需要绘制的路径，碰撞检测需要对shape进行重写，_update_对Item进行更新，一般在状态改变后进行设置。

对于打印，只要声明一个QPrinter()对象，然后可以使用QPrintDialog(printer)进行设置，在模态对话框执行后，将打印机绘制到QPainter上，生成一个painter对象，对painter设置抗锯齿Hint以及对scene使用render(painter)即可将场景和painter，以及设置好的printer联系起来，进行打印。

## B、千足虫动画

![](/Media/1202.png)

第二个例子是千足虫动画，主要使用了Item的_paint_和_shape_以及碰撞检测相关功能，开始在QGraphicsView、Scene生成几条包含头和身子的虫，如果虫的身子碰撞，则颜色变蓝，如果头碰撞，则变红，变化到一定程度此虫消失。虫在场景里运动，使用定时器设置一个Pos的偏转，另外，根据屏幕大小不同可以进行不同级别的图像绘制，定时器会导致虫的移动，动画就产生了。一个亮点是，头是第一节身子的父对象，而第一节身子是之后身子的父对象，这种设计导致一旦把头删除，则所有部分都会被删除。

在程序的下方有一个zoom的杠杆，这个东西会和zoom()方法联系起来，调用self.view.setTransform()对QGraphicsView进行变换，而不是Scene，变换导致了一个全局变量的改变，然后会导致各Item在绘制过程中选择合适当前显示的细节。

头和身子都需要单独进行绘制（因为头下可能有不同段的身子），其都是继承了QGraphicsItem的类，注意在PyQt中，只能够继承一个Qt类，比如，你不能同时继承QGraphicsItem和QObject类。在每个类的初始化方法中，对于位置、颜色、定时器都有设定。会简单的开始一个定时器，此定时器和一个函数关联，在此函数中实现动作变换。

两个重要的需要重写的方法是_boundingRect_和_shape_，对于后者，需要返回一个QPainterPath()，关于Path系统提供了很多方法，如何新建、如果封闭、一些快速的方法、如何删除都有详细的介绍，具体参见QPainterPath的帮助文档，对此，我们只需要addEllipse()并且返回一个path（QPainterPath对象）就行了。

_paint(self,painter,option,widget=None)_需要重绘，因为身子的颜色变化了，形状也变化了，设置笔刷和笔之后再painter中进行绘制即可，option的类型是QStyleOptionGraphiocsItem，其包含了Item的字体、变换矩阵、调色板、状态和细节等级LOD，这有助于判断Item如何进行缩放，如果没有放大，则LOD为1.0，放大2倍，则LOD为2.0，其需要一个levelOfDetailFromTransform(martix)方法，传入的是一个矩阵，根据此矩阵判断LOD，在各种不同条件下绘制不同的细节，比如虫的外眼、内眼、鼻子等。绘制使用painter.drawEllipse,参数为其各自的逻辑坐标系，所有外部的变换都会被自动处理，不用担心。对于定时器动画需要将上述定时器信号传递给tiemout(self)方法，此方法设置颜色、角度和位置，这样在时间到期后这个头就会自己运动。另外，使用Scene的碰撞检测，也就是_collidingItems_方法判断，将这些碰撞过的头部设置颜色更红，可可以这样：item.color.setRed(XX).

大概就是这些，只要明白了流程，View、Scene、Item的主要方法以及子类化后一些关键的重写方法，使用QGraphics进行基于项的绘制还是很简单的，并且，不同于对于QWidght进行paintEvent的重新实现，使用QGraphics进行绘制更加方便，后者提供了更加丰富的函数和方法，并且性能更好。

## 程序代码参考

> [Page Designer 代码](/Project_PyQt5NoteBook/Ch12_item/writter.py)

> [千足虫动画 代码](/Project_PyQt5NoteBook/Ch12_item/multipedes.py)