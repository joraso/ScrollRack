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
        # Auto-find the index of columns the model needs to treat specially
        self.selectioncolumn = self.collection.columns.get_loc('Sel')
        self.manacolumn = self.collection.columns.get_loc('Cost')
        # Keep a master list of the editable columns
        self.editable = [self.selectioncolumn]
        
    # Mandatory reimplementations for a table model ===========================
    def data(self, index, role):
        # The 'Cost' column has an image as decoration role, no display role
        if index.column()==self.manacolumn:
            if role==QtCore.Qt.DecorationRole:
                return self.parseManaCost(index)
        # The selection column has a checked state, no display role
        elif index.column()==self.selectioncolumn:
            if role==QtCore.Qt.CheckStateRole:
                if self.collection.iloc[index.row(), index.column()]:
                    return QtCore.Qt.Checked
                else: return QtCore.Qt.Unchecked
        # For all other columns, default to collection content as display role
        elif role==QtCore.Qt.DisplayRole:
            return str(self.collection.iloc[index.row(), index.column()])        
    def rowCount(self, index):
        return len(self.collection)
    def columnCount(self, index):
        return len(self.collection.columns)
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        # Display the column names in the horizontal header
        if orientation == QtCore.Qt.Horizontal:
            if section == self.selectioncolumn:
                if role == QtCore.Qt.CheckStateRole:
                    return QtCore.Qt.Checked
            elif role == QtCore.Qt.DisplayRole:
                return self.collection.columns[section]
        # Note: no vertical header - it's ugly
        
    # Mandatory reimplementations for an editable table =======================
    def flags(self, index):
        # The editable columns need to be flagged as such
        if index.column() in self.editable:
            return (super().flags(index) | QtCore.Qt.ItemIsEditable)
        # Otherwise go to the parent definition
        else: return super().flags(index)
    def setData(self, index, value, role):
        # Define how values are translated to bool for the selection column
        if index.column() == self.selectioncolumn:
            if value==0:
                self.collection.iloc[index.row(),index.column()] = False
            else: self.collection.iloc[index.row(),index.column()] = True
            self.layoutChanged.emit()
            return True
        return False
            
    # Nonstandard functions ===================================================
    def parseManaCost(self, index, symbol_size=15):
        """Retrieves the mana cost from the card at (index) and returns a
        QImage of the cost to display."""
        # Retriving and parsing the mana cost string into a list of filenames
        cost_string = self.collection.iloc[index.row(), self.manacolumn]
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
    columnWidths = {"Sel":22, "Name":200, "Cost":60, "Set":50, "Rarity":50,
                    "MV":50, "Color":50, "Released":100}
    def __init__(self, collection, *args, fname=None, **kwargs):
        super().__init__(*args, **kwargs)
        # create and set the collection model.
        self.setModel(CollectionModel(collection))
        # Set selection behavior to whole rows at a time
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # Set the minimum horizontal section size to small
        self.horizontalHeader().setMinimumSectionSize(20)
        # Set the view column widths according to defaults
        columns = self.model().collection.columns
        for c in range(len(columns)):
            if columns[c] in self.columnWidths.keys():
                self.setColumnWidth(c, self.columnWidths[columns[c]])
        # Connect the on-click functionality
        self.clicked.connect(self.onClick)
    def onClick(self):
        """Defines what happens when the table is clicked."""
        index = self.selectionModel().currentIndex()
        # if the index is the selection column, toggle it's value
        if index.column() == self.model().selectioncolumn:
            if self.model().collection.iloc[index.row(), index.column()]:
                self.model().setData(index, 0, QtCore.Qt.CheckStateRole)
            else: self.model().setData(index, 1, QtCore.Qt.CheckStateRole)
            
            
class MainWindow(QtWidgets.QMainWindow):
    """The main GUI window. Collections are opened in tabs, with a toolbar
    along the top of the window for navigation."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("ScrollRack")
        self.setGeometry(100,100,800,500)
        # Setting up the tab space in the central window
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        self.setCentralWidget(self.tabs)
        # Add the top tool bar.
        self.generateToolBar(); self.generateSearchBar()
    
    # Toolbar and Searchbar generators ========================================
    def generateToolBar(self):
        """Initializes the toolbar at the top of the window."""
        self.toolbar = QtWidgets.QToolBar()
        # Add simple bottun items Open/Save/New/Scryfall
        self.toolbar.addAction("Open", self.openTab)
        self.toolbar.addAction("New", self.newTab)
        self.toolbar.addAction("Scryfall", lambda:
            self.searchbar.setHidden(False))
        self.toolbar.addAction("Save", self.saveTab)
        self.toolbar.addAction("Save as", self.saveAsTab)
        self.toolbar.addSeparator()
        self.toolbar.addAction("Drop", self.dropSelected)
        # Adding the dropdown menu for 'Copy To' and 'Move To'
        self.copytoMenu = QtWidgets.QMenu("Copy To")
        self.copytoMenu.aboutToShow.connect(self.generateCopyToMenu)
        self.toolbar.addAction(self.copytoMenu.menuAction())
        self.movetoMenu = QtWidgets.QMenu("Move To")
        self.movetoMenu.aboutToShow.connect(self.generateMoveToMenu)
        self.toolbar.addAction(self.movetoMenu.menuAction())
        # Add the toolbar to the main window
        self.addToolBar(self.toolbar)
    def generateSearchBar(self):
        """Initializes a search bar at the bottom of the window."""
        layout = QtWidgets.QHBoxLayout()
        # Generate the line-edit for entering search queries
        self.searchfield = QtWidgets.QLineEdit()
        self.searchfield.returnPressed.connect(self.openSearch)
        layout.addWidget(self.searchfield)
        # Generate the search pushbutton
        searchbutton = QtWidgets.QPushButton("Search")
        searchbutton.clicked.connect(self.openSearch)
        layout.addWidget(searchbutton)
        # Wrap in a DockWidget
        searchwidget = QtWidgets.QWidget()
        searchwidget.setLayout(layout)
        self.searchbar = QtWidgets.QDockWidget()
        self.searchbar.setWidget(searchwidget)
        self.searchbar.setWindowTitle("Enter Scryfall query:")
        # Default to hidden upon initialization
        self.searchbar.setHidden(True)
        # Add the seachbar to the main window
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.searchbar)
    
    # Tab/file manipulation functions =========================================
    def openSearch(self):
        """Opens a new collection tab containing search results."""
        view = CollectionView(Collection.from_search(self.searchfield.text()))
        self.tabs.addTab(view, view.model().collection.name)
        self.searchbar.setHidden(True) # re-hide the search bar
    def newTab(self):
        """Opens a blank collection tab."""
        # Must initialize a blank collection to pass to the model/view
        view = CollectionView(Collection())
        self.tabs.addTab(view, view.model().collection.name)
    def openTab(self):
        """Opens a new tab with a collection from file."""
        fpath_tuple = QtWidgets.QFileDialog.getOpenFileName(
            directory='Library/')
        if fpath_tuple[0]:
            collection = Collection.from_file(fpath_tuple[0])
            view = CollectionView(collection)
            self.tabs.addTab(view, collection.name)
    def closeTab(self, currentIndex):
        """Closes a tab."""
        self.tabs.removeTab(currentIndex)
    def saveTab(self):
        """Saves the currently selected collection to file if it has an an
        associated file path. Otherwise prompts 'Save As'."""
        thisTab = self.tabs.currentIndex()
        # Only do something if the focus is currently on a tab
        if thisTab > -1:
            collection = self.tabs.widget(thisTab).model().collection
            if collection.fpath: collection.save()
            else: self.saveAsTab()
    def saveAsTab(self):
        """Saves the currently selected collection to file."""
        thisTab = self.tabs.currentIndex()
        # Only do something if the focus is currently on a tab
        if thisTab > -1:
            collection = self.tabs.widget(thisTab).model().collection
            fpath_tuple = QtWidgets.QFileDialog.getSaveFileName(
                caption="Save As", directory=f"Library/{collection.name}.csv")
            # Proceed to saving if a filepath was specified
            if fpath_tuple[0]:
                collection.save(fpath_tuple[0])
                # Update the tab with the newly saved collection name
                self.tabs.setTabText(thisTab, collection.name)
        
        
    # Collection editing functionalities ======================================
    def dropSelected(self):
        """Drops the selected cards from the current Collection."""
        mod = self.tabs.widget(self.tabs.currentIndex()).model()
        mod.collection.drop_selected(); mod.layoutChanged.emit()
    def generateCopyToMenu(self):
        """Generates/regenerates the dropdown menu of currently open tabs to
        copy selected cards to."""
        self.copytoMenu.clear() # Clear the current menu
        sourceIndex = self.tabs.currentIndex()
        def generate_copyto(destIndex):
            # Generates a copy to function for each source/destination.
            source = self.tabs.widget(sourceIndex).model()
            dest = self.tabs.widget(destIndex).model()
            def copyto():
                # Perform the copy to operation
                cards = source.collection.copy_selected()
                dest.collection.add_cards(cards)
                # Update the view of both models
                dest.layoutChanged.emit(); source.layoutChanged.emit()
            return copyto
        # Iterate through open tabs and add them to the list
        for i in range(self.tabs.count()):
            if i != sourceIndex:
                tabname = self.tabs.widget(i).model().collection.name
                self.copytoMenu.addAction(tabname, generate_copyto(i))
        # Copying to the current tab is treated separately
        self.copytoMenu.addSeparator()
        self.copytoMenu.addAction("Here", generate_copyto(sourceIndex))
    def generateMoveToMenu(self):
        """Generates/regenerates the dropdown menu of currently open tabs to
        move selected cards to."""
        self.movetoMenu.clear() # Clear the current menu
        sourceIndex = self.tabs.currentIndex()
        def generate_moveto(destIndex):
            # Generates a move to function for each source/destination.
            source = self.tabs.widget(sourceIndex).model()
            dest = self.tabs.widget(destIndex).model()
            def moveto():
                # Perform the move to operation
                cards = source.collection.copy_selected()
                dest.collection.add_cards(cards)
                # The key difference between copy and move:
                source.collection.drop_selected() 
                # Update the view of both models
                dest.layoutChanged.emit(); source.layoutChanged.emit()
            return moveto
        # Note: 'move to' provides no option to move to the source list
        for i in range(self.tabs.count()):
            if i != sourceIndex:
                tabname = self.tabs.widget(i).model().collection.name
                self.movetoMenu.addAction(tabname, generate_moveto(i))
        
        
if __name__ == '__main__':
    
    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()
    app.exec()
    
    # After closing the window, grab a few handles for debugging
    view = win.tabs.widget(0)
    mod = view.model()
    col = mod.collection