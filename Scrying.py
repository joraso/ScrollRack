# -*- coding: utf-8 -*-
"""
Created on Sat Oct  2 12:52:09 2021

This module contains the functions used to interface with Scryfall's API for
pulling card information from their online database.

@author: Joe Raso
"""

import json, time, requests
from Collection import Collection

class SearchPortal:
    """Generic search engine object for inerfacing with web-based M:tg
    database APIs."""
    
class Scryfall(SearchPortal):
    """Search engine that connects to https://scryfall.com/ for card 
    information and searches."""
    def __init__(self):
        self.searchpath = 'https://api.scryfall.com/cards/search'
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
        """Returns the results of a Scryfall Search. For query syntax see
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
            print("Warning: Some cards were not pulled, maxcards reached.")
        # Format the restults into a collection:
        return Collection.from_scryfall(data)    
        
if __name__ == '__main__':
    
    portal = Scryfall()
    test = portal.search('!"Intet, the Dreamer" include:extras')
    test2 = portal.search('t:goblin lang:en')