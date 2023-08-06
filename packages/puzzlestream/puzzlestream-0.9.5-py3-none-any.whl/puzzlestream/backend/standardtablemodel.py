# -*- coding: utf-8 -*-
"""Standard table model module.

contains PSStandardTableModel
"""

import numpy as np
import pandas as pd
from puzzlestream.ui.tableplot import PSTablePlot
from PyQt5 import QtCore


class PSStandardTableModel(QtCore.QAbstractTableModel):

    """Standard table model class used in PSDataView.

    This class adds some functions to the standard Qt abstract table model;
    the most significant ones are the handling of separate columns, which are
    added, accessed and deleted using addColumn, getColumn and deleteColumn.
    For each column a pyqtgraph plot widget can be requested using
    getPlotWidget. getItemAt is necessary to have a unified way of accessing
    data when using PSStandardTableModel and PSNumpyModel2D at the same time.
    """

    def __init__(self, parent: QtCore.QObject = None):
        """PSStandardTableModel init.

        Args:
            parent (QtWidget): Qt parent
        """
        super().__init__(parent)
        self.__keys, self.__data = [], []
        self.createKeyList()

    @property
    def modelData(self) -> list:
        return self.__data

    def createKeyList(self):
        """Recreates key list (each key represents one column)."""
        keys = []

        for key in self.__data:
            if ((isinstance(self.__data[key], np.ndarray) or
                 isinstance(self.__data[key], pd.Series)) and
                    len(self.__data[key].shape) == 1):
                keys.append(key)

        self.__keys = sorted(keys)

    @property
    def keys(self) -> list:
        """Column names, used as a header (list)."""
        return self.__keys

    def addColumn(self, key: str, data: np.ndarray):
        """Add a column to the model.

        Args:
            key (str): Name of the column.
            data (1D numpy array): Column data.
        """
        self.__keys.append(key)
        self.__keys.sort()
        self.__data.insert(self.__keys.index(key), data)

    def deleteColumn(self, key: str):
        """Delete column from the model.

        Args:
            key (str): name of the column.
        """
        index = self.__keys.index(key)
        del self.__keys[index], self.__data[index]

    def getColumn(self, index):
        """Get data of a specific column.

        Args:
            index (str, int): Name or index of the column.
        Returns:
            column data (1D numpy array).
        """
        if isinstance(index, str):
            return self.__data[index]
        else:
            index = self.__keys.index(index)
            return self.__data[index]

    def getPlotWidget(self, column: str):
        """Create and return pyqtgraph plot widget for a specific column.

        Args:
            column (str): Name of the column.
        Returns:
            pyqtgraph widget, displaying a spark line of the data (QWidget).
        """
        data = self.__data[column]

        try:
            if data.dtype in [int, float, np.int32, np.int64, np.float32,
                              np.float64, "int32", "int64", "float32",
                              "float64"]:
                return PSTablePlot(data)
        except Exception as e:
            print(e)
        return None

    def rowCount(self, parent: QtCore.QObject = None) -> int:
        """Number of rows."""
        counts = [len(item) for item in self.__data]
        if len(counts) > 0:
            return max(counts) + 1
        return 0

    def columnCount(self, parent: QtCore.QObject = None) -> int:
        """Number of columns."""
        return len(self.keys)

    def data(self, index: QtCore.QModelIndex, role=QtCore.Qt.DisplayRole):
        """Return data at index as QVariant.

        Args:
            index (QModelIndex): Index the data is needed at.
            role (Qt role): Qt.DisplayRole or Qt.EditRole

        Returns:
            data at index (QVariant).
        """
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                row = index.row()
                col = index.column()
                if row > 0 and row < len(self.__data[col]) + 1:
                    return QtCore.QVariant(str(self.getItemAt(row, col)))
        return QtCore.QVariant()

    def getItemAt(self, row: int, column: int):
        """Unified way of directly accessing data at specific index.

        Args:
            row, column (int): Index.
        Returns:
            data at index
        """
        if row - 1 < len(self.__data[column]) and row - 1 >= 0:
            return self.__data[column][row - 1]
        return None

    def headerData(self, section: int, orientation,
                   role=QtCore.Qt.DisplayRole) -> QtCore.QVariant:
        """Return header data for given section.

        Args:
            section (int): Index of the section.
            orientation: Qt.Horizontal or Qt.Vertical.
            role: Qt.DisplayRolw or Qt.EditRole.
        Returns:
            section title (horizontal) or section number (vertical) (QVariant)
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section < len(self.__keys):
                    return QtCore.QVariant(self.__keys[section])
            else:
                if section > 0:
                    return QtCore.QVariant(section - 1)
        return QtCore.QVariant()
