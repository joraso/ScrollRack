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
    def __init__(self, *args, name=None, **kwargs):
        # Fix columns to the currently in-use card properties
        kwargs['columns'] = ['Sel', 'Name', 'Cost', 'Set', 'Rarity']
        super().__init__(*args, **kwargs)
        # Needs a name member for certain operations
        self.name = name if name else "Unnamed"
        # set column indicating selection status to False
        self.Sel = False
    def load(self):
        """Loads the collection data from the Library folder."""
        fpath = 'Library/'+self.name+'.csv'
        data = pd.read_csv(fpath, sep=';')
        self.__init__(data, name=self.name)
    def save(self):
        """Saves the collection as a ';' delimited csv file in the Library
        folder under the name of the collection."""
        # Drop selection status column before saving
        data = self.drop(columns=['Sel'])
        fpath = 'Library/'+self.name+'.csv'
        data.to_csv(fpath, index=False, sep=';')
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
        self.__init__(combined, name=self.name)
        
    # Scryfall Connectors =====================================================
    @classmethod
    def from_search(cls, query, name="Search results"):
        """Creates a Collection from the results of a Scryfall search with the
        given query. For query syntax see https://scryfall.com/docs/syntax."""
        # Perform the search using the Scryfall portal object.
        portal = ScryfallPortal(); data = portal.search(query)
        return cls(data, name=name)

if __name__ == "__main__":
    
    test = Collection(name="SampleCollection")
    test.load()
    test.iloc[3:7,0]=True
    test2 = test.copy_selected()
    test.drop_selected()
    test3 = Collection.from_search("t:ouphe")
    test.add_cards(test3)