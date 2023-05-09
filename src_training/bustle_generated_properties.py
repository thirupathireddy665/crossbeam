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
        # print(property_object.toString())
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
                                     range(0, 130)]


LongProgramAvgRanks = [33, 94, 68, 91, 32, 111, 6, 31, 4, 90, 25, 41, 37, 30,
                       88, 29, 19, 21, 2, 35, 92, 63, 87, 39, 15, 8, 67, 23,
                       17, 16, 9, 10, 44, 13, 14, 59, 12, 38, 18, 1, 34, 84,
                       40, 5, 20, 3, 0, 24, 26, 45, 43, 27, 7, 46, 11, 22, 36,
                       83, 108, 81, 50, 28, 110, 119, 48, 66, 64, 107, 42, 52,
                       86, 53, 62, 51, 49, 60, 121, 56, 47, 85, 57, 74, 65, 61,
                       93, 55, 54, 82, 58, 124, 73, 76, 75, 77, 79, 80, 69, 70,
                       109, 71, 72, 96, 99, 78, 98, 100, 101, 89, 95, 97, 103,
                       102, 104, 106, 112, 105, 113, 118, 114, 115, 120, 116,
                       117, 122, 123, 125, 126, 127, 128, 129]

MediumProgramAvgRanks = [94, 68, 6, 32, 91, 4, 31, 90, 41, 25, 33, 19, 2, 9, 14,
                         1, 0, 8, 21, 3, 17, 29, 15, 5, 12, 30, 10, 39, 13, 7,
                         16, 23, 87, 11, 22, 20, 38, 37, 18, 44, 26, 27, 35, 40,
                         24, 63, 43, 34, 88, 28, 45, 81, 42, 46, 36, 59, 50, 52,
                         49, 51, 47, 48, 67, 56, 57, 60, 53, 55, 54, 83, 84, 64,
                         111, 61, 58, 65, 86, 66, 85, 82, 62, 73, 93, 74, 69, 70,
                         92, 71, 121, 76, 72, 79, 80, 75, 119, 77, 78, 96, 99,
                         100, 89, 98, 101, 108, 124, 95, 109, 97, 104, 102, 106,
                         110, 103, 105, 107, 112, 113, 122, 114, 117, 115, 116,
                         118, 120, 123, 125, 126, 127, 128, 129]

MediumProgramSumRanks = [19, 33, 71, 85, 86, 94, 25, 91, 72, 32, 41, 59, 68, 90,
                         99, 124, 111, 30, 92, 31, 14, 95, 98, 36, 65, 29, 9, 63,
                         96, 10, 37, 81, 52, 83, 74, 45, 4, 101, 82, 76, 6, 110,
                         53, 56, 50, 18, 121, 24, 119, 42, 84, 34, 67, 46, 87, 88,
                         5, 39, 40, 28, 15, 35, 26, 27, 100, 109, 44, 108, 43, 0,
                         1, 2, 3, 7, 8, 11, 12, 13, 16, 17, 20, 21, 22, 23, 38,
                         47, 48, 49, 51, 54, 55, 57, 58, 60, 61, 62, 64, 66, 69,
                         70, 73, 75, 77, 78, 79, 80, 89, 93, 97, 102, 103, 104,
                         105, 106, 107, 112, 113, 114, 115, 116, 117, 118, 120,
                         122, 123, 125, 126, 127, 128, 129]


ShortProgramAvgRanks = [94, 31, 68, 2, 32, 25, 4, 9, 1, 3, 0, 91, 6, 5, 23, 8, 7,
                        10, 15, 29, 12, 14, 41, 17, 21, 11, 16, 13, 30, 20, 19, 22,
                        18, 33, 37, 26, 35, 27, 34, 24, 40, 39, 38, 28, 44, 36, 63,
                        43, 46, 45, 42, 48, 47, 52, 49, 67, 50, 51, 55, 56, 54, 53,
                        61, 57, 60, 65, 64, 59, 83, 58, 87, 85, 81, 62, 66, 88, 69,
                        70, 80, 73, 93, 74, 71, 72, 86, 82, 77, 75, 76, 92, 79, 78,
                        84, 90, 89, 95, 99, 101, 96, 98, 97, 100, 111, 102, 108,
                        103, 104, 106, 105, 107, 124, 119, 121, 109, 110, 112, 113,
                        114, 117, 115, 122, 118, 116, 120, 123, 125, 126, 127, 128,
                        129]

ShortProgramSumRanks = [67, 21, 25, 71, 10, 32, 94, 91, 41, 93, 33, 99, 68, 86,
                        90, 65, 46, 117, 111, 82, 44, 74, 36, 31, 12, 83, 29, 45,
                        52, 88, 48, 59, 30, 63, 84, 4, 124, 18, 87, 34, 121, 15,
                        101, 14, 6, 24, 28, 35, 119, 92, 108, 0, 1, 2, 3, 5, 7, 8,
                        9, 11, 13, 16, 17, 19, 20, 22, 23, 26, 27, 37, 38, 39, 40,
                        42, 43, 47, 49, 50, 51, 53, 54, 55, 56, 57, 58, 60, 61, 62,
                        64, 66, 69, 70, 72, 73, 75, 76, 77, 78, 79, 80, 81, 85,
                        89, 95, 96, 97, 98, 100, 102, 103, 104, 105, 106, 107, 109,
                        110, 112, 113, 114, 115, 116, 118, 120, 122, 123, 125,
                        126, 127, 128, 129]

SizeBasedRanks = list(range(0, 130))

SubModularPropertyRankings = SizeBasedRanks

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
