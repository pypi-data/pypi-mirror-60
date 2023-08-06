# -*- coding: utf-8 -*-
"""Output text edit module.

contains PSOutputTextEdit, a subclass of QTextEdit
"""

from PyQt5 import QtCore, QtGui, QtWidgets


class PSOutputTextEdit(QtWidgets.QTextEdit):

    def __init__(self, parent: QtCore.QObject = None):
        super().__init__(parent)
        font = QtGui.QFont("Fira Code", pointSize=9)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)
        scrollbar = self.verticalScrollBar()
        scrollbar.valueChanged.connect(self.__outputScrollbarValueChanged)
        self.textChanged.connect(self.__textChanged)
        self.setReadOnly(True)
        self.activateAutoscroll()

    def __outputScrollbarValueChanged(self, value: float):
        if (value >= self.verticalScrollBar().maximum() -
                0.5 * self.verticalScrollBar().pageStep()):
            self.activateAutoscroll()

    def __textChanged(self):
        if self.__autoscroll:
            self.ensureCursorVisible()

    def eventFilter(self, target: QtCore.QObject, event: QtCore.QEvent):
        if isinstance(event, QtGui.QWheelEvent):
            self.__autoscroll = False
        return QtWidgets.QTextEdit.eventFilter(self, target, event)

    def activateAutoscroll(self):
        self.__autoscroll = True
