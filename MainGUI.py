# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 17:56:24 2021

This module contains the main GUI interface --- the model and view objects for
collections as well as the main window.

@author: Joe Raso
"""

from Collection import Collection
from PyQt5 import QtWidgets, QtCore, QtGui, QtSvg

class CollectionModel(QtCore.QAbstractTableModel):
    """The model for GUI interface with a collection object."""
    def __init__(self, collection, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collection = collection
    def data(self, index, role):
        # By defaul display the contents of the collection as a string
        if role == QtCore.Qt.DisplayRole and index.column() != 1:
            return str(self.collection.iloc[index.row(), index.column()])
        # For the 'Cost' column, include no display role, and instead put the
        # cost image as decoation role.
        if role == QtCore.Qt.DecorationRole and index.column() == 1:
            return self.parseManaCost(index)
    def rowCount(self, index):
        return len(self.collection)
    def columnCount(self, index):
        return len(self.collection.columns)
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and \
            role == QtCore.Qt.DisplayRole:
            return self.collection.columns[section]
        # In every other case, return the parent call
        return super().headerData(section, orientation, role)
    # Nonstandard functions ===================================================
    def parseManaCost(self, index, symbol_size=15):
        """Retrieves the mana cost from the card at (index) and returns a
        QImage of the cost to display."""
        # Retriving and parsing the mana cost string into a list of filenames
        cost_string = self.collection.iloc[index.row(), 1]
        cost_string = cost_string.replace('/','') # for hybrid/phyrex. mana
        symbols = cost_string[1:-1].split('}{')
        # Generate the cost image and painter object
        imgformat = QtGui.QImage.Format_ARGB32
        image = QtGui.QImage(symbol_size*len(symbols), symbol_size, imgformat)
        image.fill(0) # Fills in a white background
        painter = QtGui.QPainter(image); loc=0
        # render symbols from their individual files and add them to the image
        for sym in symbols:
            renderer = QtSvg.QSvgRenderer(f'images/mana-symbols/{sym}.svg')
            area = QtCore.QRectF(loc, 0, symbol_size, symbol_size)
            renderer.render(painter, area)
            loc += symbol_size
        return image
        
        
class CollectionView(QtWidgets.QTableView):
    """The view object for GUI interface with a model/collection."""
    # Class variable that dictates the appropriate width of columns
    columnWidths = {"Name":200, "Cost":60, "Set":50, "Rarity":50}
    def __init__(self, collection, *args, fname=None, **kwargs):
        super().__init__(*args, **kwargs)
        # create and set the collection model.
        self.setModel(CollectionModel(collection))
        # Set selection behavior to whole rows at a time
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # Set the view column widths according to defaults
        columns = self.model().collection.columns
        for c in range(len(columns)):
            if columns[c] in self.columnWidths.keys():
                self.setColumnWidth(c, self.columnWidths[columns[c]])
        
class MainWindow(QtWidgets.QMainWindow):
    """The main GUI window. Collections are opened in tabs, with a toolbar
    along the top of the window for navigation."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Scroll Rack")
        self.setGeometry(100,100,1000,500)
        # Setting up the tab space in the central window
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        self.setCentralWidget(self.tabs)
        # Add the top tool bar.
        self.addToolBar(self.toolBar())
    def toolBar(self):
        """Initializes the toolbar at the top of the window."""
        self.toolbar = QtWidgets.QToolBar()
        self.openButton = self.toolbar.addAction("Open", self.openTab)
        self.newButton = self.toolbar.addAction("New", self.newTab)
        return self.toolbar
    def newTab(self):
        """Opens a blank collection tab."""
        # Must initialize a blank collection to pass to the model/view
        view = CollectionView(Collection())
        self.tabs.addTab(view, view.model().collection.name)
    def openTab(self):
        """Opens a new tab with a collection from file."""
        fpath_tuple = QtWidgets.QFileDialog.getOpenFileName()
        if fpath_tuple[0]:
            # Note that the collection model expects a name without the 
            # file suffix, so we have to strip that out
            name = fpath_tuple[0].split('/')[-1][:-4]
            collection = Collection(name=name)
            collection.load()
            view = CollectionView(collection)
            self.tabs.addTab(view, name)
    def closeTab(self, currentIndex):
        """Closes a tab."""
        self.tabs.removeTab(currentIndex)
        
if __name__ == '__main__':
    
    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()
    app.exec()
    
    