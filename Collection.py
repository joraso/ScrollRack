# -*- coding: utf-8 -*-
"""
Created on Sat Sep 18 17:58:16 2021

This module defines the core 'Collection' object, A subclass of the Pandas
DataFrame object used as ScrollRack's primary tool for creating and
manipulating lists of M:tG cards.

@author: Joe Raso
"""

import pandas as pd
from Search import ScryfallPortal

# See https://pandas.pydata.org/docs/reference/frame.html
class Collection(pd.DataFrame):
    """The core object of ScrollRack - a collection is a named list of cards,
    that may represent a deck, the contents of a binder or box, etc."""
    def __init__(self, *args, fpath=None, **kwargs):
        # Fix columns to the currently in-use card properties
        kwargs['columns'] = ['Sel', 'Name', 'Cost', 'Set', 'Rarity', 'MV',
            'Color', 'Released']
        super().__init__(*args, **kwargs)
        self.fpath = fpath
        # Needs a name member for certain operations, based on the file path,
        # if one is provided.
        if self.fpath:
            self.name = (self.fpath.split("/")[-1]).split(".")[0]
        else: self.name = "Unnamed"
        # set column indicating selection status to False
        self.Sel = False
        # set any blank values to an empty string
        self.fillna("", inplace=True)
        
    # Editing Functionality ===================================================
    def copy_selected(self):
        """Returns a Collection containing a copy of the cards selected."""
        data = self[self["Sel"]==True].copy()
        return Collection(data) # re-initialize as a collection
    def drop_selected(self):
        """Drops the selected cards from the Collection in place."""
        self.drop(self.index[self["Sel"]==True], inplace=True)
    def add_cards(self, collection):
        """Adds the cards from another Collection to this one."""
        combined = pd.concat([self, collection], axis=0).reset_index()
        self.__init__(combined, fpath=self.fpath)
    def sort_by(self, column, ascending=True):
        """Sorts the Collection in place by the (single) specified card
        property."""
        if column == "Set": # Sorting by set = sorting by release date
            self.sort_values(["Released"], ascending=ascending, inplace=True)
        if column == "Rarity": # Sorting by rarity requires a key
            def rarity_key(column):
                codes = {"C":0, "U":1, "R":2, "M":3}; return column.map(codes)
            self.sort_values([column], ascending=ascending, inplace=True,
                             key=rarity_key)
        else: # Default to normal sorting for undefined columns
            self.sort_values([column], ascending=ascending, inplace=True)
        self.reset_index(drop=True, inplace=True)
        
    # Save/load functionality =================================================
    def save(self, fpath=None):
        """Saves the collection as a ';' delimited csv file to the provided
        location and updates the name of the collection accordingly. If a new
        location is not provided, defaults to using the Collection's already
        associated fpath. (If neither is set, nothing happens.)"""
        if fpath: # If a new fpath is given, update collection fpath and name
            self.fpath = fpath
            self.name = (self.fpath.split("/")[-1]).split(".")[0]
        if self.fpath:
            # Drop selection status column before saving
            data = self.drop(columns=['Sel'])
            data.to_csv(self.fpath, index=False, sep=';')
        # If neither exists, print a warning to stdout
        # (may replace with an actual warning or exception later)
        else: print(f"Warning: Collection {self.name} can't be saved - "+\
            "no file path specified.")
    def reload(self):
        """Reloads the collection data from its associated file lococation
        (replacing the current data)."""
        if self.fpath:
            data = pd.read_csv(self.fpath, sep=';')
            self.__init__(data, fpath=self.fpath)
    @classmethod
    def from_file(cls, fpath):
        """Loads a new collection object from a csv file."""
        data = pd.read_csv(fpath, sep=';')
        return cls(data, fpath=fpath)
        
    # Scryfall Connectors =====================================================
    @classmethod
    def from_search(cls, query, name="Search results"):
        """Creates a Collection from the results of a Scryfall search with the
        given query. For query syntax see https://scryfall.com/docs/syntax."""
        # Perform the search using the Scryfall portal object.
        portal = ScryfallPortal(); data = portal.search(query)
        results = cls(data, fpath=None); results.name = "Search Results"
        return results

if __name__ == "__main__":
    
    test = Collection.from_file("Library/SampleCollection.csv")