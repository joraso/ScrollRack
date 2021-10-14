# ScrollRack
ScrollRack is an open-source, python-based Magic: the Gathering card inventory manager, designed with the individual card collector in mind.

## Features
- Scroll Rack's primary functionality is building and maintaining **Collection** objects --- catalogs of cards which may represent a deck, the contents of a binder or box, etc. The Collection object itself is built off of Pandas DataFrames, making command-line manipulation for sorting and analysis painless and fluid.
- Collections contain save/load methods that store them as semicolon-delimited CSV files in a 'Library' folder, making them easy to access and modify by other programs.
- ScrollRack also interfaces with Scryfall's search API, giving it the capability to generate Collections from the results of a search.
- Finally, ScrollRack incorporates a (currently limited) GUI interface for managing Collections, built in PyQt5.

## Planned Features
- Library management --- the ability to search and analyze all cards in all Collections stored in a library.
- Tracking quantity, condition and current market price of cards in a collection.
- Update or correct card information (especially prices) in a Collection from Scryfall.
- Ability to import/export to other common formats of M:tG card lists, such as TappedOut lists and .dec files.
- Deckbuilding and financial analysis toolkits.
