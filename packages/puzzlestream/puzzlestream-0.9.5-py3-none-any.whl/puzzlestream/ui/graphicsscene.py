# -*- coding: utf-8 -*-
"""Graphics scene module.

contains PSGraphicsScene, a subclass of QGraphicsScene
"""

import numpy as np
from puzzlestream.ui import colors
from puzzlestream.ui.module import PSModule
from puzzlestream.ui.pipe import PSPipe
from puzzlestream.ui.puzzleitem import PSPuzzleItem
from puzzlestream.ui.valve import PSValve
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

translate = QCoreApplication.translate


class PSGraphicsScene(QGraphicsScene):

    """
    ===========================================================================
        Event initialisation
    """

    stdoutChanged = pyqtSignal(object, object)
    statusChanged = pyqtSignal(object)
    nameChanged = pyqtSignal(object)
    mousePressed = pyqtSignal(object)
    positionChanged = pyqtSignal(object)
    mouseReleased = pyqtSignal(object)
    progressChanged = pyqtSignal(object)
    itemAdded = pyqtSignal(object)
    itemDeleted = pyqtSignal(object)
    dataViewRequested = pyqtSignal(object)
    plotViewRequested = pyqtSignal(object)

    """
    ===========================================================================
        Creation and initialisation
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.__modules, self.__pipes, self.__valves = {}, {}, {}
        self.__bkCenterPos = {}
        self.__connMatrix = np.zeros((0, 0), dtype=bool)
        self.__connMatrixIndexBindings = []

        self.__selItems = []
        self.__unselItems = []
        self.__connectionsToCut = []
        self.__selConnMatrix = np.zeros((0, 0), dtype=bool)

        self.lastID = -1

        self.selectionChanged.connect(self.__onSelectionChanged)
        self.__standardContextMenu = None

    """
    ===========================================================================
        Content properties
    """

    @property
    def numberOfItems(self) -> int:
        return (len(self.__modules) + len(self.__pipes) + len(self.__valves))

    @property
    def puzzleItemList(self) -> list:
        return (list(self.modules.values()) +
                list(self.pipes.values()) +
                list(self.valves.values()))

    @property
    def modules(self) -> dict:
        return self.__modules

    @property
    def pipes(self) -> dict:
        return self.__pipes

    @property
    def valves(self) -> dict:
        return self.__valves

    """
    ===========================================================================
        Reset itempositions
    """

    def bkAllItemPos(self):
        for item in self.puzzleItemList:
            self.__bkCenterPos[item.id] = item.centerPos()

    def bkSomePos(self, itemlist: list):
        for item in itemlist:
            self.__bkCenterPos[item.id] = item.centerPos()

    def bkSelectedItemPos(self):
        for item in self.selectedItemList:
            self.__bkCenterPos[item.id] = item.centerPos()

    def resetItemPos(self):
        for item in self.puzzleItemList:
            item.setCenterPos(self.__bkCenterPos[item.id])

    """
    ===========================================================================
        Relations between items in scene
    """

    def itemDistance(self, item1: PSPuzzleItem, item2: PSPuzzleItem) -> float:
        x1, y1 = item1.centerPos().x(), item1.centerPos().y()
        x2, y2 = item2.centerPos().x(), item2.centerPos().y()
        dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return dist

    def neighbor(self, item: PSPuzzleItem, position: str) -> PSPuzzleItem:
        if position == "right":
            shift = QPointF(item.width, 0)
        if position == "left":
            shift = QPointF(-item.width, 0)
        if position == "top":
            shift = QPointF(0, -item.width)
        if position == "bottom":
            shift = QPointF(0, item.width)

        return self.puzzleItemAtPosition(item.centerPos() + shift)

    def puzzleItemAtPosition(self, pos: QPoint) -> PSPuzzleItem:
        itemlist = self.items(pos)
        for item in itemlist:
            if isinstance(item, PSPuzzleItem):
                return item
    """
    ===========================================================================
        Item creation
    """

    def getNextID(self) -> int:
        self.lastID += 1
        return self.lastID

    def __setStandardConnections(
        self,
        puzzleItem: PSPuzzleItem
    ) -> PSPuzzleItem:
        puzzleItem.statusChanged.connect(self.statusChanged.emit)
        puzzleItem.positionChanged.connect(self.positionChanged.emit)
        puzzleItem.mouseReleased.connect(self.mouseReleased.emit)
        puzzleItem.mousePressed.connect(self.mousePressed.emit)
        puzzleItem.dataViewRequested.connect(self.dataViewRequested.emit)
        puzzleItem.plotViewRequested.connect(self.plotViewRequested.emit)
        puzzleItem.deletionRequested.connect(self.deleteItem)
        puzzleItem.contextMenuRequested.connect(self.__contextMenuRequest)
        return puzzleItem

    def addModule(self, module: PSModule):
        if isinstance(module, PSModule):
            module = self.__setStandardConnections(module)
            module.stdoutChanged.connect(self.stdoutChanged.emit)
            module.nameChanged.connect(self.nameChanged.emit)
            module.progressChanged.connect(self.progressChanged.emit)
            self.statusChanged.connect(module.visualStatusUpdate)
            self.__modules[module.id] = module
            self.addItem(module)
            self.itemAdded.emit(module)
            self.bkSomePos([module])
            self.__addToConnMatrix(module)
        else:
            raise TypeError("Has to be a module.")

    def addPipe(self, pipe: PSPipe):
        if isinstance(pipe, PSPipe):
            self.__pipes[pipe.id] = pipe
            pipe = self.__setStandardConnections(pipe)
            self.addItem(pipe)
            self.itemAdded.emit(pipe)
            self.bkSomePos([pipe])
            self.__addToConnMatrix(pipe)
        else:
            raise TypeError("Has to be a pipe.")

    def addValve(self, valve: PSValve):
        if isinstance(valve, PSValve):
            self.__valves[valve.id] = valve
            valve = self.__setStandardConnections(valve)
            self.addItem(valve)
            self.itemAdded.emit(valve)
            self.bkSomePos([valve])
            self.__addToConnMatrix(valve)
        else:
            raise TypeError("Has to be a valve.")

    """
    ===========================================================================
        Item selection
    """

    def registerConnectionsToCut(self):
        self.__connectionsToCut = []

        for item in self.__selItems:
            for inputItem in item.inputItems:
                if inputItem in self.__unselItems:
                    self.__connectionsToCut.append((inputItem, item))

        for item in self.__unselItems:
            for inputItem in item.inputItems:
                if inputItem in self.__selItems:
                    self.__connectionsToCut.append((inputItem, item))

    def __createSelConnMatrix(self):
        copyToSelConnMatrix = np.ones(self.__connMatrix.shape, dtype=bool)
        for item in self.__unselItems:
            index = self.__connMatrixIndexBindings.index(item.id)
            copyToSelConnMatrix[index, :] = False
            copyToSelConnMatrix[:, index] = False
        nSelItems = len(self.__selItems)
        self.__selConnMatrix = np.resize(
            self.__connMatrix[copyToSelConnMatrix], (nSelItems, nSelItems))

    def __onSelectionChanged(self):
        """Triggered on selection-change. Updates selection lists and array."""
        self.__selItems = []
        self.__unselItems = []
        for item in self.puzzleItemList:
            if item.isSelected():
                self.__selItems.append(item)
            else:
                self.__unselItems.append(item)
        self.__createSelConnMatrix()
        self.registerConnectionsToCut()

    @property
    def selectedItemList(self) -> list:
        return self.__selItems

    @property
    def unselectedItemList(self) -> list:
        return self.__unselItems

    @property
    def selectionIsOneBlock(self) -> bool:
        return (np.count_nonzero(self.__selConnMatrix) ==
                len(self.__selItems) - 1)

    @property
    def connectionsToCut(self) -> list:
        return self.__connectionsToCut

    """
    ===========================================================================
        Item connection
    """

    def __findConnectionIndices(self, inp: PSPuzzleItem,
                                output: PSPuzzleItem) -> tuple:
        inInd = self.__connMatrixIndexBindings.index(inp.id)
        outInd = self.__connMatrixIndexBindings.index(output.id)
        return inInd, outInd

    def __addToConnMatrix(self, puzzleItem: PSPuzzleItem):
        """Expand connMatrix and connMatrixIndexBindings"""
        oldSize = len(self.__connMatrix)
        newSize = oldSize + 1
        expandedMatrix = np.zeros((newSize, newSize), dtype=bool)
        expandedMatrix[:oldSize, :oldSize] = self.__connMatrix
        self.__connMatrix = expandedMatrix
        self.__connMatrixIndexBindings.append(puzzleItem.id)

    def registerConnection(self, inputItem: PSPuzzleItem,
                           outputItem: PSPuzzleItem):
        inInd, outInd = self.__findConnectionIndices(inputItem, outputItem)
        self.__connMatrix[outInd, inInd] = True
        self.registerConnectionsToCut()

        for item in self.puzzleItemList:
            ind = self.__connMatrixIndexBindings.index(item.id)
            if np.sum(self.__connMatrix[:, ind]) == 0:
                item.updateStreamSectionFromInputs()

    def unregisterConnection(self, inputItem: PSPuzzleItem,
                             outputItem: PSPuzzleItem):
        inInd, outInd = self.__findConnectionIndices(inputItem, outputItem)
        self.__connMatrix[outInd, inInd] = False

    def removeAllPreconnections(self):
        for item in self.puzzleItemList:
            item.removePreconnections()

    """
    ===========================================================================
        Item deletion
    """

    def __removeFromConnMatrix(self, puzzleItem: PSPuzzleItem):
        index = self.__connMatrixIndexBindings.index(puzzleItem.id)
        self.__connMatrix = np.delete(self.__connMatrix, index, axis=0)
        self.__connMatrix = np.delete(self.__connMatrix, index, axis=1)
        del self.__connMatrixIndexBindings[index]

    def deleteItem(self, puzzleItem: PSPuzzleItem):
        for item in puzzleItem.inputItems:
            puzzleItem.removeConnection(item)

        itemIndex = self.__connMatrixIndexBindings.index(puzzleItem.id)
        connections = self.__connMatrix[:, itemIndex]

        for i, c in enumerate(connections):
            if c:
                otherItem = None

                otherID = self.__connMatrixIndexBindings[i]
                if otherID in self.__modules:
                    otherItem = self.__modules[otherID]
                elif otherID in self.__pipes:
                    otherItem = self.__pipes[otherID]
                elif otherID in self.__valves:
                    otherItem = self.__valves[otherID]

                if otherItem is not None:
                    otherItem.removeConnection(puzzleItem)

        self.removeItem(puzzleItem)
        self.__removeFromConnMatrix(puzzleItem)

        if isinstance(puzzleItem, PSModule):
            del self.__modules[puzzleItem.id]
        elif isinstance(puzzleItem, PSPipe):
            del self.__pipes[puzzleItem.id]
        elif isinstance(puzzleItem, PSValve):
            del self.__valves[puzzleItem.id]

        self.itemDeleted.emit(puzzleItem)

    def deleteItems(self, items: list):
        for i in items:
            self.deleteItem(i)

    def clear(self):
        for item in self.puzzleItemList:
            item.setSelected(False)
        self.__modules.clear()
        self.__pipes.clear()
        self.__valves.clear()
        super().clear()

    """
    ===========================================================================
        Context menu stuff
    """

    def setStandardContextMenu(self, menu: QMenu):
        self.__standardContextMenu = menu

    def contextMenuEvent(self, event: QEvent):
        if (self.itemAt(event.scenePos(), QTransform()) is None and
                self.__standardContextMenu is not None):
            self.__standardContextMenu.exec(event.screenPos())
        else:
            super().contextMenuEvent(event)

    def __contextMenuRequest(self, item: PSPuzzleItem, event: QEvent):
        menu = None

        if item.isSelected():
            items = self.selectedItemList

            if len(items) == 1:
                menu = self.__singleItemMenu(item)
            else:
                menu = self.__multipleItemsMenu(items)
        else:
            menu = self.__singleItemMenu(item)

        if menu is not None:
            menu.exec(event.screenPos())

    def __singleItemMenu(self, item: PSPuzzleItem) -> QMenu:
        if isinstance(item, PSModule):
            return self.__singleModuleMenu(item)
        elif isinstance(item, PSPipe):
            return self.__singlePipeMenu(item)
        elif isinstance(item, PSValve):
            return self.__singleValveMenu(item)

    def __singleModuleMenu(self, module: PSModule) -> QMenu:
        menu = QMenu()
        runAction = menu.addAction(
            translate("GraphicsScene", "Run from here"))
        dataViewAction = menu.addAction(
            translate("GraphicsScene", "Show data"))
        plotViewAction = menu.addAction(
            translate("GraphicsScene", "Show plots"))
        menu.addSeparator()
        outsourceAction = menu.addAction(
            translate("GraphicsScene", "Change module file path"))
        deleteAction = menu.addAction(
            translate("GraphicsScene", "Delete module"))

        runAction.triggered.connect(module.run)
        dataViewAction.triggered.connect(
            lambda x, m=module: self.dataViewRequested.emit(m))
        plotViewAction.triggered.connect(
            lambda x, m=module: self.plotViewRequested.emit(m))
        deleteAction.triggered.connect(lambda x, m=module: self.deleteItem(m))
        outsourceAction.triggered.connect(module.outsource)
        return menu

    def __singlePipeMenu(self, pipe: PSPipe) -> QMenu:
        menu = QMenu()
        runAction = menu.addAction(
            translate("GraphicsScene", "Run from here"))
        dataViewAction = menu.addAction(
            translate("GraphicsScene", "Show data"))
        plotViewAction = menu.addAction(
            translate("GraphicsScene", "Show plots"))

        if pipe.autopass:
            closingAction = menu.addAction(
                translate("GraphicsScene", "Close pipe"))
        else:
            closingAction = menu.addAction(
                translate("GraphicsScene", "Open pipe"))

        deleteAction = menu.addAction(
            translate("GraphicsScene", "Delete pipe"))

        runAction.triggered.connect(pipe.runFromHere)
        dataViewAction.triggered.connect(
            lambda x, p=pipe: self.dataViewRequested.emit(p))
        plotViewAction.triggered.connect(
            lambda x, p=pipe: self.plotViewRequested.emit(p))
        closingAction.triggered.connect(pipe.toggleOpenClosed)
        deleteAction.triggered.connect(lambda x, p=pipe: self.deleteItem(p))
        return menu

    def __singleValveMenu(self, valve: PSValve) -> QMenu:
        menu = QMenu()
        runAction = menu.addAction(
            translate("GraphicsScene", "Run from here"))
        dataViewAction = menu.addAction(
            translate("GraphicsScene", "Show data"))
        plotViewAction = menu.addAction(
            translate("GraphicsScene", "Show plots"))

        if valve.autopass:
            closingAction = menu.addAction(
                translate("GraphicsScene", "Close valve"))
        else:
            closingAction = menu.addAction(
                translate("GraphicsScene", "Open valve"))

        stopIncompleteAction = menu.addAction(
            translate("GraphicsScene", "Propagate incomplete inputs"))
        stopIncompleteAction.setCheckable(True)
        stopIncompleteAction.setChecked(valve.propagateIncompleteInputs)

        deleteAction = menu.addAction(
            translate("GraphicsScene", "Delete valve"))

        runAction.triggered.connect(valve.runFromHere)
        dataViewAction.triggered.connect(
            lambda x, v=valve: self.dataViewRequested.emit(v))
        plotViewAction.triggered.connect(
            lambda x, v=valve: self.plotViewRequested.emit(v))
        closingAction.triggered.connect(valve.toggleOpenClosed)
        stopIncompleteAction.triggered.connect(
            valve.togglePropagateIncompleteInputs)
        deleteAction.triggered.connect(lambda x, v=valve: self.deleteItem(v))
        return menu

    def __multipleItemsMenu(self, items: list) -> QMenu:
        menu = QMenu()

        if all([isinstance(i, PSModule) for i in items]):
            text = "modules"
        elif all([isinstance(i, PSPipe) for i in items]):
            text = "pipes"
        elif all([isinstance(i, PSValve) for i in items]):
            text = "valves"
        else:
            text = "items"

        deleteAction = menu.addAction(
            translate("GraphicsScene", "Delete") + " " + text)
        deleteAction.triggered.connect(
            lambda x, items=items: self.deleteItems(items))
        return menu
