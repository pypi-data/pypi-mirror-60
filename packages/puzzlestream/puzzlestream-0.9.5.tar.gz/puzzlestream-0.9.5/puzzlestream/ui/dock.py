# -*- coding: utf-8 -*-
"""Docking module.

contains Triangle and PSDock
"""

from time import time
from typing import Callable

from puzzlestream.ui import colors
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Triangle(QtWidgets.QGraphicsPolygonItem):

    def __init__(self, posx: int, posy: int, width: int, height: int,
                 parent: QObject = None):

        super().__init__(parent=parent)

        self.__width = width
        self.__height = height
        self.__triangle = QPolygonF()

        self.__triangle.append(QPointF(posx - self.__width / 2, posy))
        self.__triangle.append(QPointF(posx, posy - self.__height))
        self.__triangle.append(QPointF(posx + self.__width / 2, posy))
        self.__triangle.append(QPointF(posx - self.__width / 2, posy))

        self.setPolygon(self.__triangle)


class PSDock(QtWidgets.QGraphicsItemGroup):

    def __init__(self, width: int, height: int, parent: QObject = None):

        super().__init__(parent=parent)

        self.__initx = 0
        self.__inity = 0
        self.__width = width
        self.__height = height

        self.setFlag(QtWidgets.QGraphicsItemGroup.ItemIsSelectable)

        self.__rectangle = QtWidgets.QGraphicsRectItem(
            self.__initx, self.__inity,
            self.__width, self.__height, parent=self)

        self.__triangle = Triangle(
            self.__initx + self.__width / 2, self.__inity + self.__height,
            self.__width, self.__height, parent=self)

        self.addToGroup(self.__rectangle)
        self.addToGroup(self.__triangle)

        self.setTransformOriginPoint(
            self.__initx + self.__width / 2, self.__inity + self.__height / 2)

        # Preference change stuff
        self.__doubleClickMethod = None
        self.showOnMouseOver = True
        self.setAcceptHoverEvents(True)

    def setColor(self, state: str):
        if state == "input":
            self.__rectBrush = QBrush(QColor(colors.get("standard-blue")))
        if state == "output":
            self.__rectBrush = QBrush(QColor(colors.get("light-blue")))

        self.__triBrush = QBrush(QColor("black"))
        self.__framePen = QPen(QColor("black"))

        self.__rectangle.setBrush(self.__rectBrush)
        self.__rectangle.setPen(self.__framePen)

        self.__triangle.setBrush(self.__triBrush)
        self.__triangle.setPen(self.__framePen)

    def setCenterPos(self, position: QPointF):
        self.setPos(position - QPointF(self.__width / 2, self.__height / 2))

    def setDoubleClickReaction(self, method: Callable):
        self.__doubleClickMethod = method

    def mouseDoubleClickEvent(self, event: QEvent):
        if self.__doubleClickMethod is not None and self.showOnMouseOver:
            self.__doubleClickMethod()
