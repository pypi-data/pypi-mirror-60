# -*- coding: utf-8 -*-
"""Plot view module.

contains PSPlotView, a subclass of QMainWindow
"""

import gc
import sys

import matplotlib.backends.backend_qt5agg as mplAgg
import matplotlib.pyplot as plt
from matplotlib import get_backend
from matplotlib.figure import Figure
from puzzlestream.backend.signal import PSSignal
from puzzlestream.backend.status import PSStatus
from puzzlestream.backend.stream import PSStream
from puzzlestream.ui.manager import PSManager
from puzzlestream.ui.plot import KeyPlot
from puzzlestream.ui.puzzleitem import PSPuzzleItem
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

translate = QCoreApplication.translate


class PSPlotView(QtWidgets.QMainWindow):

    def __init__(self, manager: PSManager, puzzleItem: PSPuzzleItem,
                 parent: QObject = None, numberOfViewers: int = 1):
        super().__init__(parent)
        self.__viewerWindows = []
        self.__manager = manager
        self.__config = manager.config
        self.__puzzleItem = puzzleItem
        self.__autotile = self.__config["autotilePlots"]
        self.__createGUI(numberOfViewers)
        self.__closedSignal = PSSignal()
        self.retranslateUi()

    @property
    def closedSignal(self) -> PSSignal:
        return self.__closedSignal

    def retranslateUi(self):
        if self.__puzzleItem is None:
            self.setWindowTitle(translate("PlotView", "Plot view") + " - " +
                                translate("PlotView", "complete stream"))
        else:
            self.setWindowTitle(translate("PlotView", "Plot view") + " - " +
                                str(self.__puzzleItem))

        self.__addAction.setText(translate("PlotView", "Add viewer"))
        self.__tileAction.setText(translate("PlotView", "Tile windows"))
        self.__tileChkBox.setText(translate("PlotView", "auto tile"))

    def changeEvent(self, event: QEvent):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        return super().changeEvent(event)

    def statusUpdate(self, item):
        if item.status is PSStatus.FINISHED:
            if self.__puzzleItem is None or item == self.__puzzleItem:
                self.__update(item)

    def __update(self, sourceItem=None):
        for v in self.__viewerWindows:
            v.update(sourceItem)

    def updatePuzzleItem(self, puzzleItem):
        if puzzleItem.status is PSStatus.FINISHED:
            for v in self.__viewerWindows:
                v.updatePuzzleItem(puzzleItem)

    def __createGUI(self, numberOfViewers=1):
        self.mdi = QtWidgets.QMdiArea()
        self.setCentralWidget(self.mdi)

        self.toolbar = QtWidgets.QToolBar()
        self.__addAction = self.toolbar.addAction("Add viewer")
        self.__tileAction = self.toolbar.addAction("Tile windows")

        self.__tileChkBox = QtWidgets.QCheckBox("auto tile")
        self.__tileChkBox.setChecked(self.__config["autotilePlots"])
        self.__tileChkBox.stateChanged.connect(self.__autotileChanged)
        self.toolbar.addWidget(self.__tileChkBox)

        self.__addAction.triggered.connect(self.__addViewer)
        self.__tileAction.triggered.connect(self.mdi.tileSubWindows)
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        for _ in range(numberOfViewers):
            self.__addViewer()

    def __addViewer(self):
        viewer = PSSinglePlotView(self.__manager, self.__puzzleItem, self)
        viewer.closedSignal.connect(self.__viewerClosed)

        self.__viewerWindows.append(viewer)
        self.mdi.addSubWindow(viewer)
        viewer.show()

        if self.__autotile:
            self.mdi.tileSubWindows()

    def __autotileChanged(self, state):
        self.__autotile = state == 2

    def updatePlots(self):
        for viewer in self.__viewerWindows:
            viewer.updatePlots()

    def __viewerClosed(self, viewer):
        i = self.__viewerWindows.index(viewer)
        del self.__viewerWindows[i]
        gc.collect()

    def closeEvent(self, event):
        self.__close()
        super().closeEvent(event)

    def close(self):
        self.__close()
        super().close()

    def __close(self):
        self.__config["autotilePlots"] = self.__autotile
        for v in self.__viewerWindows:
            v.closePlot()
        self.setParent(None)
        gc.collect()
        self.closedSignal.emit(self)


class PSSinglePlotView(QtWidgets.QMdiSubWindow):

    def __init__(self, manager, puzzleItem=None, parent=None):
        super().__init__(parent)
        self.__manager = manager
        self.__stream = manager.stream
        self.__modules = manager.scene.modules
        self.__puzzleItem = puzzleItem

        if puzzleItem is None:
            self.__data = self.__stream
        else:
            self.__data = puzzleItem.streamSection.data

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.__widget = QtWidgets.QWidget()
        self.setWidget(self.__widget)
        self.__parent = parent
        self.box = QtWidgets.QGridLayout()
        self.__widget.setLayout(self.box)
        self.__plots = []

        self.switchLayout = QtWidgets.QHBoxLayout()
        self.previousBtn = QtWidgets.QPushButton()
        self.nextBtn = QtWidgets.QPushButton()
        self.combo = QtWidgets.QComboBox()
        self.combo.currentIndexChanged.connect(self.__selectionChanged)
        self.switchLayout.addWidget(self.previousBtn)
        self.switchLayout.addWidget(self.nextBtn)
        self.switchLayout.addWidget(self.combo)
        self.switchLayout.setContentsMargins(0, 0, 0, 0)
        self.box.addLayout(self.switchLayout, 0, 0)

        self.previousBtn.clicked.connect(
            lambda: self.combo.setCurrentIndex(self.combo.currentIndex() - 1))
        self.nextBtn.clicked.connect(
            lambda: self.combo.setCurrentIndex(self.combo.currentIndex() + 1))
        self.previousBtn.setStyleSheet(
            "QPushButton { min-width: 5em; max-width: 5em; }")
        self.nextBtn.setStyleSheet(
            "QPushButton { min-width: 5em; max-width: 5em; }")
        self.previousBtn.setEnabled(False)
        self.nextBtn.setEnabled(False)

        self.__plotWidget = None
        self.__closedSignal = PSSignal()

        self.updatePlots()
        self.retranslateUi()

    @property
    def closedSignal(self):
        return self.__closedSignal

    def retranslateUi(self):
        self.previousBtn.setText(translate("SinglePlotView", "previous"))
        self.nextBtn.setText(translate("SinglePlotView", "next"))

    def changeEvent(self, event: QEvent):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        return super().changeEvent(event)

    def closeEvent(self, event: QEvent):
        self.closePlot()
        return super().closeEvent(event)

    def __translateKeyToUser(self, key: str) -> str:
        if isinstance(self.__data, PSStream):
            ID = key.split("-")[0]
            if not int(ID) in self.__modules:
                return
            keyn = key[len(ID) + 1:]
            return self.__modules[int(ID)].name + ": " + keyn
        return key

    def __translateKeyToInternal(self, key) -> str:
        if key in self.__retranslatedKeys:
            return self.__retranslatedKeys[key]

    def updatePlots(self):
        plotList = []
        self.__retranslatedKeys = {}

        for key in self.__data:
            try:
                if isinstance(self.__data[key], Figure):
                    transKey = self.__translateKeyToUser(key)

                    if transKey is not None:
                        self.__retranslatedKeys[transKey] = key
                        plotList.append(key)
            except Exception as e:
                print(e)

        self.__plots = sorted(plotList)
        self.combo.clear()
        for key in self.__plots:
            self.combo.addItem(self.__translateKeyToUser(key))

        if self.__puzzleItem is not None:
            self.__data.cleanRam()

    def update(self, sourceItem: PSPuzzleItem = None):
        if self.__puzzleItem is not None or sourceItem is None:
            needsUpdate = True
        else:
            needsUpdate = False
            for key in self.__data:
                if (int(key.split("-")[0]) == sourceItem.id and
                        isinstance(self.__data[key], Figure)):
                    needsUpdate = True
                    break

        if needsUpdate:
            if not isinstance(self.__data, PSStream):
                self.__data.reload()
            i = self.combo.currentIndex()
            self.updatePlots()
            if i < 0 and len(self.__plots) > 0:
                i = 0
            self.combo.setCurrentIndex(i)
            self.__selectionChanged()

    def updatePuzzleItem(self, puzzleItem: PSPuzzleItem):
        self.__puzzleItem = puzzleItem
        self.__data = puzzleItem.streamSection.data
        self.update(puzzleItem)

    def __setFigure(self, index: int = 0):
        self.__closeCurrentPlotWidget()

        if len(self.__plots) > 0 and self.__plotWidget is None:
            self.__plotWidget = KeyPlot(self.__data, self.__plots[index], self)
            self.box.addWidget(self.__plotWidget, 1, 0)

    def __selectionChanged(self):
        self.__setFigure(self.combo.currentIndex())
        self.previousBtn.setEnabled(
            len(self.__plots) > 0 and self.combo.currentIndex() != 0)
        self.nextBtn.setEnabled(
            len(self.__plots) > 0 and
            self.combo.currentIndex() < len(self.__plots) - 1
        )

    def __closeCurrentPlotWidget(self):
        if self.__plotWidget is not None:
            self.__plotWidget.clear()
            plt.close("all")
            self.box.removeWidget(self.__plotWidget)
            self.__plotWidget.setParent(None)
            self.__plotWidget.hide()
            del self.__plotWidget
            self.__plotWidget = None

        if self.__puzzleItem is not None:
            self.__data.cleanRam()

        gc.collect()

    def closePlot(self):
        self.__closeCurrentPlotWidget()
        self.setParent(None)
        self.__widget.setParent(None)
        self.closedSignal.emit(self)
        gc.collect()
