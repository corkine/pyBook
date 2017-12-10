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