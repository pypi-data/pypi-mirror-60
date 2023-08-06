""" This module contains functions to generate lexers. """

import logging
import sys
from pathlib import Path

import yaml

import basicwrangler.lex.lexer as lexer

# This is needed to find files when running with pyinstaller.
if hasattr(sys, "_MEIPASS"):
    SCRIPT_DIR = Path.joinpath(Path(sys._MEIPASS).resolve(), "lex")  # type: ignore # pylint: disable=no-member
else:
    SCRIPT_DIR = Path(__file__).resolve().parent


def generate_splitter():
    """ Loads the splitting regex from the file. """
    yaml_path = Path.joinpath(SCRIPT_DIR, "rules.yaml")
    with open(yaml_path) as yaml_file:
        yaml_dict = yaml.safe_load(yaml_file)
    split_string = yaml_dict["split"]
    return split_string


def generate_label_lexer(basic_type):
    """ Generates a lexer for converting to labelled format. """
    regex_dict_order = [
        "LINE",
        "KEYWORDS",
        "FLOW",
        "NUMBER",
        "COMMENT",
        "DATA",
        "LET",
        "ID",
        "STATEMENT",
        "STRING",
        "PRINT",
        "PUNCTUATION",
    ]
    yaml_path = Path.joinpath(SCRIPT_DIR, "rules.yaml")
    with open(yaml_path) as yaml_file:
        yaml_dict = yaml.safe_load(yaml_file)
    regex_dict = yaml_dict[basic_type]
    rules = list()
    for key in regex_dict_order:
        temp_tuple = (regex_dict[key], key)
        rules.append(temp_tuple)
    logging.debug(rules)
    if basic_type.startswith("cbm"):
        lx = lexer.Lexer(rules, skip_whitespace=True, ignore_case=True)
    else:
        lx = lexer.Lexer(rules, skip_whitespace=True)
    return lx
