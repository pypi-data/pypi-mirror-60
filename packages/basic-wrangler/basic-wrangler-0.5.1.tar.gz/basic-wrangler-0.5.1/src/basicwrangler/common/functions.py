""" This module contains functions that are accessed from multiple other modules. """

import logging
import re

from basicwrangler.common.constants import RE_QUOTES


def strip_file(unstripped):
    """ Strip newlines and whitespace. """
    # strip whitespace
    stripped = [line.strip() for line in unstripped]
    return stripped


def remove_comments(commented):
    """ This will remove comments from the file. """
    # strip comments
    uncommented = [
        a.rstrip(":")
        for a in [
            b.rstrip() for b in [re.sub(RE_QUOTES + r"'.*?$", "", c) for c in commented]
        ]
    ]
    uncommented = list(filter(None, uncommented))
    return uncommented


def reformat_data_statements(input_file, basic_defs):
    """ Formats a newline-delimited list of values into DATA statements. """
    if basic_defs.data_length is None:
        data_statement_length = basic_defs.basic_line_length - 9
    elif basic_defs.data_length is not None:
        data_statement_length = basic_defs.data_length - 9
    if basic_defs.crunch != 1:
        data_statement_length += 1
    output_file = list()
    for index, line in enumerate(input_file):
        if line.startswith("#data"):
            start_data_block = index + 1
            break
        output_file.append(line)
    for index, line in enumerate(input_file):
        if line.startswith("#enddata"):
            end_data_block = index
    data_block = list()
    for index in range(start_data_block, end_data_block):
        data_block.append(input_file[index])
    logging.debug(data_block)
    if basic_defs.crunch == 1:
        data_statement_start = "DATA"
    else:
        data_statement_start = "DATA "
    data_statement = data_statement_start
    for index, line in enumerate(data_block):
        combined_line_length = len(data_statement) + len(line)
        if combined_line_length <= data_statement_length:
            data_statement = data_statement + line + ","
        elif combined_line_length > data_statement_length:
            data_statement = data_statement.rstrip(",")
            output_file.append(data_statement)
            data_statement = data_statement_start + line + ","
            logging.debug(data_statement)
        logging.debug(data_statement)
    data_statement = data_statement.rstrip(",")
    logging.debug(data_statement)
    output_file.append(data_statement)
    output_file = list(filter(None, output_file))
    return output_file
