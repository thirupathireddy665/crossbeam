from utils import *
import pickle

AllTrue = -1
Mixed = 0
AllFalse = 1
Padding = 2

EncodedAllTrue = [1, 0, 0, 0]
EncodedAllFalse = [0, 1, 0, 0]
EncodedMixed = [0, 0, 1, 0]
EncodedPadding = [0, 0, 0, 1]

property_input_key = 'arg'
property_output_key = 'out'


def load_object(filename):
    with open(filename, 'rb') as inp:
        property_object = pickle.load(inp)
        return property_object


def make_property(property_index):
    property_object = load_object(pickle_files_directory + "prop" + str(property_index) + ".pkl")

    def property_function(input_output, key):
        # print("index: ", property_index)
        # print("property: ", property_object.toString())
        is_true_present = False
        is_false_present = False
        for in_out in input_output:
            program_input = in_out[key]
            output = in_out['out']
            property_input_output = {property_input_key: program_input, property_output_key: output}
            property_output = property_object.interpret(property_input_output)
            if property_output:
                is_true_present = True
            else:
                is_false_present = True

        if is_true_present and is_false_present:
            return Mixed
        elif is_true_present:
            return AllTrue
        else:
            return AllFalse

    return property_function


# Properties acting only on the string
def is_string_empty(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if len(program_input) == 0:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_single_char(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if len(program_input.strip()) == 1:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_short_string(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if len(program_input.strip()) <= 5:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_lower_case(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if program_input.islower():
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_upper_case(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if program_input.isupper():
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_contains_space(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if " " in program_input:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_contains_comma(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if "," in program_input:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_contains_period(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if "." in program_input:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_contains_dash(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if "-" in program_input:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_contains_slash(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if "/" in program_input:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_contains_digit(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if regex_digit.search(program_input) is not None:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_contains_only_digits(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if regex_only_digits.search(program_input) is not None:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_contains_letters(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if regex_alpha.search(program_input) is not None:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_contains_letters_only(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if regex_alpha_only.search(program_input) is not None:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


# Properties acting only on the integer

def is_zero(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if program_input == 0:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_one(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if program_input == 1:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_two(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if program_input == 2:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_negative(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if program_input < 0:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_small(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if 0 < program_input <= 3:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_medium(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if 3 < program_input <= 9:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_large(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if program_input > 9:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


# Properties acting only on Boolean

def is_true(inputs):
    is_true_present = False
    is_false_present = False
    for program_input in inputs:
        if program_input:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


# Properties acting on input integer and output string
def is_less_than_output_length(input_output, key):
    is_true_present = False
    is_false_present = False
    for in_out in input_output:
        program_input = in_out[key]
        output = in_out['out']
        if program_input < len(output):
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_less_than_or_equal_output_length(input_output, key):
    is_true_present = False
    is_false_present = False
    for in_out in input_output:
        program_input = in_out[key]
        output = in_out['out']
        if program_input <= len(output):
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_equal_output_length(input_output, key):
    is_true_present = False
    is_false_present = False
    for in_out in input_output:
        program_input = in_out[key]
        output = in_out['out']
        if program_input == len(output):
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_greater_than_or_equal_output_length(input_output, key):
    is_true_present = False
    is_false_present = False
    for in_out in input_output:
        program_input = in_out[key]
        output = in_out['out']
        if program_input >= len(output):
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_greater_than_output_length(input_output, key):
    is_true_present = False
    is_false_present = False
    for in_out in input_output:
        program_input = in_out[key]
        output = in_out['out']
        if program_input > len(output):
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_very_closer_to_output_length(input_output, key):
    is_true_present = False
    is_false_present = False
    for in_out in input_output:
        program_input = in_out[key]
        output = in_out['out']
        if abs(program_input - len(output)) <= 1:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


def is_closer_to_output_length(input_output, key):
    is_true_present = False
    is_false_present = False
    for in_out in input_output:
        program_input = in_out[key]
        output = in_out['out']
        if abs(program_input - len(output)) <= 3:
            is_true_present = True
        else:
            is_false_present = True

    if is_true_present and is_false_present:
        return Mixed
    elif is_true_present:
        return AllTrue
    else:
        return AllFalse


StringProperties = [is_string_empty,
                    is_single_char,
                    is_short_string,
                    is_lower_case,
                    is_upper_case,
                    is_contains_space,
                    is_contains_comma,
                    is_contains_period,
                    is_contains_dash,
                    is_contains_slash,
                    is_contains_digit,
                    is_contains_only_digits,
                    is_contains_letters,
                    is_contains_letters_only
                    ]

IntegerProperties = [is_zero,
                     is_one,
                     is_two,
                     is_negative,
                     is_small,
                     is_medium,
                     is_large
                     ]

BooleanProperties = [is_true]

# Properties acting on input string and output string
InputStringOutputStringProperties = [make_property(property_index)
                                     for property_index in
                                     range(0, 100)]

SubModularPropertyRankings = [79, 58, 72, 37, 77, 26, 8, 60, 62, 38, 74, 32, 76, 57, 71, 65, 50, 11, 64, 13, 10, 53, 86, 55, 12, 59, 67, 31, 69, 14, 61, 73, 81, 52, 54, 75, 28, 15, 2, 0, 1, 6, 4, 7, 25, 16, 3, 66, 5, 30, 34, 33, 78, 9, 68, 17, 18, 19, 35, 20, 21, 22, 36, 24, 27, 23, 29, 63, 80, 39, 40, 41, 42, 43, 90, 44, 88, 45, 46, 49, 47, 70, 48, 51, 56, 82, 83, 84, 85, 87, 89, 91, 92, 93, 94, 95, 96, 97, 98, 99]

properties_considered_count = 30
TopInputStringOutputStringProperties = [InputStringOutputStringProperties[rank_index]
                                        for rank_index in
                                        SubModularPropertyRankings[:properties_considered_count]]

BottomInputStringOutputStringProperties = [InputStringOutputStringProperties[rank_index]
                                           for rank_index in
                                           SubModularPropertyRankings[-1 * properties_considered_count:]]

InputIntegerOutputStringProperties = [
    is_less_than_output_length,
    is_less_than_or_equal_output_length,
    is_equal_output_length,
    is_greater_than_or_equal_output_length,
    is_greater_than_output_length,
    is_very_closer_to_output_length,
    is_closer_to_output_length
]
