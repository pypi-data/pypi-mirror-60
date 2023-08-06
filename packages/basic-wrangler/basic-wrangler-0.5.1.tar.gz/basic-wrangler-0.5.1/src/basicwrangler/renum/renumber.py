""" This module contains the line number renumbering routines. """
# pylint: disable=bad-continuation
import logging
import re

from basicwrangler.common.constants import RE_QUOTES


def populate_label_data(working_file):
    """ This function populates a dictionary with labels and determines how many bytes to assume when replacing a line label. """
    file_length = len(working_file)
    line_count = 0
    label_dict = dict()
    # add labels to dictionary
    for line in working_file:
        if line.startswith("_"):
            label_dict[line] = 0
            line_count += 1
            logging.debug(line)
    lines_total = file_length - line_count
    logging.debug("Total number of lines: %s", lines_total)
    # determine how many bytes are needed when replacing labels
    if lines_total < 10:
        line_replacement = 1
    elif lines_total < 100:
        line_replacement = 2
    elif lines_total < 1000:
        line_replacement = 3
    elif lines_total < 10000:
        line_replacement = 4
    else:
        line_replacement = 5
    logging.debug("Line replacement value: %s", line_replacement)
    return label_dict, line_replacement


def fix_spacing(line):
    """ Removes spaces where they are not needed. """
    error_list = [('"', ";"), (";", '"'), ("<>", '"'), ("=", '"')]
    adjust_length = 0
    # remove spaces between one thing and another using the list of tuples above
    for index, _ in enumerate(error_list):
        for x in range(len(line) - 1, -1, -1):
            if line[x - 1].endswith(error_list[index][0]) and line[x].startswith(
                error_list[index][1]
            ):
                line[x - 1] = line[x - 1] + line[x]
                line.pop(x)
                adjust_length += 1
    # remove spaces between comma joined elements
    for x in range(len(line) - 1, -1, -1):
        if line[x] == ",":
            line[x - 1] = line[x - 1] + line[x] + line[x + 1]
            line.pop(x + 1)
            line.pop(x)
            adjust_length += 2
    logging.debug("Line adjusment is: %s", adjust_length)
    return line, adjust_length


def check_new_line(line):
    """ Checks to see if a new line is mandatory. """
    need_new_line = False
    if "IF" in line:
        need_new_line = True
    if "GOTO" in line:
        need_new_line = True
    if "RETURN" in line:
        need_new_line = True
    if (
        line[0].startswith("DATA")
        or line[0].startswith("D.")
        or line[0].startswith("REM")
    ):
        need_new_line = True
    return need_new_line


def determine_line_length(line, basic_defs, line_replacement):
    """ Algorithmically determine the length of a line. """
    current_line_length = 0
    for element in line:
        if element.startswith("`"):
            current_line_length = current_line_length + line_replacement
        elif element == "PRINT" and basic_defs.print_as_question:
            current_line_length += 1
        else:
            current_line_length = current_line_length + len(element)
    if basic_defs.crunch == 0:
        for element in line:
            current_line_length += 1
    return current_line_length


def crunch_line(line, basic_defs):
    """ This function crunches lines.

    If crunch is 0, it will join with spaces, and if crunch is 1 it will join with no spaces. """
    if not basic_defs.tokenize:
        while basic_defs.print_as_question and "PRINT" in line:
            print_index = line.index("PRINT")
            line[print_index] = "?"
    if basic_defs.crunch == 1:
        final_line = "".join(line)
    else:
        final_line = " ".join(line)
    return final_line


def tokenize_line(line):
    """ A super-naive line lexer.

    This splits a string on spaces, quotes, and commas to create a list of tokens.
    TODO: replace this with a better lexer at some point. """
    temp1 = re.split(r"(REM.*$|DATA.*$|D\..*$|\s|\".*?\"|,)", line)
    temp2 = [x for x in temp1 if x.strip()]
    return temp2


def start_new_line(current_line_number):
    """ Starts a new BASIC line. """
    current_line = str(current_line_number)
    current_line_length = len(current_line)
    return current_line, current_line_length


def renumber_basic_file(
    input_file, basic_defs, label_dict, line_replacement, basic_type
):
    """ The main renumbering routine. """
    output_file = list()
    current_line_number = basic_defs.numbering
    persistent_buffer, persistent_line_length = start_new_line(current_line_number)
    for line in input_file:
        logging.debug(persistent_buffer)
        # routine for jump targets
        if line.startswith("_"):
            if persistent_buffer != str(current_line_number):
                label_dict[line] = current_line_number + basic_defs.increment
                persistent_buffer = persistent_buffer.rstrip(
                    basic_defs.statement_joining_character
                )
                output_file.append(persistent_buffer)
                current_line_number = current_line_number + basic_defs.increment
            else:
                label_dict[line] = current_line_number
            logging.debug(persistent_buffer)
            persistent_buffer, persistent_line_length = start_new_line(
                current_line_number
            )
            continue
        # tokenizes lines, determines line length, and sets the current buffer to the tokenized line
        tokenized_line = tokenize_line(line)
        logging.debug(tokenized_line)
        current_buffer_length = determine_line_length(
            tokenized_line, basic_defs, line_replacement
        )
        logging.debug("Current buffer length: %s", current_buffer_length)
        # fix spacing when spaces are needed
        if basic_defs.crunch != 1:
            fixed_line, adjust_length = fix_spacing(tokenized_line)
            current_buffer_length = current_buffer_length - adjust_length
            current_buffer = crunch_line(fixed_line, basic_defs)
        else:
            current_buffer = crunch_line(tokenized_line, basic_defs)
        logging.debug(current_buffer)
        # when lines don't need to be combined
        if not basic_defs.combine:
            persistent_buffer = persistent_buffer + current_buffer
            output_file.append(persistent_buffer)
            current_line_number = current_line_number + basic_defs.increment
            logging.debug(persistent_buffer)
            persistent_buffer, persistent_line_length = start_new_line(
                current_line_number
            )
        # when lines do need to be combined
        else:
            combined_line_length = (
                persistent_line_length
                + len(basic_defs.statement_joining_character)
                + current_buffer_length
            )
            logging.debug("Combined line length: %s", combined_line_length)
            need_new_line = check_new_line(tokenized_line)
            # when a new line is mandatory
            if need_new_line:
                if basic_type in ["bbc", "riscos"] and current_buffer.startswith(
                    "DATA"
                ):
                    # this is to avoid Out of DATA errors in BBC BASIC - it's the same code as the code below, I know, but using seperate functions for this stuff is trickier than it looks, and there's other features for this that are worth working on first
                    persistent_buffer = persistent_buffer.rstrip(
                        basic_defs.statement_joining_character
                    )
                    output_file.append(persistent_buffer)
                    current_line_number = current_line_number + basic_defs.increment
                    logging.debug(persistent_buffer)
                    persistent_buffer, persistent_line_length = start_new_line(
                        current_line_number
                    )
                    persistent_buffer = persistent_buffer + current_buffer
                    output_file.append(persistent_buffer)
                    current_line_number = current_line_number + basic_defs.increment
                    logging.debug(persistent_buffer)
                    persistent_buffer, persistent_line_length = start_new_line(
                        current_line_number
                    )
                elif combined_line_length <= basic_defs.basic_line_length:
                    persistent_buffer = persistent_buffer + current_buffer
                    output_file.append(persistent_buffer)
                    current_line_number = current_line_number + basic_defs.increment
                    logging.debug(persistent_buffer)
                    persistent_buffer, persistent_line_length = start_new_line(
                        current_line_number
                    )
                elif combined_line_length > basic_defs.basic_line_length:
                    persistent_buffer = persistent_buffer.rstrip(
                        basic_defs.statement_joining_character
                    )
                    output_file.append(persistent_buffer)
                    current_line_number = current_line_number + basic_defs.increment
                    logging.debug(persistent_buffer)
                    persistent_buffer, persistent_line_length = start_new_line(
                        current_line_number
                    )
                    persistent_buffer = persistent_buffer + current_buffer
                    output_file.append(persistent_buffer)
                    current_line_number = current_line_number + basic_defs.increment
                    logging.debug(persistent_buffer)
                    persistent_buffer, persistent_line_length = start_new_line(
                        current_line_number
                    )
                continue
            # when a new line is not mandatory
            if combined_line_length <= basic_defs.basic_line_length:
                current_buffer = current_buffer + basic_defs.statement_joining_character
                persistent_buffer = persistent_buffer + current_buffer
                persistent_line_length = len(persistent_buffer)
            elif combined_line_length > basic_defs.basic_line_length:
                persistent_buffer = persistent_buffer.rstrip(
                    basic_defs.statement_joining_character
                )
                output_file.append(persistent_buffer)
                current_line_number = current_line_number + basic_defs.increment
                logging.debug(persistent_buffer)
                persistent_buffer, persistent_line_length = start_new_line(
                    current_line_number
                )
                persistent_buffer = (
                    persistent_buffer
                    + current_buffer
                    + basic_defs.statement_joining_character
                )
                persistent_line_length = len(persistent_buffer)
    # replace labels with line numbers
    for key in sorted(label_dict, key=len, reverse=True):
        for index, line in enumerate(output_file):
            output_file[index] = re.sub(key + RE_QUOTES, str(label_dict[key]), line)
    # warn if line is too long
    for index, line in enumerate(output_file):
        if len(line) > basic_defs.basic_line_length:
            line_number_match = re.search(r"^\d*", line)
            line_number = line[
                line_number_match.span()[0] : line_number_match.span()[1]
            ]
            logging.warning("Line number %s may be too long.", line_number)
    # add space in between line number and rest of line for certain basic versions
    if basic_type in ["bascom", "amiga"] or basic_type.startswith("zx"):
        for index, line in enumerate(output_file):
            space_index = re.search(r"^\d*", line)
            output_file[index] = (
                line[0 : space_index.span()[1]] + " " + line[space_index.span()[1] :]
            )
    return output_file
