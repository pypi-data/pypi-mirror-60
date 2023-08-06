# -*- coding: utf-8 -*-
"""Traceback view module.

contains PSTracebackView, a subclass of QMainWindow
"""

from puzzlestream.backend.stream import PSStream
from puzzlestream.backend.tracebackmodel import PSTracebackModel
from PyQt5 import QtCore, QtWidgets

translate = QtCore.QCoreApplication.translate


class PSTracebackView(QtWidgets.QMainWindow):

    def __init__(self, key: str, userKey: str, stream: PSStream, modules: list,
                 parent: QtCore.QObject = None):
        super().__init__(parent)
        self.__widget = QtWidgets.QWidget()
        self.__layout = QtWidgets.QGridLayout()

        model = PSTracebackModel(key, stream, modules)

        self.__listView = QtWidgets.QListView(self.__widget)
        self.__listView.setModel(model)
        self.__listView.setSelectionMode(
            QtWidgets.QListView.NoSelection)
        self.__layout.addWidget(self.__listView)
        self.__widget.setLayout(self.__layout)
        self.setCentralWidget(self.__widget)

        self.setWindowTitle(
            translate("Traceback", "Traceback") + " - " + userKey)
        self.resize(400, 800)
        self.show()
