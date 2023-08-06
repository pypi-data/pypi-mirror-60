""" This module contains the routines to convert a numbered listing to a labelled listing. """
# pylint: disable=bad-continuation

import logging
import sys

from basicwrangler.lex.genlex import generate_label_lexer
from basicwrangler.lex.lexer import LexerError


def tokenize_line(Lexer, untokenized_line, line_no):
    """ This function returns an untokenized line as a list of tokens. """
    Lexer.input(untokenized_line)
    token_list = list()
    try:
        for tok in Lexer.tokens():
            logging.debug(tok)
            token_list.append(tok)
    except LexerError as err:
        print("LexerError at position %s in line number %s" % (err.pos, line_no + 1))
    return token_list


def sanity_check_listing(Lexer, numbered_file):
    """ First pass - This function returns a list of all the line numbers in the file. """
    original_line_numbers = list()
    for line_no, line in enumerate(numbered_file):
        tokenized_line = tokenize_line(Lexer, line, line_no)
        if tokenized_line[0].type == "LINE":
            if len(original_line_numbers) == 0:
                original_line_numbers.append(tokenized_line[0].val)
            else:
                if tokenized_line[0].val in original_line_numbers:
                    # Duplicate Line sanity check
                    logging.critical(
                        "Fatal Error! Line number "
                        + tokenized_line[0].val
                        + " is a duplicate!"
                    )
                    sys.exit(1)
                if int(tokenized_line[0].val) < int(original_line_numbers[-1]):
                    # Out of order check.
                    logging.warning(
                        "Line number " + tokenized_line[0].val + " is out of order."
                    )
                original_line_numbers.append(tokenized_line[0].val)
    return original_line_numbers


def extract_jump_targets(Lexer, numbered_file, original_line_numbers):
    """ Second pass - This function returns a set of jump targets. """
    jump_targets = set()
    for line_no, line in enumerate(numbered_file):
        handled = list()
        tokenized_line = tokenize_line(Lexer, line, line_no)
        tokenized_line_length = len(tokenized_line)
        indices = [i for i, x in enumerate(tokenized_line) if x.type == "FLOW"]
        logging.debug(line)
        logging.debug(indices)
        for index in indices:
            if index in handled:
                continue
            if tokenized_line[index].val == "ON":
                if (
                    tokenized_line[index + 1].type == "ID"
                    and tokenized_line[index + 2].type == "FLOW"
                ):
                    on_start_index = index + 2
                    handled.append(on_start_index)
                    for i in range(on_start_index + 1, tokenized_line_length):
                        if tokenized_line[i].type == "NUMBER":
                            target = tokenized_line[i].val
                            logging.debug(target)
                            if target not in original_line_numbers:
                                logging.critical(
                                    "Fatal Error! Attempt to jump to line number "
                                    + target
                                    + " is invalid!"
                                )
                                sys.exit(1)
                            jump_targets.add(target)
                        elif tokenized_line[i].val == ",":
                            continue
            if index + 1 < tokenized_line_length:
                if tokenized_line[index + 1].type == "NUMBER":
                    target = tokenized_line[index + 1].val
                    logging.debug(target)
                    if target not in original_line_numbers:
                        logging.critical(
                            "Fatal Error! Attempt to jump to line number "
                            + target
                            + " is invalid!"
                        )
                        sys.exit(1)
                    jump_targets.add(target)
    logging.debug(jump_targets)
    return jump_targets


def output_basic_listing(Lexer, numbered_file, jump_targets, basic_type):
    """ Final pass - This function returns the labelled BASIC file. """
    labeled_file = ""
    for line_no, line in enumerate(numbered_file):
        set_flow = False
        set_on = False
        tokenized_line = tokenize_line(Lexer, line, line_no)
        tokenized_line_length = len(tokenized_line)
        for index, token in enumerate(tokenized_line):
            current_value = ""
            if token.type == "LINE":
                if token.val in jump_targets:
                    labeled_file = labeled_file + "\n" + "_" + token.val + ":" + "\n"
                    continue
                continue
            if (
                token.type == "STATEMENT"
                and tokenized_line[index + 1].type == "COMMENT"
            ):
                labeled_file = labeled_file + " "
                set_flow = False
                set_on = False
                continue
            if token.type == "STATEMENT":
                labeled_file = labeled_file.rstrip() + "\n"
                set_flow = False
                set_on = False
                continue
            if basic_type.startswith("cbm"):
                # Format into upper-case correctly for CBM BASIC
                if set_on and token.type == "NUMBER":
                    current_value = "_" + token.val
                elif set_flow and not set_on:
                    current_value = "_" + token.val
                    set_flow = False
                elif (
                    token.type == "FLOW"
                    and token.val == "ON"
                    and index + 1 < tokenized_line_length
                    and tokenized_line[index + 1].type == "ID"
                ):
                    set_on = True
                    current_value = token.val.upper()
                elif (
                    token.type == "FLOW"
                    and index + 1 < tokenized_line_length
                    and tokenized_line[index + 1].type == "NUMBER"
                ):
                    set_flow = True
                    current_value = token.val.upper()
                elif token.type == "COMMENT" and token.val.islower():
                    current_value = "'" + token.val[3:].upper()
                elif token.type == "COMMENT":
                    current_value = "'" + token.val[3:]
                elif token.type == "DATA" and token.val.islower():
                    current_value = token.val.upper()
                elif token.type == "DATA":
                    current_value = "DATA" + token.val[4:]
                elif token.type == "STRING" and token.val.islower():
                    current_value = token.val.upper()
                elif token.type == "STRING":
                    current_value = token.val
                elif token.type == "PRINT":
                    current_value = "PRINT"
                else:
                    current_value = token.val.upper()
            else:
                if set_on and token.type == "NUMBER":
                    current_value = "_" + token.val
                elif set_flow and not set_on:
                    current_value = "_" + token.val
                    set_flow = False
                elif (
                    token.type == "FLOW"
                    and token.val == "ON"
                    and index + 1 < tokenized_line_length
                    and tokenized_line[index + 1].type == "ID"
                ):
                    set_on = True
                    current_value = token.val
                elif (
                    token.type == "FLOW"
                    and index + 1 < tokenized_line_length
                    and tokenized_line[index + 1].type == "NUMBER"
                ):
                    set_flow = True
                    current_value = token.val
                elif token.type == "COMMENT":
                    current_value = "'" + token.val[3:]
                elif token.type == "PRINT":
                    current_value = "PRINT"
                else:
                    current_value = token.val
            labeled_file = labeled_file + current_value
            if index + 1 < tokenized_line_length:
                if (
                    not token.type == "PUNCTUATION"
                    and not tokenized_line[index + 1].type == "PUNCTUATION"
                    and not token.type == "STATEMENT"
                ):
                    labeled_file = labeled_file + " "
                # The following elif is not redundant. It fixes formatting errors.
                elif (
                    tokenized_line[index + 1].type == "FLOW"
                    and not token.type == "STATEMENT"
                ):
                    labeled_file = labeled_file + " "
        labeled_file = labeled_file + "\n"
    return labeled_file


def label_listing(numbered_file, basic_type):
    """ This function returns a labeled BASIC listing. """
    Lexer = generate_label_lexer(basic_type)
    original_line_numbers = sanity_check_listing(Lexer, numbered_file)
    jump_targets = extract_jump_targets(Lexer, numbered_file, original_line_numbers)
    labeled_list = output_basic_listing(Lexer, numbered_file, jump_targets, basic_type)
    labeled_file = labeled_list.splitlines()
    return labeled_file
