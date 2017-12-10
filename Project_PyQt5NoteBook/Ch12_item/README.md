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

> Page Designer 代码
```python
#!/usr/bin/env python3
# -*- coding:utf8 -*-

import functools
import random
import sys
from PyQt5.QtCore import (QByteArray, QDataStream, QFile, QFileInfo,
                          QIODevice, QPoint, QPointF, QRectF, Qt)
from PyQt5.QtWidgets import (QApplication, QDialog,
                             QDialogButtonBox, QFileDialog, QFontComboBox,
                             QGraphicsItem, QGraphicsPixmapItem,
                             QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGridLayout,
                             QHBoxLayout, QLabel, QMenu, QMessageBox,QPushButton, QSpinBox,
                             QStyle, QTextEdit, QVBoxLayout)
from PyQt5.QtGui import QFont,QCursor,QFontMetrics,QTransform,QPainter,QPen,QPixmap,QColor
from PyQt5.QtPrintSupport import QPrinter,QPrintDialog

MAC = True
try:
    from PyQt5.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False
  
PageSize = (595, 842) # A4 in points
# PageSize = (612, 792) # US Letter in points
PointSize = 10

MagicNumber = 0x70616765
FileVersion = 1

Dirty = False


class TextItemDlg(QDialog):

    def __init__(self, item=None, position=None, scene=None, parent=None):
        super(TextItemDlg, self).__init__(parent)

        self.item = item
        self.position = position
        self.scene = scene

        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setTabChangesFocus(True)
        editorLabel = QLabel("&Text:")
        editorLabel.setBuddy(self.editor)
        self.fontComboBox = QFontComboBox()
        self.fontComboBox.setCurrentFont(QFont("Times", PointSize))
        fontLabel = QLabel("&Font:")
        fontLabel.setBuddy(self.fontComboBox)
        self.fontSpinBox = QSpinBox()
        self.fontSpinBox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.fontSpinBox.setRange(6, 280)
        self.fontSpinBox.setValue(PointSize)
        fontSizeLabel = QLabel("&Size:")
        fontSizeLabel.setBuddy(self.fontSpinBox)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                          QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        if self.item is not None:
            self.editor.setPlainText(self.item.toPlainText())
            self.fontComboBox.setCurrentFont(self.item.font())
            self.fontSpinBox.setValue(self.item.font().pointSize())

        layout = QGridLayout()
        layout.addWidget(editorLabel, 0, 0)
        layout.addWidget(self.editor, 1, 0, 1, 6)
        layout.addWidget(fontLabel, 2, 0)
        layout.addWidget(self.fontComboBox, 2, 1, 1, 2)
        layout.addWidget(fontSizeLabel, 2, 3)
        layout.addWidget(self.fontSpinBox, 2, 4, 1, 2)
        layout.addWidget(self.buttonBox, 3, 0, 1, 6)
        self.setLayout(layout)


        self.fontComboBox.currentFontChanged.connect(self.updateUi)
        self.fontSpinBox.valueChanged.connect(self.updateUi)
        self.editor.textChanged.connect(self.updateUi)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Page Designer - {0} Text Item".format(
                "Add" if self.item is None else "Edit"))
        self.updateUi()


    def updateUi(self):
        font = self.fontComboBox.currentFont()
        font.setPointSize(self.fontSpinBox.value())
        # void QFont::setPointSize(int pointSize)
        self.editor.document().setDefaultFont(font) 
        # .document(): This property holds the underlying document of the text editor.
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
                bool(self.editor.toPlainText()))


    def accept(self):
        if self.item is None:
            self.item = TextItem("", self.position, self.scene)
        font = self.fontComboBox.currentFont()
        font.setPointSize(self.fontSpinBox.value())
        self.item.setFont(font)
        self.item.setPlainText(self.editor.toPlainText())   
        self.item.update()
        # Schedules a redraw of the area covered by rect in this item. 
        # You can call this function whenever your item needs to be redrawn, such as if it changes appearance or size.
        global Dirty
        Dirty = True
        QDialog.accept(self)


class TextItem(QGraphicsTextItem):
    def __init__(self, text, position, scene,
                 font=QFont("Times", PointSize), matrix=QTransform()):
        super(TextItem, self).__init__(text)
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable)
        self.setFont(font)
        self.setPos(position)
        self.setTransform(matrix)
        scene.clearSelection()
        scene.addItem(self)
        self.setSelected(True)
        global Dirty
        Dirty = True


    def parentWidget(self):
        return self.scene().views()[0]


    def itemChange(self, change, variant):
        if change != QGraphicsItem.ItemSelectedChange:
            global Dirty
            Dirty = True
        return QGraphicsTextItem.itemChange(self, change, variant)


    def mouseDoubleClickEvent(self, event):
        dialog = TextItemDlg(self, self.parentWidget()) # parentWidget()是做这个用的，因为双击后调用不能用在自己作为父容器
        dialog.exec_()



class GraphicsPixmapItem(QGraphicsPixmapItem):        #add by yangrongdong
    def __init__(self,pixmap):
        super(GraphicsPixmapItem, self).__init__(pixmap)


class BoxItem(QGraphicsItem):

    def __init__(self, position, scene, style=Qt.SolidLine,
                 rect=None, matrix=QTransform()):
        # 需要的参数为 矩形大小、样式、变换、位置和放置对象
        # QTransform() :Constructs an identity matrix. 可接受一个矩阵，TF对象或者一些点
        super(BoxItem, self).__init__()
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable|
                      QGraphicsItem.ItemIsFocusable) # 可选择、可移动、可集中焦点
        if rect is None:
            rect = QRectF(-10 * PointSize, -PointSize, 20 * PointSize,
                          2 * PointSize) # 提供一个默认的矩形
        self.rect = rect
        self.style = style
        self.setPos(position)
        self.setTransform(matrix)
        scene.clearSelection() # [slot] void QGraphicsScene::clearSelection() Clears the current selection.
        scene.addItem(self) # 添加项目并且选中并且高亮（添加的主题是scene）
        self.setSelected(True) #If selected is true and this item is selectable, this item is selected; otherwise, it is unselected.
        self.setFocus() #Gives keyboard input focus to this item. void QGraphicsItem::setFocus(Qt::FocusReason focusReason = Qt::OtherFocusReason)
        # The focusReason argument will be passed into any focus event generated by this function;
        global Dirty
        Dirty = True # 设置Dirty为Ture，标记更改


    def parentWidget(self):
        return self.scene().views()[0]
        # Returns a list of all the views that display this scene.
        # QView.scene() Returns a pointer to the scene that is currently visualized in the view.


    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)
        # 返回和提供一个外边框值，如果没有给予参数传递过来，那么这会生成一个默认的扁平框


    def paint(self, painter, option, widget):
        pen = QPen(self.style)
        pen.setColor(Qt.black)
        pen.setWidth(1)
        if option.state & QStyle.State_Selected:
            pen.setColor(Qt.blue)
        painter.setPen(pen)
        painter.drawRect(self.rect)


    def itemChange(self, change, variant):
        if change != QGraphicsItem.ItemSelectedChange:
            global Dirty
            Dirty = True
        return QGraphicsItem.itemChange(self, change, variant)


    def contextMenuEvent(self, event):
        wrapped = []
        menu = QMenu(self.parentWidget())
        for text, param in (
                ("&Solid", Qt.SolidLine),
                ("&Dashed", Qt.DashLine),
                ("D&otted", Qt.DotLine),
                ("D&ashDotted", Qt.DashDotLine),
                ("DashDo&tDotted", Qt.DashDotDotLine)):
            wrapper = functools.partial(self.setStyle, param) # 不像直接用setPenStyle() 因为还要处理更新显示的问题和设置dirty问题，做成参数传递进去
            # 此处self.setStyle不需要加括号，第二个为参数，直接传递就行。
            wrapped.append(wrapper)
            menu.addAction(text, wrapper)
        menu.exec_(event.screenPos()) # screenPos\GlobalPos全局的位置\windowPos 可能因为窗口移动而改变
        #  3 QPointQMouseEvent::pos();//返回相对这个widget的位置
        #  4 QPointQWidget::pos();//这个属性获得的是当前目前控件在父窗口中的位置
        #  QMouseEvent::screenPos()和QPoint QMouseEvent::globalPos() 值相同，但是类型更高精度的QPointF，其实某些组件也有globalPosF返回QPoint


    def setStyle(self, style):
        self.style = style
        self.update()
        global Dirty
        Dirty = True


    def keyPressEvent(self, event):
        # ?????????????????????????/为什么没效果?????????????????????????????
        factor = PointSize / 4 # 移动精度
        changed = False
        if event.modifiers() & Qt.ShiftModifier:
            if event.key() == Qt.Key_Left:
                self.rect.setRight(self.rect.right() - factor)
                # void QRect::setRight(int x) Sets the right edge of the rectangle to the given x coordinate
                # May change the width, but will never change the left edge of the rectangle.
                # moveRight() Moves the rectangle horizontally, leaving the rectangle's right edge at the given x coordinate. The rectangle's size is unchanged.
                changed = True
            elif event.key() == Qt.Key_Right:
                self.rect.setRight(self.rect.right() + factor)
                changed = True
            elif event.key() == Qt.Key_Up:
                self.rect.setBottom(self.rect.bottom() - factor)
                changed = True
            elif event.key() == Qt.Key_Down:
                self.rect.setBottom(self.rect.bottom() + factor)
                changed = True
        if changed:
            self.update()
            global Dirty
            Dirty = True
        else:
            QGraphicsItem.keyPressEvent(self, event)


class GraphicsView(QGraphicsView):

    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        # A rubber band will appear. Dragging the mouse will set the rubber band geometry, 
        # and all items covered by the rubber band are selected. This mode is disabled for non-interactive views.
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)


    def wheelEvent(self, event):
        #factor = 1.41 ** (-event.delta() / 240.0) 
        factor = event.angleDelta().y()/120.0
        if event.angleDelta().y()/120.0 > 0:
            factor=2
        else:
            factor=0.5
        self.scale(factor, factor)
        # Scales the current view transformation by (sx, sy).


class MainForm(QDialog):

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        self.filename = ""
        self.copiedItem = QByteArray()
        self.pasteOffset = 5
        self.prevPoint = QPoint()
        self.addOffset = 5
        self.borders = []

        self.printer = QPrinter(QPrinter.HighResolution)
        # enum QPrinter::PrinterMode 
        # HighRes是一个高分辨率模式，是PrinterMode组成
        self.printer.setPageSize(QPrinter.A4)
        self.view = GraphicsView()
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, PageSize[0], PageSize[1])
        self.addBorders()
        self.view.setScene(self.scene)
        # 不用写 view.show?
        self.wrapped = [] # Needed to keep wrappers alive
        buttonLayout = QVBoxLayout()
        for text, slot in (
                ("Add &Text", self.addText),
                ("Add &Box", self.addBox),
                ("Add Pi&xmap", self.addPixmap),
                ("&Align", None),
                ("&Copy", self.copy),
                ("C&ut", self.cut),
                ("&Paste", self.paste),
                ("&Delete...", self.delete),
                ("&Rotate", self.rotate),
                ("Pri&nt...", self.print_),
                ("&Open...", self.open),
                ("&Save", self.save),
                ("&Quit", self.accept)):
            button = QPushButton(text)
            if not MAC:
                button.setFocusPolicy(Qt.NoFocus)
            if slot is not None:
                button.clicked.connect(slot)
            if text == "&Align":
                menu = QMenu(self)
                for text, arg in (
                        ("Align &Left", Qt.AlignLeft),
                        ("Align &Right", Qt.AlignRight),
                        ("Align &Top", Qt.AlignTop),
                        ("Align &Bottom", Qt.AlignBottom)):
                    wrapper = functools.partial(self.setAlignment, arg)
                    # ?????
                    self.wrapped.append(wrapper)
                    menu.addAction(text, wrapper)
                button.setMenu(menu)
            if text == "Pri&nt...":
                buttonLayout.addStretch(5)
            if text == "&Quit":
                buttonLayout.addStretch(1)
            buttonLayout.addWidget(button)
        buttonLayout.addStretch()

        layout = QHBoxLayout()
        layout.addWidget(self.view, 1) 
        # QBoxLayout::addWidget(QWidget *widget, int stretch = 0, Qt::Alignment alignment = Qt::Alignment())
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        fm = QFontMetrics(self.font())
        self.resize(self.scene.width() + fm.width(" Delete... ") + 50,
                    self.scene.height() + 50)
        self.setWindowTitle("Page Designer 页面设计器")


    def addBorders(self):
        '''添加出血框和打印边界框，对scene进行操作同时添加到self.borders这一列表中'''
        self.borders = []
        rect = QRectF(0, 0, PageSize[0], PageSize[1])
        self.borders.append(self.scene.addRect(rect, Qt.black)) # addRect px,py,x,y,QPen,QBrush or QRectF,QPen,QBrush
        # scene.addRect(): Return QGraphicsRectItem；Inherits: QGraphicsItem

        margin = 5.25 * PointSize
        self.borders.append(self.scene.addRect(
                rect.adjusted(margin, margin, -margin, -margin),
                Qt.red))


    def removeBorders(self):
        '''从列表删除边框，从scene删除边框'''
        while self.borders:
            item = self.borders.pop()
            self.scene.removeItem(item) #Removes the item item and all its children from the scene. 接受参数为QGraphicsItem
            del item


    def reject(self):
        self.accept()


    def accept(self):
        self.offerSave()
        QDialog.accept(self) # 完成提示保存之后传递给QDialog的accept命令，之前几章好像讲过为什么要直接调用QDialog这个父类，这里的MWindow是QDialog


    def offerSave(self):
        '''根据Dirty判断是否更改，如果更改则弹出保存对话框，调用save()函数进行保存。'''
        if (Dirty and QMessageBox.question(self,
                            "Page Designer - Unsaved Changes",
                            "Save unsaved changes?",
                            QMessageBox.Yes|QMessageBox.No) == 
           QMessageBox.Yes):
            self.save()


    def position(self):
        point = self.mapFromGlobal(QCursor.pos()) # mFG接受一个QPoint参数，包含两个元素的元组 此函数转换QPoint到map，返回依旧是QPoint
        # Translates the global screen coordinate pos to widget coordinates.
        if not self.view.geometry().contains(point): #??????????????????????????????????????????????
            coord = random.randint(36, 144)
            point = QPoint(coord, coord)
        else:
            if point == self.prevPoint:
                point += QPoint(self.addOffset, self.addOffset)
                self.addOffset += 5
            else:
                self.addOffset = 5
                self.prevPoint = point
        return self.view.mapToScene(point) # 将Widght的点左边转换成为Scene坐标，调用对象是QGView


    def addText(self):
        dialog = TextItemDlg(position=self.position(),
                             scene=self.scene, parent=self)
        dialog.exec_()


    def addBox(self):
        BoxItem(self.position(), self.scene)


    def addPixmap(self):
        path = (QFileInfo(self.filename).path()
            if self.filename else ".") # 获取filename定义的正确地址，或者返回此程序根目录
        fname,filetype = QFileDialog.getOpenFileName(self,
                "Page Designer - Add Pixmap", path,
                "Pixmap Files (*.bmp *.jpg *.png *.xpm)")
        if not fname:
            return
        self.createPixmapItem(QPixmap(fname), self.position()) # 插入时候要将地址传递给QPixmap生成对象，并且还需要位置参数


    def createPixmapItem(self, pixmap, position, matrix=QTransform()): # 传递参数为：文件、位置和变换
        item = GraphicsPixmapItem(pixmap) # 第一步，将QPixmap转换成为GPItem
        item.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable) # 设置一些属性
        item.setPos(position) # 设置位置
        item.setTransform(matrix) # 将变换参数应用到GPItem之中
        self.scene.clearSelection() # 选择清空
        self.scene.addItem(item) # 添加项目
        item.setSelected(True) # 并且选中
        global Dirty
        Dirty = True # 全局变量Dirty设置为True
        return item # 为什么需要返回这个？？？


    def selectedItem(self): # 默认的scene选择的是一个列表，如果只有一个则返回index=0的item,如果多选则不返回任何一个
        items = self.scene.selectedItems()
        if len(items) == 1:
            return items[0]
        return None


    def copy(self):
        item = self.selectedItem()
        if item is None:
            return
        self.copiedItem.clear()
        self.pasteOffset = 5
        stream = QDataStream(self.copiedItem, QIODevice.WriteOnly)
        self.writeItemToStream(stream, item) # 写入到流


    def cut(self):
        item = self.selectedItem()
        if item is None:
            return
        self.copy()
        self.scene.removeItem(item)
        del item


    def paste(self):
        if self.copiedItem.isEmpty():
            return
        stream = QDataStream(self.copiedItem, QIODevice.ReadOnly)
        self.readItemFromStream(stream, self.pasteOffset) # 从数据流中读入信息，并且输出到self.pasteOffset中
        self.pasteOffset += 5


    def setAlignment(self, alignment):
        # Items are returned in arbitrary order
        items = self.scene.selectedItems()
        if len(items) <= 1:
            return
        # Gather coordinate data
        leftXs, rightXs, topYs, bottomYs = [], [], [], []
        for item in items:
            rect = item.sceneBoundingRect()
            # Returns the bounding rect of this item in scene coordinates : Return QRectF
            leftXs.append(rect.x())
            rightXs.append(rect.x() + rect.width())
            topYs.append(rect.y())
            bottomYs.append(rect.y() + rect.height())
        # Perform alignment
        if alignment == Qt.AlignLeft:
            xAlignment = min(leftXs)
            for i, item in enumerate(items):
                item.moveBy(xAlignment - leftXs[i], 0)
                # void QGraphicsItem::moveBy(qreal dx, qreal dy)
                # Moves the item by dx points horizontally, and dy point vertically.
        elif alignment == Qt.AlignRight:
            xAlignment = max(rightXs)
            for i, item in enumerate(items):
                item.moveBy(xAlignment - rightXs[i], 0)
        elif alignment == Qt.AlignTop:
            yAlignment = min(topYs)
            for i, item in enumerate(items):
                item.moveBy(0, yAlignment - topYs[i])
        elif alignment == Qt.AlignBottom:
            yAlignment = max(bottomYs)
            for i, item in enumerate(items):
                item.moveBy(0, yAlignment - bottomYs[i])
        global Dirty
        Dirty = True


    def rotate(self):
        for item in self.scene.selectedItems():
            item.setRotation(item.rotation()+30)

    def delete(self): # 从基本scene属性中选取选择的多个，弹出对话框，如果允许，则迭代进行删除，并且设置Dirty为True
        items = self.scene.selectedItems()
        if (len(items) and QMessageBox.question(self,
                "Page Designer - Delete",
                "Delete {0} item{1}?".format(len(items),
                "s" if len(items) != 1 else ""),
                QMessageBox.Yes|QMessageBox.No) ==
                QMessageBox.Yes):
            while items:
                item = items.pop()
                self.scene.removeItem(item)
                del item
            global Dirty
            Dirty = True


    def print_(self):
        # dialog = QPrintDialog(self.printer) # 在此已经设置好了self.printer 也就是QPrinter对象，QPDlg直接传递回了Printer对象，之后重新由
        # # printer对象声称心的QPrinter就可以继续使用在这句话中设置好的参数了。
        # if dialog.exec_():
        painter = QPainter(self.printer)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        self.scene.clearSelection()
        self.removeBorders()
        self.scene.render(painter)
        # [void] Renders the source rect from scene into target, using painter. This function is useful for capturing the contents
        # of the scene onto a paint device, such as a QImage (e.g., to take a screenshot), or for printing with QPrinter. For example:
        self.addBorders()


    def open(self):
        self.offerSave()
        path = (QFileInfo(self.filename).path()
                if self.filename else ".")
        fname,filetype = QFileDialog.getOpenFileName(self,
                "Page Designer - Open", path,
                "cmPage Designer Files (*.cmpd *.pgd *.cmd)")
        if not fname:
            return
        self.filename = fname
        fh = None
        try:
            fh = QFile(self.filename)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError(str(fh.errorString()))
            items = self.scene.items() # 返回所有的QGitem List形式
            while items:
                item = items.pop() # 从列表中删除一个，从scene中删除一个，迭代到全部删除
                self.scene.removeItem(item)
                del item
            self.addBorders()
            stream = QDataStream(fh)
            stream.setVersion(QDataStream.Qt_5_7)
            magic = stream.readInt32()
            if magic != MagicNumber:
                raise IOError("not a valid .cmpd file")
            fileVersion = stream.readInt16()
            if fileVersion != FileVersion:
                raise IOError("unrecognised .cmpd file version")
            while not fh.atEnd():
                self.readItemFromStream(stream)
        except IOError as e:
            QMessageBox.warning(self, "Page Designer -- Open Error",
                    "Failed to open {0}: {1}".format(self.filename, e))
        finally:
            if fh is not None:
                fh.close()
        global Dirty
        Dirty = False


    def save(self):
        if not self.filename:
            path = "."
            fname,filetype = QFileDialog.getSaveFileName(self,
                    "Page Designer - Save As", path,
                    "cmPage Designer Files (*.cmpd *.pgd *.cmd)")
            if not fname:
                return
            self.filename = fname
        fh = None
        try:
            fh = QFile(self.filename)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError(str(fh.errorString()))
            self.scene.clearSelection()
            stream = QDataStream(fh)
            stream.setVersion(QDataStream.Qt_5_7)
            stream.writeInt32(MagicNumber)
            stream.writeInt16(FileVersion)
            for item in self.scene.items():
                self.writeItemToStream(stream, item)
        except IOError as e:
            QMessageBox.warning(self, "Page Designer -- Save Error",
                    "Failed to save {0}: {1}".format(self.filename, e))
        finally:
            if fh is not None:
                fh.close()
        global Dirty
        Dirty = False


    def readItemFromStream(self, stream, offset=0):
        type = ""
        position = QPointF()
        matrix = QTransform()
        rotateangle=0#add by yangrongdong
        type=stream.readQString()
        stream >> position >> matrix
        if offset:
            position += QPointF(offset, offset)
        if type == "Text":
            text = ""
            font = QFont()
            text=stream.readQString()
            stream >> font
            rotateangle=stream.readFloat()
            tx=TextItem(text, position, self.scene, font, matrix)
            tx.setRotation(rotateangle)
        elif type == "Box":
            rect = QRectF()
            stream >> rect
            style = Qt.PenStyle(stream.readInt16())
            rotateangle=stream.readFloat()
            bx=BoxItem(position, self.scene, style, rect, matrix)
            bx.setRotation(rotateangle)
        elif type == "Pixmap":
            pixmap = QPixmap()
            stream >> pixmap
            rotateangle=stream.readFloat()
            px=self.createPixmapItem(pixmap, position, matrix)
            px.setRotation(rotateangle)


    def writeItemToStream(self, stream, item):
        if isinstance(item, TextItem):
            stream.writeQString("Text")
            stream<<item.pos()<< item.transform() 
            stream.writeQString(item.toPlainText())
            stream<< item.font()
            stream.writeFloat(item.rotation())#add by yangrongdong
        elif isinstance(item, GraphicsPixmapItem):
            stream.writeQString("Pixmap")
            stream << item.pos() << item.transform() << item.pixmap()
            stream.writeFloat(item.rotation())#add by yangrongdong
        elif isinstance(item, BoxItem):
            stream.writeQString("Box")
            stream<< item.pos() << item.transform() << item.rect
            stream.writeInt16(item.style)
            stream.writeFloat(item.rotation())#add by yangrongdong



app = QApplication(sys.argv)
form = MainForm()
rect = QApplication.desktop().availableGeometry()
# QA.desktop(): Returns the desktop widget (also called the root window).
# .availableGeometry() QDesktopWidget::availableGeometry(const QWidget *widget) Return QRect
form.resize(int(rect.width() * 0.6), int(rect.height() * 0.9))
form.show()
app.exec_()

```
> 程序：千足虫动画

```python
#!/usr/bin/env python3

import math
import random
import sys
from PyQt5.QtCore import (QTimer, QPointF, QRectF, Qt,QObject)
from PyQt5.QtWidgets import (QApplication, QDialog,
        QGraphicsItem, QGraphicsScene, QGraphicsView, QHBoxLayout,
          QPushButton, QSlider,QVBoxLayout)
from PyQt5.QtGui import (QBrush, QColor,QPainter,QPainterPath,QPolygonF)

SCENESIZE = 500
INTERVAL = 100

class Head(QGraphicsItem):
    # class Head(QGraphicsItem,QObject): PyQt不能多重继承多个选项

    Rect = QRectF(-30, -20, 60, 40)

    def __init__(self, color, angle, position):
        super(Head, self).__init__()
        self.color = color
        self.angle = angle
        self.setPos(position)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        self.timer.start(INTERVAL)

    def boundingRect(self):
        '''制定一个边界矩形作为项目的矩形框'''
        return Head.Rect


    def shape(self):
        '''用来进行碰撞检测，这里对于QPP添加一个范围为Head.Rect的圆来定义Path'''
        # 如果两个头部的矩形交叉，但头部椭圆没有碰撞，则不会检测到碰撞
        path = QPainterPath()
        path.addEllipse(Head.Rect)
        return path


    def paint(self, painter, option, widget=None):
        # option：QStyleOptionGraphicsItem
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(Head.Rect)
        # martix = self.transform()
        # print(self.transform().dx(),self.transform().dy())
        global SCALE
        martix = SCALE
        # print('比例:',option.levelOfDetailFromTransform(self.transform()))
        # 图形项使用其各自所在的逻辑坐标系，所有外部变换都会自动处理
        if option.levelOfDetailFromTransform(martix) > 0.5: # Outer eyes
            # Returns the level of detail from the worldTransform.
            # If zoomed out 1:2, the level of detail will be 0.5, and if zoomed in 2:1, its value is 2
            painter.setBrush(QBrush(Qt.yellow))
            painter.drawEllipse(-12, -19, 8, 8)
            painter.drawEllipse(-12, 11, 8, 8)
            if option.levelOfDetailFromTransform(martix)> 0.8: # Inner eyes
                painter.setBrush(QBrush(Qt.darkBlue))
                painter.drawEllipse(-12, -19, 4, 4)
                painter.drawEllipse(-12, 11, 4, 4)
                if option.levelOfDetailFromTransform(martix) > 0.9: # Nostrils
                    painter.setBrush(QBrush(Qt.white))
                    painter.drawEllipse(-27, -5, 2, 2)
                    painter.drawEllipse(-27, 3, 2, 2)


    def timeout(self):
        if not Running:
            # print("暂停头部生成")
            return
        angle = self.angle
        while True:
            angle +=  random.randint(-9,9)
            offset = random.randint(3,15)
            x = self.x() + (offset * math.sin(math.radians(angle)))
            y = self.y() + (offset * math.cos(math.radians(angle)))
            if 0 <= x <= SCENESIZE and 0 <= y <= SCENESIZE:
                # print("CurrentSize[%s,%s]"%(x,y))
                break
        self.angle = angle  
        self.setRotation(random.randint(-5,5))
        self.setPos(QPointF(x,y))
        # self.color.setRed(min(255,self.color.red()+1))
        # self.update()
        if self.scene():
            # print("Change Color NOW!")
            for item in self.scene().collidingItems(self):
                # 在本例子中，要求所有项都具有碰撞检测功能
                # Returns a list of all items that collide with item. 
                # Collisions are determined by calling QGraphicsItem::collidesWithItem()
                if isinstance(item,Head):
                    self.color.setRed(min(255,self.color.red()+10))
                else:
                    item.color.setBlue(min(255,self.color.blue()+20))

class Segment(QGraphicsItem):
    '''
    # 新建Path
    QPath 可以通过从empty path或者另一个path新建，
    Once created, lines and curves can be added to the path using the lineTo(), arcTo(), cubicTo() and quadTo() functions.
    currentPosition() of the QPainterPath object is always the end position of the last subpath that was added (or the initial start point)
    # 开始新的subpath的两种方法：
    moveTo()： function implicitly starts a new subpath, and closes the previous one.
    closeSubpath()：Another way of starting a new subpath is to call the closeSubpath() function which closes the current path by adding a line from the currentPosition()
    back to the path's start position. Note that the new path will have (0, 0) as its initial currentPosition().
    # 一些便捷的方法：
    addEllipse(), addPath(), addRect(), addRegion() and addText(). The addPolygon() function adds an unclosed subpath. 
    In fact, these functions are all collections of moveTo(), lineTo() and cubicTo() operations.
    # 连接到上一条Path：
    In addition, a path can be added to the current path using the connectPath() function. 
    But note that this function will connect the last element of the current path to the first element of given one by adding a line.
    
    '''
    def __init__(self, color, offset, parent):
        # offset接收一个偏移量，这是身子相对于头的偏移量
        super(Segment, self).__init__(parent)
        self.color = color
        self.rect = QRectF(offset, -20, 30, 40)
        self.path = QPainterPath()
        self.path.addEllipse(self.rect)
        x = offset + 15
        y = -20
        self.path.addPolygon(QPolygonF([QPointF(x, y),
                QPointF(x - 5, y - 12), QPointF(x - 5, y)]))
        self.path.closeSubpath()
        # Closes the current subpath by drawing a line to the beginning of the subpath, 
        # automatically starting a new path. 
        # The current point of the new path is (0, 0).
        y = 20
        self.path.addPolygon(QPolygonF([QPointF(x, y),
                QPointF(x - 5, y + 12), QPointF(x - 5, y)]))
        self.path.closeSubpath()
        self.change = 1
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        self.timer.start(INTERVAL)

    def boundingRect(self):
        return self.path.boundingRect()


    def shape(self):
        return self.path

    def paint(self, painter, option, widget=None):
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.color))
        global SCALE
        martix = SCALE
        if option.levelOfDetailFromTransform(martix) < 0.9:
            painter.drawEllipse(self.rect)
        else:
            painter.drawPath(self.path)

    def timeout(self):
        if not Running:
            # print("暂停身体生成")
            return 
        matrix = self.transform()
        matrix.reset()
        self.setTransform(matrix)
        self.angle += self.change
        if self.angle > 3:
            self.change = -1
            self.angle -= 1
            # print("浪过去")
        elif self.angle < -3:
            self.change = 1
            self.angle += 1
            # print("浪回来")
        self.setRotation(self.angle)


class MainForm(QDialog):

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        # self.running = False
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, SCENESIZE, SCENESIZE)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.view = QGraphicsView()
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setScene(self.scene)
        self.view.setFocusPolicy(Qt.NoFocus)
        zoomSlider = QSlider(Qt.Horizontal)
        zoomSlider.setRange(5, 200)
        zoomSlider.setValue(100)
        self.pauseButton = QPushButton("Pa&use")
        quitButton = QPushButton("&Quit")
        quitButton.setFocusPolicy(Qt.NoFocus)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.pauseButton)
        bottomLayout.addWidget(zoomSlider)
        bottomLayout.addWidget(quitButton)
        layout.addLayout(bottomLayout)
        self.setLayout(layout)

        self.pauseButton.clicked.connect(self.pauseOrResume)
        zoomSlider.valueChanged[int].connect(self.zoom)
        quitButton.clicked.connect(self.accept)

        self.populate()
        self.startTimer(INTERVAL)
        self.setWindowTitle("Multipedes")

        global SCALE
        SCALE = self.view.transform() 

    def zoom(self, value):
        factor = value / 100.0
        matrix=self.view.transform() 
        matrix.reset()
        matrix.scale(factor, factor)
        self.view.setTransform(matrix) #在Qt5中已经进行了更改
        global SCALE
        SCALE = self.view.transform() 


    def pauseOrResume(self):
        global Running
        Running = not Running
        # print(Running)
        self.pauseButton.setText("Pa&use" if Running else "Res&ume")


    def populate(self):
        red, green, blue = 0, 150, 0
        for i in range(random.randint(6, 10)):
            angle = random.randint(0, 360)
            offset = random.randint(0, SCENESIZE // 2) # 返回整数
            half = SCENESIZE / 2
            x = half + (offset * math.sin(math.radians(angle)))
            y = half + (offset * math.cos(math.radians(angle)))
            color = QColor(red, green, blue)
            head = Head(color, angle, QPointF(x, y))
            color = QColor(red, green + random.randint(10, 60), blue)
            offset = 25
            segment = Segment(color, offset, head) # 这是第一个关节，其父为Head
            # 之后所得segment以第一节关节作为父的话，其坐标按照第一节关节为0来计算
            for j in range(random.randint(2, 7)):
                offset += 25
                segment = Segment(color, offset, segment) #所有的子关节的父为第一个关节，方便删除
            head.setRotation(random.randint(0, 360))
            self.scene.addItem(head)
        global Running
        Running = True


    def timerEvent(self, event):
        if not Running:
            # print("暂停主程序")
            return
        dead = set()
        items = self.scene.items()
        if len(items) == 0:
            self.populate()
            return
        heads = set()
        for item in items:
            if isinstance(item, Head):
                heads.add(item) # 删除了头就删除了第一节身子，而删除了第一节身子也就删除了所有身体其余构成部分
                # if item.color.red() == 255 and random.random() > 0.75:
                if item.color.red() == 255:
                    dead.add(item)
        if len(heads) == 1:
            dead = heads
        del heads
        while dead:
            item = dead.pop()
            self.scene.removeItem(item)
            del item
        # self.scene.advance() # 信号：告诉scene中的item可以准备移动并且可以移动了。
        # 没有采用这种方式，发现效率不行，改用了在每个Item中设置定时器的方式，速度不错。


app = QApplication(sys.argv)
form = MainForm()
rect = QApplication.desktop().availableGeometry()
form.resize(int(rect.width() * 0.75), int(rect.height() * 0.9))
form.show()
app.exec_()

```