# -*- coding: utf-8 -*-
"""Main window module.

contains PSVMainWindow, a subclass of QMainWindow
"""

import matplotlib
import matplotlib.backends.backend_qt5agg as mplAgg
import matplotlib.pyplot as plt
import os
from matplotlib.figure import Figure
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from puzzlestream.backend.figure import PSFigure
import puzzlestream.ui.colors as colors


class Plot(QWidget):

    def __init__(self, figure: Figure, parent: QObject = None):
        super().__init__(parent=parent)
        self.__fig = figure
        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.__layout)
        canvas = mplAgg.FigureCanvasQTAgg(self.__fig)
        self.__layout.addWidget(canvas)
        toolbar = mplAgg.NavigationToolbar2QT(canvas, None)
        toolbar.setStyleSheet("background-color:white; color:black;")
        self.__layout.addWidget(toolbar)

    def clear(self):
        self.__fig.clear()


class PSVMainWindow(QMainWindow):

    def __init__(self, path: str):
        super().__init__()
        self.__path = path

        self.setWindowTitle("Puzzlestream Viewer")
        self.setWindowState(Qt.WindowMaximized)

        fileMenu = self.menuBar().addMenu("File")

        if path is not None:
            self.__figure = PSFigure(path).getHandle()
        else:
            self.__figure = plt.figure()

        main = Plot(self.__figure, self)
        self.setCentralWidget(main)

        # figsizePix = figure.get_size_inches()*figure.dpi
        # self.resize(figsizePix[0], figsizePix[1])
        self.resize(800, 600)
        self.statusBar().showMessage("Maybe we show something here")

        currentDir = os.path.dirname(__file__)
        style = "dark"
        colors.update(os.path.join(currentDir, "style/" + style + ".yml"))
        self.setStyleSheet(
            colors.parseQSS(currentDir + "/style/sheet-em.qss"))
        self.show()

    def __save(self):
        pass
