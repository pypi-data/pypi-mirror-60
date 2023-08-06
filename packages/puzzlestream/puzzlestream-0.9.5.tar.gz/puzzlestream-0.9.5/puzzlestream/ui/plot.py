import sys

import matplotlib
import matplotlib.backends.backend_qt5agg as mplAgg
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtGui, QtWidgets


class Plot(QtWidgets.QWidget):

    def __init__(self, figure: Figure, parent: QtCore.QObject = None):
        super().__init__(parent=parent)
        self.__fig = figure
        self.__layout = QtWidgets.QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.__layout)
        canvas = mplAgg.FigureCanvasQTAgg(self.__fig)
        self.__layout.addWidget(canvas)
        toolbar = mplAgg.NavigationToolbar2QT(canvas, None)
        toolbar.setStyleSheet("background-color:white; color:black;")
        self.__layout.addWidget(toolbar)

    @property
    def figure(self) -> Figure:
        return self.__fig

    def clear(self):
        self.__fig.clear()

    def draw(self):
        self.__layout.itemAt(0).widget().draw()


class KeyPlot(Plot):

    def __init__(self, data: dict, figureKey: str,
                 parent: QtCore.QObject = None):
        super().__init__(data[figureKey], parent)
