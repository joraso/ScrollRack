# -*- coding: utf-8 -*-
"""
Created on Sat Oct  2 12:52:09 2021

This module contains the ScryfallPortal object used by Collections to interface
with Scryfall's API and pull card information from their online database.

@author: Joe Raso
"""

import json, time, requests
import pandas as pd

class ScryfallPortal:
    """Search engine that connects to the Scryfall API (https://scryfall.com/)
    to retrieve card information and searches."""
    def __init__(self):
        self.searchpath = 'https://api.scryfall.com/cards/search'
    def format_result(self, data):
        """Formats a the results of a Scryfall search (a json list of
        dictionaries) into a Collection-compatible DataFrame."""
        data = pd.DataFrame.from_dict(data)
        # Retrieve and rename the columns expected by the collection object.
        scrynames = {'name':'Name', 'mana_cost':'Cost', 'set':'Set',
            'rarity':'Rarity'}
        data = data[list(scrynames.keys())]
        data.rename(columns=scrynames, inplace=True)
        # Rarity column needs to be remapped to one-letter codes
        rarities = {'mythic':'M', 'rare':'R', 'uncommon':'U', 'common':'C'}
        data.replace({'Rarity':rarities}, inplace=True)
        # Set abbreviations should be capatalized
        data['Set'] = data['Set'].apply(str.upper)
        return data
    def request(self, uri, **kwargs):
        """Makes a request from Scryfall's API at the specified uri, and
        returns the results as a dictionary. Any keywords included here are
        passed to requests.get()."""
        # Scryfall's docs (https://scryfall.com/docs/api), request that a
        # 50-100 millisecond delay be inserted between requests sent to the
        # server. We add 200ms, 2x the requested amount just to be safe.
        time.sleep(0.2)
        req = requests.get(uri, **kwargs)
        return req.json()
    def search(self, query, maxcards=1000):
        """Returns the results of a Scryfall search. For query syntax see
        https://scryfall.com/docs/syntax. The maxcards keyword is used to
        ensure that the amount of data pulled does not overload memory."""
        # Pull the first page of search results from the scryfall API:
        js = self.request(self.searchpath, params={'q':query})
        data = js['data']; ncards = len(data)
        # Pull from the next pages in the list while there are more pages AND
        # the maximum number of cards has not been reached:
        while ('next_page' in js.keys()) and (ncards < maxcards):
            # request the next_page using the provided uri:
            js = self.request(js['next_page'])
            # concatenate into the data and recount the number of cards:
            data += js['data']; ncards = len(data)
        # Throw a warning if the above loop terminated due maxing out cards:
        if ('next_page' in js.keys()):
            print("Warning: Some cards were not pulled --- maxcards reached.")
        # Format the restults into to pass to the Collection:
        return self.format_result(data)
        
if __name__ == '__main__':
    
    portal = Scryfall()
    test = portal.search('!"Intet, the Dreamer" unique:prints')