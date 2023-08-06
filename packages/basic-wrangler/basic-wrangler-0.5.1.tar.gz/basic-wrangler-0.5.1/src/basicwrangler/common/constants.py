""" This module contains constants accessed by other modules. """

RE_QUOTES = r'(?=([^"]*"[^"]*")*[^"]*$)'  # this selects things NOT inside quotes
NO_TOKENIZER = [
    "generic",
    "freebasic",
    "qbasic",
    "gwbasic",
    "riscos",
    "amiga",
    "gsoft",
    "cpc",
    "adam",
    "msx",
    "oric",
    "bbc",
]
