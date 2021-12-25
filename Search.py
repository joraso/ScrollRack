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
        # Unpack neccessary charactoristics for double-faced cards
        if 'card_faces' in data.columns:
            subset = data[data.card_faces.isnull()==False]
            faces = pd.DataFrame(subset.card_faces.to_list(), index=subset.index)
            front = pd.json_normalize(faces.loc[:,0]).set_index(faces.index)
            back = pd.json_normalize(faces.loc[:,1]).set_index(faces.index)
            # Mana cost (and name) are given for both faces
            subset.loc[:,'mana_cost'] = (front.loc[:,'mana_cost'] + ' // ' + 
                back.loc[:,'mana_cost'])
            # Color (and mana volue) are for the front face only
            subset.loc[:,'colors'] = front.loc[:,'colors']
            # These columns need to exist in 'data' if they don't already
            if 'colors' not in data.columns: data['colors'] = ''
            if 'mana_cost' not in data.columns: data['mana_cost'] = ''
            data.update(subset)
        # Rename the columns expected by the collection object.
        scrynames = {'name':'Name', 'mana_cost':'Cost', 'set':'Set',
            'rarity':'Rarity', 'cmc':'MV', 'colors':'Color',
            'released_at':'Released'}
        data = data[list(scrynames.keys())].copy()
        data.rename(columns=scrynames, inplace=True)
        # Remap rarity column to one-letter codes
        rarities = {'mythic':'M', 'rare':'R', 'uncommon':'U', 'common':'C'}
        data.replace({'Rarity':rarities}, inplace=True)
        # Set abbreviations should be capatalized
        data['Set'] = data['Set'].apply(str.upper)
        # Mana value should be an integer
        data['MV'] = data['MV'].apply(int)
        # Colors should be sorted and joined into a string
        color_order = {'W':0, 'U':1, 'B':2, 'R':3, 'G':4}
        def sort_join_colors(colors):
            colors.sort(key=(lambda c: color_order[c]))
            return "".join(colors)
        data["Color"] = data['Color'].apply(sort_join_colors)
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
    
    portal = ScryfallPortal()
#    test = portal.search('!"Intet, the Dreamer" unique:prints')
    test = portal.search('jadzi')
    # Note: Cost and name displays as both sides. Color and MV are front face only.