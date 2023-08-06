# -*- coding: utf-8 -*-
from matplotlib.figure import Figure
from matplotlib.axis import Axis
import numpy as np
import pandas as pd
from puzzlestream.apps.base import PSApp, PSAppGUIWidget
from puzzlestream.backend.stream import PSStream
from puzzlestream.ui.plot import Plot
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

app = "PSPlotApp"
name = "Plot"
# icon = "icon.png"


class PSPlotApp(PSApp):

    def __init__(self, data: dict, **pars):
        super().__init__(data, **pars)
        self._guiWidgetClass = PSPlotAppGUI

    @property
    def code(self) -> str:
        return super().code

    def setParameters(self, **pars):
        super().setParameters(**pars)


class PSPlotAppGUI(PSAppGUIWidget):

    def __init__(self, app: PSApp, parent=None):
        super().__init__(app, parent=parent)
        self.__app = app
        self.__layout = QGridLayout()
        self.setLayout(self.__layout)

        self.__plotChoices = []
        self.__cmbPlotChoice = QComboBox()
        self.__cmbPlotChoice.currentIndexChanged.connect(
            self.__plotChoiceChanged)
        self.__layout.addWidget(self.__cmbPlotChoice, 0, 0)

        self.__btnAddChoice = QPushButton("+")
        self.__btnRemoveChoice = QPushButton("-")
        self.__btnAddChoice.clicked.connect(lambda x: self.addPlotChoice())
        self.__btnRemoveChoice.clicked.connect(self.removePlotChoice)
        self.__layout.addWidget(self.__btnAddChoice, 0, 1)
        self.__layout.addWidget(self.__btnRemoveChoice, 0, 2)

        self.__lblTitle = QLabel("Title:")
        self.__lblXLabel = QLabel("x label:")
        self.__lblYLabel = QLabel("y label:")
        self.__txtTitle = QLineEdit()
        self.__txtXLabel = QLineEdit()
        self.__txtYLabel = QLineEdit()
        self.__chkLegend = QCheckBox("Legend")
        self.__chkTightLayout = QCheckBox("Tight layout")
        self.__layout.addWidget(self.__lblTitle, 2, 0)
        self.__layout.addWidget(self.__lblXLabel, 3, 0)
        self.__layout.addWidget(self.__lblYLabel, 4, 0)
        self.__layout.addWidget(self.__txtTitle, 2, 1, 1, 2)
        self.__layout.addWidget(self.__txtXLabel, 3, 1, 1, 2)
        self.__layout.addWidget(self.__txtYLabel, 4, 1, 1, 2)
        self.__layout.addWidget(self.__chkLegend, 5, 0, 1, 3)
        self.__layout.addWidget(self.__chkTightLayout, 6, 0, 1, 3)

        self.__plot = Plot(Figure())
        self.__layout.addWidget(self.__plot, 0, 3, 6, 1)
        self.__btnUpdatePlot = QPushButton("Update plot")
        self.__btnUpdatePlot.clicked.connect(self.updatePlot)
        self.__layout.addWidget(self.__btnUpdatePlot, 6, 3)

        self.addPlotChoice()
        self.reload()
        self.updatePlot()

    def reload(self):
        for p in self.__plotChoices:
            p.reload(self.__app.data)

    def updatePlot(self):
        self.__plot.figure.clear()
        ax = self.__plot.figure.add_subplot(111)
        for p in self.__plotChoices:
            p.runPlot(ax, self.__app.data, legend=self.__chkLegend.isChecked())

        # this has to change when we add more than one subplot
        if self.__txtTitle.text() != "":
            try:
                ax.set_title(self.__txtTitle.text())
            except Exception as e:
                print(e)
        if self.__txtXLabel.text() != "":
            try:
                ax.set_xlabel(self.__txtXLabel.text())
            except Exception as e:
                print(e)
        if self.__txtYLabel.text() != "":
            try:
                ax.set_ylabel(self.__txtYLabel.text())
            except Exception as e:
                print(e)

        if self.__chkTightLayout.isChecked():
            self.__plot.figure.tight_layout()
        self.__plot.draw()

    def retranslateUi(self):
        pass

    def addPlotChoice(self, kind="1D"):
        if kind == "1D":
            p = PS1DPlotChoice()
        else:
            return

        p.reload(self.__app.data)
        self.__plotChoices.append(p)
        self.__cmbPlotChoice.addItem("1D")
        self.__cmbPlotChoice.setCurrentIndex(self.__cmbPlotChoice.count() - 1)

    def removePlotChoice(self):
        if len(self.__plotChoices) > 1:
            index = self.__cmbPlotChoice.currentIndex()
            del self.__plotChoices[index]
            self.__cmbPlotChoice.removeItem(index)
            if index > 0:
                self.__cmbPlotChoice.setCurrentIndex(index - 1)

    def __plotChoiceChanged(self, index: int):
        currentItem = self.__layout.itemAtPosition(1, 0)
        if currentItem is not None:
            self.__layout.replaceWidget(currentItem.widget(),
                                        self.__plotChoices[index])
            currentItem.widget().hide()
        else:
            self.__layout.addWidget(self.__plotChoices[index], 1, 0, 1, 3)
        self.__plotChoices[index].show()
        self.__plotChoices[index].setFixedWidth(200)

    def tight_layout(self):
        self.__plot.figure.tight_layout()
        self.__plot.draw()


class PSPlotChoice(QWidget):

    def __init__(self, parent: QObject = None):
        super().__init__(parent=parent)
        self._layout = QGridLayout()
        self.setLayout(self._layout)
        self._txtError = QTextEdit("")
        self._txtError.setReadOnly(True)
        self._layout.addWidget(self._txtError, 0, 0, 1, 2)
        self.__lblName = QLabel("Name:")
        self._layout.addWidget(self.__lblName, 1, 0)
        self._txtName = QLineEdit()
        self._layout.addWidget(self._txtName, 1, 1)

    def runPlot(self, ax: Axis, data: dict, **kwargs):
        raise NotImplementedError()

    def reload(self, data: dict):
        raise NotImplementedError()


class PS1DPlotChoice(PSPlotChoice):

    def __init__(self, parent: QObject = None):
        super().__init__(parent=parent)
        self.__lblXData = QLabel("x-data key:")
        self.__lblYData = QLabel("y-data key:")
        self.__lblXError = QLabel("x-error key:")
        self.__lblYError = QLabel("y-error key:")
        self.__lblFormat = QLabel("Format:")
        self.__lblLineshape = QLabel("Linestyle:")
        self.__lblColor = QLabel("Color:")
        self._layout.addWidget(self.__lblXData, 2, 0)
        self._layout.addWidget(self.__lblYData, 3, 0)
        self._layout.addWidget(self.__lblXError, 4, 0)
        self._layout.addWidget(self.__lblYError, 5, 0)
        self._layout.addWidget(self.__lblFormat, 6, 0)
        self._layout.addWidget(self.__lblLineshape, 7, 0)
        self._layout.addWidget(self.__lblColor, 8, 0)
        self.__cmbXData = QComboBox()
        self.__cmbYData = QComboBox()
        self.__cmbXError = QComboBox()
        self.__cmbYError = QComboBox()
        self.__txtFormat = QLineEdit()
        self.__txtLinestyle = QLineEdit()
        self.__txtColor = QLineEdit()
        self._layout.addWidget(self.__cmbXData, 2, 1)
        self._layout.addWidget(self.__cmbYData, 3, 1)
        self._layout.addWidget(self.__cmbXError, 4, 1)
        self._layout.addWidget(self.__cmbYError, 5, 1)
        self._layout.addWidget(self.__txtFormat, 6, 1)
        self._layout.addWidget(self.__txtLinestyle, 7, 1)
        self._layout.addWidget(self.__txtColor, 8, 1)

    def runPlot(self, ax: Axis, data: dict, **kwargs):
        self._txtError.setPlainText("Ready")
        xKey = self.__cmbXData.currentText()
        yKey = self.__cmbYData.currentText()
        xErrKey = self.__cmbXError.currentText()
        yErrKey = self.__cmbYError.currentText()

        if (xKey is not None and yKey is not None and
                len(xKey) > 0 and len(yKey) > 0):
            xData, yData = data[xKey], data[yKey]

            try:
                plot_args = {"label": self._txtName.text()}
                if self.__txtLinestyle.text() != "":
                    plot_args["ls"] = self.__txtLinestyle.text()
                if self.__txtColor.text() != "":
                    plot_args["color"] = self.__txtColor.text()

                if xErrKey is not None and len(xErrKey) > 0:
                    xErr = data[xErrKey]
                else:
                    xErr = None
                if yErrKey is not None and len(yErrKey) > 0:
                    yErr = data[yErrKey]
                else:
                    yErr = None

                if xErr is not None or yErr is not None:
                    if self.__txtFormat.text() != "":
                        plot_args["fmt"] = self.__txtFormat.text()
                    ax.errorbar(xData, yData, xerr=xErr, yerr=yErr,
                                **plot_args)
                else:
                    if self.__txtFormat.text() != "":
                        ax.plot(xData, yData,
                                self.__txtFormat.text(), **plot_args)
                    else:
                        ax.plot(xData, yData, **plot_args)
            except Exception as e:
                self._txtError.setPlainText(str(e))
                print(e)
                return

            try:
                if "legend" in kwargs and kwargs["legend"]:
                    ax.legend()
            except Exception as e:
                self._txtError.setPlainText(str(e))
                print(e)
                return

    def reload(self, data: dict):
        self.__cmbXData.clear()
        self.__cmbYData.clear()
        self.__cmbXError.clear()
        self.__cmbYError.clear()

        self.__cmbXError.addItem("")
        self.__cmbYError.addItem("")

        for key in data:
            d = data[key]
            if isinstance(d, np.ndarray) or isinstance(d, pd.Series):
                if len(d.shape) == 1:
                    self.__cmbXData.addItem(key)
                    self.__cmbYData.addItem(key)
                    self.__cmbXError.addItem(key)
                    self.__cmbYError.addItem(key)
