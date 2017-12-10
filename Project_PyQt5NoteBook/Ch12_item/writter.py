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