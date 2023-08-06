# -*- coding: utf-8 -*-
"""Manager module.

contains PSManager, a subclass of QObject
"""

import json
import os
import shutil
from datetime import datetime
from math import sqrt
from threading import Thread
from time import sleep, time

from appdirs import user_config_dir
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from puzzlestream.backend import notificationsystem
from puzzlestream.backend.config import PSConfig
from puzzlestream.backend.signal import PSSignal
from puzzlestream.backend.stream import PSStream
from puzzlestream.backend.streamsection import PSStreamSection
from puzzlestream.backend.worker import PSWorker
from puzzlestream.ui.graphicsscene import PSGraphicsScene
from puzzlestream.ui.module import PSModule
from puzzlestream.ui.pipe import PSPipe
from puzzlestream.ui.puzzleitem import PSPuzzleItem
from puzzlestream.ui.translate import changeLanguage
from puzzlestream.ui.valve import PSValve

translate = QtCore.QCoreApplication.translate

try:
    import git
    gitAvailable = True
except Exception:
    gitAvailable = False


class PSManager(QtCore.QObject):

    """
    ===========================================================================
        Eventinitialisation
    """

    configChanged = QtCore.pyqtSignal(object)

    """
    ===========================================================================
        Creation and Initialisation
    """

    def __init__(self, parent: QtCore.QObject):
        super().__init__()
        self.__parent = parent
        self.__stream, self.__projectPath = None, None
        self.__repo = None
        self.__dirty, self.__dirtyChanged = False, PSSignal()
        self.__workers, self.__pendingWorkers = {}, []
        self.__scene = PSGraphicsScene()
        self.__scene.installEventFilter(self)
        self.__scene.mousePressed.connect(self.__itemDrag)
        self.__scene.positionChanged.connect(self.__positionChanged)
        self.__scene.mouseReleased.connect(self.__mouseReleased)
        self.__puzzleLocked = False
        self.__updateSignal = PSSignal()

        self.addStatus = None
        self.config = PSConfig()
        self.config.edited.connect(self.configChanged.emit)
        self.__dockingrange = 200
        self.__connectionOnDrop = False
        self.__connectionPair = None
        self.__oldCursorPos = QtGui.QCursor.pos()

        self.__workerPollTimer = QtCore.QTimer()
        self.__workerPollTimer.setInterval(10)
        self.__workerPollTimer.timeout.connect(self.__pollWorkers)

        self.__positionChangeAllowed = True

        language = self.config["language"]
        language = language[1][language[0]]
        changeLanguage(language)

        if not gitAvailable:
            notificationsystem.newNotification(translate(
                "Manager",
                "Git is not installed. Please install the git version " +
                "control system as described <a href=\"https://git-scm.com/" +
                "book/en/v2/Getting-Started-Installing-Git\">here</a>."
            ))

    @property
    def projectPath(self) -> str:
        return self.__projectPath

    @property
    def scene(self) -> PSGraphicsScene:
        return self.__scene

    @property
    def stream(self) -> PSStream:
        return self.__stream

    @property
    def repo(self):
        return self.__repo

    @property
    def dirty(self) -> bool:
        return self.__dirty

    @dirty.setter
    def dirty(self, value: bool):
        if self.projectPath is not None:
            self.__dirty = value
        else:
            self.__dirty = False
        self.dirtyChanged.emit(self.__dirty)

    @property
    def dirtyChanged(self) -> PSSignal:
        return self.__dirtyChanged

    @property
    def puzzleLocked(self) -> bool:
        return self.__puzzleLocked

    @property
    def updateSignal(self) -> PSSignal:
        return self.__updateSignal

    """
    ===========================================================================
        load - save - close
    """

    def close(self):
        self.__unlockProject()
        self.config.save()
        self.__stream.close()

    """
    ===========================================================================
        Handle additional libaries
    """

    def addLib(self, path: str):
        if path not in self.config["libs"]:
            self.config["libs"].append(path)
            self.config.save()

    def deleteLib(self, path: str):
        i = self.config["libs"].index(path)
        del self.config["libs"][i]
        self.config.save()

    """
    ===========================================================================
        Process Management
    """

    def registerWorker(self, ID: int, worker: PSWorker):
        if ID in self.__workers:
            del self.__workers[ID]
        else:
            self.__pendingWorkers.append((ID, worker))

    def stopAllWorkers(self):
        for w in list(self.__workers.values()):
            w.stop()

        self.__pendingWorkers = []

    def startWorkerPollTimer(self):
        if not self.__workerPollTimer.isActive():
            self.__workerPollTimer.start()

    def __pollWorkers(self):
        nWorkers = self.config["numberOfProcesses"]
        if nWorkers == 0:
            nWorkers = os.cpu_count()

        for w in list(self.__workers.values()):
            w.poll()

        while (len(self.__workers) < nWorkers and
               len(self.__pendingWorkers) > 0):
            w = self.__pendingWorkers.pop()
            w[1].run()
            self.__workers[w[0]] = w[1]

        if len(self.__workers) == 0:
            self.__workerPollTimer.stop()
            self.updateSignal.emit()

    """
    ===========================================================================
        GUI Interaction
    """

    def eventFilter(self, target: QtCore.QObject, event: QtCore.QEvent):
        if isinstance(event, QtWidgets.QGraphicsSceneMouseEvent):
            x, y = event.scenePos().x(), event.scenePos().y()

            if (self.addStatus is not None and
                    event.button() == QtCore.Qt.LeftButton):
                if self.addStatus == "intModule":
                    self.newModule(x, y)
                elif self.addStatus == "extModule":
                    path = QtWidgets.QFileDialog.getOpenFileName()
                    if os.path.isfile(path[0]):
                        self.newModule(x, y, path[0])
                elif self.addStatus == "pipe":
                    self.newPipe(x, y)
                elif self.addStatus == "valve":
                    self.newValve(x, y)
                elif self.addStatus.startswith("template "):
                    self.newModule(x, y, templatePath=self.addStatus[9:])
                self.addStatus = None
        return QtCore.QObject.eventFilter(self, target, event)

    def checkModulePipeConnectable(self, module: PSModule,
                                   pipe: PSPipe) -> bool:
        directionPossible = (
            # module -> pipe
            (not module.hasOutput) and (not pipe.hasInput),
            # pipe -> module
            (not module.hasInput) and (not pipe.hasOutput)
        )

        preConnectionDirection = module.calculatePreconnectionDirection(pipe)
        if preConnectionDirection is None:
            return (False, "")

        preConnectPosition = preConnectionDirection[0]
        pref = module.connectionPreference(preConnectPosition)

        if pref == "output":
            if directionPossible[0]:
                return (pipe.preConnect(module), ">")
            elif directionPossible[1]:
                return (module.preConnect(pipe), "<")
            else:
                return (False, "")

        elif pref == "input":
            if directionPossible[1]:
                return (module.preConnect(pipe), "<")
            elif directionPossible[0]:
                return (pipe.preConnect(module), ">")
            else:
                return (False, "")

    def checkPipePipeConnectable(self, pipe1: PSPipe, pipe2: PSPipe) -> bool:
        if (not pipe1.hasOutput) and (not pipe2.hasInput):
            # pipe1 -> pipe2
            return (pipe2.preConnect(pipe1), ">")
        elif (not pipe1.hasInput) and (not pipe2.hasOutput):
            # pipe2 -> pipe1
            return (pipe1.preConnect(pipe2), "<")
        else:
            return (False, "")

    def checkPipeValveConnectable(self, pipe: PSPipe, valve: PSValve) -> bool:
        if pipe.hasInput and pipe.hasOutput:
            return (False, "")
        elif valve.numberOfInputs + valve.numberOfOutputs == 4:
            return (False, "")

        preConnectionDirection = valve.calculatePreconnectionDirection(pipe)
        if preConnectionDirection is None:
            return (False, "")

        elif pipe.hasInput and (not pipe.hasOutput):
            if valve.numberOfInputs < 3:
                # pipe -> valve
                return (valve.preConnect(pipe), ">")
            else:
                return (False, "")

        elif pipe.hasOutput and (not pipe.hasInput):
            if valve.numberOfOutputs < 3:
                # valve -> pipe
                return (pipe.preConnect(valve), "<")
            else:
                return (False, "")
        else:
            preConnectPosition = preConnectionDirection[0]
            pref = valve.connectionPreference(preConnectPosition)
            if pref == "input":
                if valve.numberOfInputs < 3:
                    return (valve.preConnect(pipe), ">")
                else:
                    return (pipe.preConnect(valve), "<")
            elif pref == "output":
                if valve.numberOfOutputs < 3:
                    return (pipe.preConnect(valve), "<")
                else:
                    return (valve.preConnect(pipe), ">")

    def __itemDrag(self, puzzleItem: PSPuzzleItem):
        """OnClick of any puzzleitem, save initial Position of selection

        Force the scene to save the position of all selected puzzleitems
        to allow position reset, if there is no valid constellation OnDrop
        """
        self.__oldCursorPos = QtGui.QCursor.pos()
        self.scene.bkSelectedItemPos()
        self.__connectionOnDrop = False
        self.__positionChangeAllowed = False
        self.__positionChangeNotAllowedReason = None

    def __positionChanged(self, puzzleItem: PSPuzzleItem):
        """On movement of puzzleitem, disconnect selection from surrounding and
        prepare reconnect to destination.

        Check if the complete selection is bounded together.
        If the selection is not one block, puzzleitemmovements are restricted.
        Block selections are disconnected from its surroundings and can be
        moved as a free selection block.
        Handling of new connection preparation is done by the
        moveFreeSelectionBlock routine
        """

        self.__connectionOnDrop = False
        if self.scene.selectionIsOneBlock and not self.__puzzleLocked:
            sel = self.scene.selectedItemList
            unsel = self.scene.unselectedItemList
            self.__scene.registerConnectionsToCut()
            connectionsToCut = self.scene.connectionsToCut

            for pair in connectionsToCut:
                pair[1].removeConnection(pair[0])
                self.scene.unregisterConnection(pair[0], pair[1])

            self.__positionChangeAllowed = True
            self.__moveFreeSelectionBlock(puzzleItem)

            if len(connectionsToCut) > 0:
                self.dirty = True
                self.updateSignal.emit()
        else:
            self.__positionChangeAllowed = False
            if not self.scene.selectionIsOneBlock:
                self.__positionChangeNotAllowedReason = "NotOneBlock"
            else:
                self.__positionChangeNotAllowedReason = "Locked"

    def __moveFreeSelectionBlock(self, puzzleItem: PSPuzzleItem):
        """Move Selection consisting of only unconnected Items and check for
        possible connections to unselected Items.

        1. Calculate the dists of any selected item to any unselected
           item and save those pairs as possible connection canidates
        2. Find the pair of selected and unselected items with
           minimum distance
        3. Check if this distance is smaller than the docking range
           that shall be experienced
                a) distance > dockingrange:
                    - set flag: connectionOnDrop = False
                b) distance < dockingrange:
                    - check if the connection would lead to a valid
                      Puzzle
                        i) connection NOT valid:
                            - delete the pair of items from connection
                                cannidates
                            - go back to step 2
                        ii) connection valid:
                            - Save the right dockingstation for connection
                            - set flag: connectionOnDrop = True
                            - GUI feedback: dockingstation now visible

        """

        sel = self.scene.selectedItemList
        unsel = self.scene.unselectedItemList
        # ---  1. ---#
        if len(unsel) != 0 and not self.__puzzleLocked:
            dists = np.empty(
                [len(sel), len(unsel)]
            )
            for i in range(len(sel)):
                for j in range(len(unsel)):
                    dists[i, j] = self.scene.itemDistance(sel[i], unsel[j])

            edgeOutsiders = np.ones(dists.shape)
            edgeOutsiders[dists < self.__dockingrange] = 0
            edgeOutsiders[dists > 1.5 * self.__dockingrange] = 0

            for i in range(len(unsel)):
                if np.count_nonzero(edgeOutsiders[:, i]) > 0:
                    edgeOutsider = unsel[i]
                    if (isinstance(edgeOutsider, PSModule) or
                            isinstance(edgeOutsider, PSValve)):
                        edgeOutsider.hideDocksWithState("disconnected")
                        edgeOutsider.hideDocksWithState("preconnected")

            for i in range(len(sel)):
                edgeOutsider = sel[i]
                if (isinstance(edgeOutsider, PSModule) or
                        isinstance(edgeOutsider, PSValve)):
                    edgeOutsider.hideDocksWithState("disconnected")
                    edgeOutsider.hideDocksWithState("preconnected")

        # ---  2. ---#
            TryAnotherPair = True
            while TryAnotherPair:
                if np.count_nonzero(~np.isnan(dists)) == 0:
                    self.__connectionOnDrop = False
                    TryAnotherPair = False
                else:
                    minPairIndizes = np.unravel_index(
                        np.nanargmin(dists), dists.shape)
                    minDist = dists[minPairIndizes[0], minPairIndizes[1]]
                    if minDist > self.__dockingrange:
                        self.__connectionOnDrop = False
                        TryAnotherPair = False
                    else:
                        minPair = [sel[minPairIndizes[0]],
                                   unsel[minPairIndizes[1]]]
                        # -----------------------------------------------------
                        # Selected Module:
                        # -----------------------------------------------------
                        if isinstance(minPair[0], PSModule):
                            # Connection to pipe worth a check
                            if isinstance(minPair[1], PSPipe):
                                checkresult = self.checkModulePipeConnectable(
                                    minPair[0], minPair[1]
                                )
                                if checkresult[0]:
                                    self.__connectionOnDrop = True
                                    self.__connectionPair = (minPair[0],
                                                             minPair[1],
                                                             checkresult[1])

                            # Connect to Module or Valve impossible
                            else:
                                self.__connectionOnDrop = False

                        # -----------------------------------------------------
                        # Selected Pipe:
                        # -----------------------------------------------------
                        elif isinstance(minPair[0], PSPipe):
                            # Connect to Module worth a check
                            if isinstance(minPair[1], PSModule):
                                checkresult = self.checkModulePipeConnectable(
                                    minPair[1], minPair[0]
                                )
                                if checkresult[0]:
                                    self.__connectionOnDrop = True
                                    self.__connectionPair = (minPair[1],
                                                             minPair[0],
                                                             checkresult[1])
                            # Connect to Pipe worth a check
                            elif isinstance(minPair[1], PSPipe):
                                checkresult = self.checkPipePipeConnectable(
                                    minPair[0], minPair[1]
                                )
                                if checkresult[0]:
                                    self.__connectionOnDrop = True
                                    self.__connectionPair = (minPair[0],
                                                             minPair[1],
                                                             checkresult[1])
                            # Connect to Valve worth a check
                            elif isinstance(minPair[1], PSValve):
                                checkresult = self.checkPipeValveConnectable(
                                    minPair[0], minPair[1]
                                )
                                if checkresult[0]:
                                    self.__connectionOnDrop = True
                                    self.__connectionPair = (minPair[0],
                                                             minPair[1],
                                                             checkresult[1])
                            else:
                                self.__connectionOnDrop = False

                        # -----------------------------------------------------
                        # Selected Valve:
                        # -----------------------------------------------------
                        elif isinstance(minPair[0], PSValve):
                            # Connect to Pipe worth a check
                            if isinstance(minPair[1], PSPipe):
                                checkresult = self.checkPipeValveConnectable(
                                    minPair[1], minPair[0]
                                )
                                if checkresult[0]:
                                    self.__connectionOnDrop = True
                                    self.__connectionPair = (minPair[1],
                                                             minPair[0],
                                                             checkresult[1])
                            # Connection to module or valve impossible
                            else:
                                self.__connectionOnDrop = False
                        # If we find a connection we don't look for another one
                        if self.__connectionOnDrop:
                            TryAnotherPair = False
                        # Exclude entry if there is no possible connection
                        if TryAnotherPair:
                            dists[minPairIndizes[0], minPairIndizes[1]] = None

    def __mouseReleased(self, puzzleItem: PSPuzzleItem) -> bool:
        if (QtGui.QCursor.pos() != self.__oldCursorPos and not
                self.__puzzleLocked):
            sel = self.scene.selectedItemList
            unsel = self.scene.unselectedItemList

            # Check if there are collisions with unselected items that shall
            # not be connected to the selected puzzle items
            # In this case there is no position change allowed
            collisionFlag = False
            for selItem in sel:
                if not collisionFlag:
                    for item in self.scene.collidingItems(selItem):
                        if (isinstance(item, PSPuzzleItem) and
                                not (item in sel)):
                            if self.__connectionOnDrop:
                                if (selItem != self.__connectionPair[0] and
                                        selItem != self.__connectionPair[1]):
                                    collisionFlag = True
                                    break
                            else:
                                collisionFlag = True
                                break
            if collisionFlag:
                self.__positionChangeAllowed = False
                self.__positionChangeNotAllowedReason = "Collision"

            # If there is no acceptable change of position, all positions are
            # reset to the drag position
            if not self.__positionChangeAllowed:
                if self.__positionChangeNotAllowedReason == "NotOneBlock":
                    notificationsystem.newNotification(
                        translate("Manager", "You cannot move a selection " +
                                  "that is not one connected block."))
                self.scene.removeAllPreconnections()
                self.scene.resetItemPos()
                return False

            # If there is a acceptable change of position,
            # the complete selection has to be moved
            if self.__connectionOnDrop:
                self.scene.bkAllItemPos()

                if self.__connectionPair[2] == "<":
                    self.__connectionPair = (
                        self.__connectionPair[1], self.__connectionPair[0]
                    )

                movementVector = self.__connectionPair[1].establishConnection(
                    self.__connectionPair[0])
                self.scene.registerConnection(self.__connectionPair[0],
                                              self.__connectionPair[1])

                if self.__connectionPair[0] in sel:
                    for item in sel:
                        item.setCenterPos(item.centerPos() - movementVector)
                else:
                    for item in sel:
                        item.setCenterPos(item.centerPos() + movementVector)

                self.__connectionPair, self.__connectionOnDrop = None, False

                # Check for additional valve connections to build data reunion
                for valve in self.scene.valves.values():
                    neighbors = []
                    if valve.topFree:
                        neighbor = self.scene.neighbor(valve, "top")
                        if neighbor is not None:
                            neighbors.append(neighbor)
                    if valve.rightFree:
                        neighbor = self.scene.neighbor(valve, "right")
                        if neighbor is not None:
                            neighbors.append(neighbor)
                    if valve.leftFree:
                        neighbor = self.scene.neighbor(valve, "left")
                        if neighbor is not None:
                            neighbors.append(neighbor)
                    if valve.bottomFree:
                        neighbor = self.scene.neighbor(valve, "bottom")
                        if neighbor is not None:
                            neighbors.append(neighbor)

                    for neighbor in neighbors:
                        if isinstance(neighbor, PSPipe):
                            checkresult = self.checkPipeValveConnectable(
                                neighbor, valve
                            )
                            if checkresult[0]:
                                connPair = (neighbor, valve, checkresult[1])
                                if connPair[2] == "<":
                                    connPair = (connPair[1], connPair[0])

                                connPair[1].establishConnection(connPair[0])

                                self.scene.registerConnection(connPair[0],
                                                              connPair[1])
                self.dirty = True
                self.updateSignal.emit()

            self.scene.removeAllPreconnections()
            self.scene.bkSelectedItemPos()
            return True

        self.scene.removeAllPreconnections()
        return True

    def newModule(self, x: int, y: int, path: str = None,
                  templatePath: str = None):
        moduleID = self.scene.getNextID()

        if path is None:
            modPath, name = ".", translate(
                "Manager", "Module_") + str(moduleID)
        else:
            modPath, name = os.path.split(os.path.splitext(path)[0])

        module = PSModule(
            moduleID, x, y, modPath, name,
            self.newStreamSection, self.registerWorker,
            self.startWorkerPollTimer, self.config["libs"]
        )

        if templatePath is not None:
            with open(os.path.join(
                    user_config_dir("Puzzlestream"),
                    "templates",
                    templatePath + ".py")) as f:
                module.createModuleScript(text=f.read())
        elif path is None or os.stat(module.filePath).st_size == 0:
            module.createModuleScript()

        self.scene.addModule(module)

    def newPipe(self, x: int, y: int):
        pipe = PSPipe(self.scene.getNextID(), self.newStreamSection, x, y)
        self.scene.addPipe(pipe)

    def newValve(self, x: int, y: int):
        valve = PSValve(self.scene.getNextID(), self.newStreamSection, x, y)
        self.scene.addValve(valve)

    def newStreamSection(self, pipeID: int):
        return PSStreamSection(pipeID, self.__stream)

    def newProject(self, path: str):
        if self.__lockProject(path):
            if self.__stream is not None:
                self.__stream.close()
            self.__stream = PSStream(path + "/pscache")
            self.__initRepoIfNeeded(path)
            self.__projectPath = path
            os.chdir(self.__projectPath)
            self.__scene.clear()
            self.config.addRecentProject(path)
            self.scene.lastID = -1
            self.dirty = True

    def save(self, thread: bool = True):
        if thread:
            thr = Thread(target=self.__savePuzzle, args=(self.__projectPath,))
            thr.start()
        else:
            self.__savePuzzle(self.__projectPath)

    def saveAs(self, path: str):
        shutil.rmtree(path)
        shutil.copytree(self.__projectPath, path)
        thr = Thread(target=self.__savePuzzle, args=(path,))
        thr.start()

        for module in self.scene.modules.values():
            if module.path == self.__projectPath:
                module.path = path

        self.__projectPath = path
        self.__stream.close()
        self.__stream = PSStream(self.__projectPath + "/pscache")
        self.config.addRecentProject(path)

    def closeProject(self):
        self.__unlockProject()
        if self.__stream is not None:
            self.__stream.close()
        self.__projectPath = None
        self.__scene.clear()

    def load(self, path: str, silent: bool = False):
        self.closeProject()
        if self.__lockProject(path, silent=silent):
            self.__stream = PSStream(path + "/pscache")
            self.__initRepoIfNeeded(path)
            self.__projectPath = path
            os.chdir(self.__projectPath)
            self.__loadPuzzle(self.__projectPath, False)
            self.config.addRecentProject(path)
            self.dirty = False

    def __lockProject(self, path: str, silent: bool = False) -> bool:
        fpath = os.path.join(path, ".pslock")
        if not os.path.exists(fpath):
            try:
                with open(fpath, "w") as f:
                    f.write(datetime.now().strftime(
                        "%Y:%m:%d-%H:%M:%S") + "\n")
                return True
            except Exception as e:
                print(e)
        elif not silent:
            msg = QtWidgets.QMessageBox(self.__parent)
            msg.setWindowTitle(translate("Manager", "Project locked"))
            msg.setText(
                translate(
                    "Manager",
                    "The project you are trying to open is locked. Please " +
                    "close the Puzzlestream instance using this project " +
                    "folder first.\n\nIf you are sure that nobody else is " +
                    "currently accessing the project, you may unlock " +
                    "it using the button below."
                ) + "\n\n" + translate(
                    "Manager",
                    "The project you were trying to open is located here:\n"
                ) + path
            )
            msg.addButton(
                QtWidgets.QPushButton(translate("Manager", "Abort")),
                QtWidgets.QMessageBox.NoRole
            )
            btnUnlock = QtWidgets.QPushButton(
                translate("Manager", "Unlock project"))
            msg.addButton(btnUnlock, QtWidgets.QMessageBox.YesRole)
            msg.exec_()

            if msg.clickedButton() == btnUnlock:
                os.remove(fpath)
                return self.__lockProject(path, silent)
        return False

    def __unlockProject(self):
        if self.__projectPath is not None:
            try:
                path = os.path.join(self.__projectPath, ".pslock")
                if os.path.isfile(path):
                    os.remove(path)
            except Exception as e:
                print(e)

    def __initRepoIfNeeded(self, path: str):
        if gitAvailable:
            initial = False

            try:
                self.__repo = git.Repo(path)
            except Exception as e:
                try:
                    git.Repo.init(path)
                    self.__repo = git.Repo(path)
                    initial = True
                except Exception as e:
                    print(e)
                    notificationsystem.newNotification(
                        translate("Manager", "Git error:") + " " + str(e))

            if ".gitignore" not in os.listdir(path):
                with open(os.path.join(path, ".gitignore"), "w") as f:
                    f.write("pscache/*\n")
                    f.write("__pycache__/*\n")
                    f.write(".pslock\n")
                initial = True

            if initial:
                try:
                    self.__repo.git.add(".")
                    self.__repo.index.commit("Initial commit")
                except Exception as e:
                    print(e)
                    notificationsystem.newNotification(
                        translate("Manager", "Git error:") + " " + str(e))

    def __savePuzzle(self, path: str):
        self.config.save()

        if path is not None:
            moduleProps = []
            for moduleID in self.__scene.modules:
                moduleProps.append(
                    self.__scene.modules[moduleID].saveProperties)

            pipeProps = []
            for pipeID in self.__scene.pipes:
                pipeProps.append(self.__scene.pipes[pipeID].saveProperties)

            valveProps = []
            for valveID in self.__scene.valves:
                valveProps.append(self.__scene.valves[valveID].saveProperties)

            with open(path + "/puzzle.json", "w") as f:
                json.dump(
                    {"modules": moduleProps, "pipes": pipeProps,
                     "valves": valveProps, "lastID": self.__scene.lastID,
                     "puzzleLocked": self.puzzleLocked},
                    f,
                    sort_keys=True,
                    indent=4
                )

            self.dirty = False

    def __loadPuzzle(self, path: str, clearStream: bool = False):
        if clearStream and self.__stream is not None:
            self.__stream.clear()
        with open(path + "/puzzle.json", "r") as f:
            puzzle = json.load(f)

        if "lastID" in puzzle:
            self.__scene.lastID = puzzle["lastID"]

        self.__scene.clear()
        pipes = []
        for props in puzzle["pipes"]:
            pipe = PSPipe(props["id"], self.newStreamSection, props["x"],
                          props["y"], props["orientation"])
            pipe.restoreProperties(props, self.__stream)
            pipes.append(pipe)
            self.__scene.addPipe(pipe)

        for props in puzzle["valves"]:
            valve = PSValve(props["id"], self.newStreamSection,
                            props["x"], props["y"])
            inPipeIDs = props["inPipeIDs"]
            self.__scene.addValve(valve)

            for i in inPipeIDs:
                pipe = self.__scene.pipes[i]
                valve.preConnect(pipe)
                valve.establishConnection(pipe, silent=True)
                self.scene.registerConnection(pipe, valve)

            valve.restoreProperties(props, self.__stream)

        for props in puzzle["modules"]:
            module = PSModule(props["id"], props["x"], props["y"],
                              props["path"], props["name"],
                              self.newStreamSection, self.registerWorker,
                              self.startWorkerPollTimer, self.config["libs"])

            self.__scene.addModule(module)

            if "inPipeID" in props:
                pipe = self.__scene.pipes[props["inPipeID"]]
                module.preConnect(pipe)
                module.establishConnection(pipe, silent=True)
                self.scene.registerConnection(pipe, module)

            module.restoreProperties(props, self.__stream)

        for i in range(len(pipes)):
            props = puzzle["pipes"][i]
            if "inItemID" in props:
                if props["inItemID"] in self.__scene.pipes:
                    inItem = self.__scene.pipes[props["inItemID"]]
                elif props["inItemID"] in self.__scene.modules:
                    inItem = self.__scene.modules[props["inItemID"]]
                else:
                    inItem = self.__scene.valves[props["inItemID"]]

                pipes[i].preConnect(inItem)
                pipes[i].establishConnection(inItem, silent=True)
                self.scene.registerConnection(inItem, pipes[i])

        if "puzzleLocked" in puzzle:
            self.__puzzleLocked = puzzle["puzzleLocked"]
            if self.__puzzleLocked:
                self.setAllItemsFixed()
            else:
                self.setAllItemsMovable()

    def setAllItemsMovable(self):
        for item in (list(self.scene.modules.values()) +
                     list(self.scene.pipes.values()) +
                     list(self.scene.valves.values())):
            item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.__puzzleLocked = False

    def setAllItemsFixed(self):
        for item in (list(self.scene.modules.values()) +
                     list(self.scene.pipes.values()) +
                     list(self.scene.valves.values())):
            item.setFlags(item.flags() ^ QtWidgets.QGraphicsItem.ItemIsMovable)
        self.__puzzleLocked = True
