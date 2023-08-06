import os

from puzzlestream.backend.signal import PSSignal
from puzzlestream.ui.codeeditor import PSCodeEdit
from puzzlestream.ui.fileexplorer import PSFileExplorer
from puzzlestream.ui.module import PSModule
from pyqode.python.backend import server
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

translate = QCoreApplication.translate


class PSEditorWidget(QSplitter):

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.__editorWidget = QWidget()
        self.__editorLayout = QGridLayout()
        self.__editorWidget.setLayout(self.__editorLayout)
        self.__editorLayout.setContentsMargins(0, 0, 0, 0)
        self.__editorLayout.setSpacing(0)
        self.editorHeader = QWidget(self)
        self.editorHeader.setObjectName("editorHeader")
        self.editorHeaderLayout = QHBoxLayout()
        self.editorHeader.setLayout(self.editorHeaderLayout)
        self.editorFilePathLabel = QLabel(self.editorHeader)
        self.editorFilePathLabel.setObjectName("editorFilePathLabel")
        self.editorHeaderLayout.addWidget(self.editorFilePathLabel)
        self.__editorLayout.addWidget(self.editorHeader, 0, 1)

        # file explorer stuff
        self.__fileExplorer = PSFileExplorer(self)
        self.__fileExplorer.openFileSignal.connect(self.__openArbitraryFile)
        # self.__layout.addWidget(self.__fileExplorer, 0, 0, 2, 1)
        self.__moduleFileOpened = PSSignal()

        self.editor = PSCodeEdit(server.__file__)
        self.__editorLayout.addWidget(self.editor, 1, 1)
        self.currentIndexChangedConnected = False
        self.__currentModule = None
        self.__modules = []

        self.addWidget(self.__fileExplorer)
        self.addWidget(self.__editorWidget)
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 5)

    @property
    def fileExplorer(self):
        return self.__fileExplorer

    @property
    def moduleFileOpened(self):
        return self.__moduleFileOpened

    def setModules(self, modules: list):
        self.__modules = modules

    def __openArbitraryFile(self, path: str):
        self.editor.file.open(path)
        self.__currentModule = None
        for m in self.__modules:
            if os.path.normpath(path) == os.path.normpath(m.filePath):
                self.__currentModule = m
                break
        if self.__currentModule is not None:
            self.editorFilePathLabel.setText(
                m.filePath + " - " +
                translate("Status", str(self.__currentModule.status))
            )
            self.moduleFileOpened.emit(m)
            if self.editorHeaderLayout.count() > 2:
                for i in range(2):
                    self.editorHeaderLayout.itemAt(i).widget().setEnabled(True)
        else:
            self.editorFilePathLabel.setText(path)
            if self.editorHeaderLayout.count() > 2:
                for i in range(2):
                    self.editorHeaderLayout.itemAt(
                        i).widget().setEnabled(False)

    def openModule(self, module: PSModule):
        self.editor.file.open(module.filePath)
        self.__fileExplorer.selectFile(module.filePath)
        self.editorFilePathLabel.setText(
            module.filePath + " - " +
            translate("Status", str(module.status))
        )
