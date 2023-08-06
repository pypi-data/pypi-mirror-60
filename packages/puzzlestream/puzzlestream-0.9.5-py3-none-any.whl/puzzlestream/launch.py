import ctypes
import sys
from multiprocessing import current_process, set_start_method
from os import listdir, makedirs, name, path, remove
from time import time

import matplotlib
import pkg_resources
from appdirs import user_config_dir

matplotlib.use("Qt5Agg")

if current_process().name == "MainProcess":
    set_start_method("spawn")
    import sys
    from PyQt5 import QtCore, QtGui, QtWidgets


def setStdout():
    configDir = user_config_dir("Puzzlestream")
    logDir = path.join(configDir, "logs")
    if not path.exists(logDir):
        makedirs(logDir)

    paths = [path.join(logDir, p) for p in listdir(logDir)]
    if len(paths) > 25:
        remove(min(paths, key=path.getctime))

    out = open(path.join(logDir, "%d.log" % (time())), "w")
    sys.stdout, sys.stderr = out, out
    print("--- Starting Puzzlestream at %d on %s ---" % (time(), name))
    print("Package set:")
    pkg_resources._initialize_master_working_set()
    for p in pkg_resources.working_set:
        print(p.key, "(%s)" % (p.version))
    print("\n--- Output ---")
    sys.stdout.flush()
    sys.stderr.flush()


def initApp():
    """Create application."""

    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    QtWidgets.QApplication.setAttribute(
        QtCore.Qt.AA_CompressHighFrequencyEvents
    )
    app = QtWidgets.QApplication(sys.argv)
    currentDir = path.dirname(__file__)

    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "puzzlestream")

    app.setWindowIcon(QtGui.QIcon(
        path.join(currentDir, "icons/Puzzlestream.png")))
    for f in listdir(path.join(currentDir, "fonts")):
        QtGui.QFontDatabase.addApplicationFont(
            path.join(currentDir, "fonts", f))
    font = QtGui.QFont("Roboto", pointSize=10)
    font.setStyleStrategy(QtGui.QFont.PreferAntialias)
    app.setFont(font)
    return app


def launchPuzzlestream():
    """Create application and MainWindow for Puzzlestream."""

    global app, psMainWindow

    app = initApp()

    app.setApplicationName("Puzzlestream")
    app.setApplicationDisplayName("Puzzlestream")

    splash_pix = QtGui.QPixmap(
        path.join(path.dirname(__file__), "icons/Puzzlestream.png"))

    desktopWidget = app.desktop()
    desktopGeometry = desktopWidget.screenGeometry()
    splash_pix = splash_pix.scaled(
        0.5*splash_pix.width()*desktopGeometry.width()/1080,
        0.5*splash_pix.height()*desktopGeometry.width()/1080,
        transformMode=QtCore.Qt.SmoothTransformation)
    splash = QtWidgets.QSplashScreen(
        splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(
        QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
    splash.show()
    app.processEvents()
    from puzzlestream.ui.main import PSMainWindow
    psMainWindow = PSMainWindow()
    splash.finish(psMainWindow)
    return app.exec_()


def launchPSViewer(path=None):
    """Create application and MainWindow for Puzzlestream Viewer."""
    global app, psViewerMainWindow

    app = initApp()

    app.setApplicationName("Puzzlestream Viewer")
    app.setApplicationDisplayName("Puzzlestream Viewer")

    from puzzlestream.ui.viewer import PSVMainWindow
    psViewerMainWindow = PSVMainWindow(path=path)

    return app.exec_()


if __name__ == "__main__":
    setStdout()
    sys.exit(launchPuzzlestream())
