# ScrollRack
ScrollRack is an open-source, python-based Magic: the Gathering card inventory manager, designed with the individual card collector (i.e. me) in mind.

## Features
- Scroll Rack's primary functionality is the **Collection** objects built off of Pandas DataFrames. These are catalogs of cards which may represent a deck, the contents of a binder or box, etc. The collection object is meant to be command-line friendly for manipulation for sorting and analysis that is painless and fluid.
- Collections by default set their first column as a boolean selection column, allowing cards to be individually selected and grouped. The collection object uses this column in it's shorthand functions to drop all the selected cards or create a new Collection from them.
- Collections can be save/loaded as any Pandas DataFrame, but also have shorthand save/reload/from_file methods that store them as semicolon-delimited CSV files, hopefully making them easy to access and modify by other means. (Commas are too common in card names to be used as delimiters.)
- ScrollRack interfaces with Scryfall's search API, giving it the ability to generate Collections from the results of a search.
- ScrollRack also incorporates a GUI Built in PyQt5 for handling collections, which currently supports a full(ish) range of Collection editing capabilities, including pulling lists of cards from Scryfall. More improvements here coming soon.

## Planned Features
- Legit documentation (hahaha).
- Library management --- the ability to search and analyze all cards across multiple Collections stored.
- Tracking quantity, condition and current market price of cards in a collection.
- Efficiently updating or correcting card information (especially prices) in a Collection from Scryfall.
- Ability to import/export to other common formats of M:tG card lists, such as TappedOut lists and .dec files.
- Deckbuilding and financial analysis toolkits.
