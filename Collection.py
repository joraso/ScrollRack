# -*- coding: utf-8 -*-
"""
Created on Sat Sep 18 17:58:16 2021

This module defines the core 'Collection' object, A subclass of the Pandas
DataFrame object used as ScrollRack's primary tool for creating and
manipulating lists of M:tG cards.

@author: Joe Raso
"""

import pandas as pd
from Scrying import Scryfall

# See https://pandas.pydata.org/docs/reference/frame.html
class Collection(pd.DataFrame):
    """The core object of ScrollRack - a collection is a named list of cards,
    presumed to be physically owned by the user, and may represent a deck, the
    contents of a binder or box, etc."""
    def __init__(self, *args, name=None, **kwargs):
        # Fix columns to the currently in-use card properties
        kwargs['columns'] = ['Name', 'Cost', 'Set', 'Rarity']
        super().__init__(*args, **kwargs)
        # Needs a name member for certain operations
        self.name = name if name else "Unnamed"
    def load(self):
        """Loads the collection data from the Library folder."""
        fpath = 'Library/'+self.name+'.csv'
        data = pd.read_csv(fpath, sep=';')
        self.__init__(data, name=self.name)
    def save(self):
        """Saves the collection as a ';' delimited csv file in the Library
        folder under the name of the collection."""
        fpath = 'Library/'+self.name+'.csv'
        self.to_csv(fpath, index=False, sep=';')
        
    # Format converters =======================================================
    @classmethod
    def from_search(cls, query, name="Search results"):
        """Creates a Collection from the results of a web search."""
        # Perform the search using the Scryfall portal
        portal = Scryfall()
        data = portal.search(query)
        return cls(data, name=name)

if __name__ == "__main__":
    
#    test = Collection(name="SampleCollection")
#    test.load()
    test = Collection.from_search("t:ouphe")