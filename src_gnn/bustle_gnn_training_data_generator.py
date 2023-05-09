import logging
import os
import random
import sys
from datetime import datetime

import pandas as pd

from bustle_properties import *
from bustle_string_dsl import *
from utils import *

rule_encodings = {}
rule_encoding_index = 0


def get_rule_encoding(program):
    global rule_encodings
    program_type = type(program)
    if program_type not in rule_encodings:
        encoding = [0] * 184
        global rule_encoding_index
        encoding[rule_encoding_index] = 1
        rule_encoding_index += 1
        rule_encodings[program_type] = encoding
    return rule_encodings[program_type]


def get_vo_property_signature(terminal, input_output):
    property_encodings = {
        AllTrue: EncodedAllTrue,
        AllFalse: EncodedAllFalse,
        Mixed: EncodedMixed,
        Padding: EncodedPadding
    }

    property_signature = []

    # boolean output of subexpression with boolean only properties
    if isinstance(terminal, BoolLiteral):
        for BooleanProperty in BooleanProperties:
            property_value = BooleanProperty([terminal.bool])
            property_signature.extend(property_encodings[property_value])
    else:
        for _ in BooleanProperties:
            property_value = Padding
            property_signature.extend(property_encodings[property_value])

    # integer output of expression with integer only properties
    if isinstance(terminal, IntLiteral):
        for IntegerProperty in IntegerProperties:
            property_value = IntegerProperty([terminal.value])
            property_signature.extend(property_encodings[property_value])
    elif isinstance(terminal, IntVar):
        var_values = [io_example.get(terminal.value) for io_example in input_output]
        for IntegerProperty in IntegerProperties:
            property_value = IntegerProperty(var_values)
            property_signature.extend(property_encodings[property_value])
    else:
        for _ in IntegerProperties:
            property_value = Padding
            property_signature.extend(property_encodings[property_value])

    # string output of subexpression with string only properties
    if isinstance(terminal, StrLiteral):
        for StringProperty in StringProperties:
            property_value = StringProperty([terminal.value])
            property_signature.extend(property_encodings[property_value])
    elif isinstance(terminal, StrVar):
        var_values = [io_example.get(terminal.value) for io_example in input_output]
        for StringProperty in StringProperties:
            property_value = StringProperty(var_values)
            property_signature.extend(property_encodings[property_value])
    else:
        for _ in StringProperties:
            property_value = Padding
            property_signature.extend(property_encodings[property_value])

    # integer output of subexpression and string output of main expression with integer-string properties
    if isinstance(terminal, IntLiteral):
        terminal_input_outputs = []

        for io_example in input_output:
            terminal_input_output = io_example.copy()
            terminal_input_output["cout"] = terminal.value
            terminal_input_outputs.append(terminal_input_output)

        for InputIntegerOutputStringProperty in InputIntegerOutputStringProperties:
            property_value = InputIntegerOutputStringProperty(terminal_input_outputs, 'cout')
            property_signature.extend(property_encodings[property_value])

    elif isinstance(terminal, IntVar):
        for InputIntegerOutputStringProperty in InputIntegerOutputStringProperties:
            property_value = InputIntegerOutputStringProperty(input_output, terminal.value)
            property_signature.extend(property_encodings[property_value])

    else:
        for _ in InputIntegerOutputStringProperties:
            property_value = Padding
            property_signature.extend(property_encodings[property_value])

    # string output of subexpression and string output of main expression with string-string properties
    if isinstance(terminal, StrLiteral):
        terminal_input_outputs = []

        for io_example in input_output:
            terminal_input_output = io_example.copy()
            terminal_input_output["cout"] = terminal.value
            terminal_input_outputs.append(terminal_input_output)

        for InputStringOutputStringProperty in InputStringOutputStringProperties:
            property_value = InputStringOutputStringProperty(terminal_input_outputs, 'cout')
            property_signature.extend(property_encodings[property_value])

    elif isinstance(terminal, StrVar):
        for InputStringOutputStringProperty in InputStringOutputStringProperties:
            property_value = InputStringOutputStringProperty(input_output, terminal.value)
            property_signature.extend(property_encodings[property_value])

    else:
        for _ in InputStringOutputStringProperties:
            property_value = Padding
            property_signature.extend(property_encodings[property_value])

    return property_signature


class ProgramList:

    def __init__(self):
        self.plist = {}
        self.number_programs = 0

    def insert(self, program):
        if program.size not in self.plist:
            self.plist[program.size] = {}

        if program.getReturnType() not in self.plist[program.size]:
            self.plist[program.size][program.getReturnType()] = []

        self.plist[program.size][program.getReturnType()].append(program)
        self.number_programs += 1

    def init_plist(self, string_literals_list, integer_literals_list, boolean_literals_list,
                   string_variables_list, integer_variables_list, input_output):
        for string_literal in string_literals_list:
            init_program = StrLiteral(string_literal)
            self.insert(init_program)

        for integer_literal in integer_literals_list:
            init_program = IntLiteral(integer_literal)
            self.insert(init_program)

        for boolean_literal in boolean_literals_list:
            init_program = BoolLiteral(boolean_literal)
            self.insert(init_program)

        for str_var in string_variables_list:
            init_program = StrVar(str_var)
            self.insert(init_program)

        for int_var in integer_variables_list:
            init_program = IntVar(int_var)
            self.insert(init_program)

    def get_programs_all(self, size):

        if size in self.plist:
            programs = []
            for value in self.plist[size].values():
                programs.extend(value)
            return programs

        return []

    def get_programs(self, size, return_type):

        if size in self.plist:
            if return_type in self.plist[size]:
                return self.plist[size][return_type]

        return []

    def get_number_programs(self):
        return self.number_programs


class BottomUpSearch:

    def __init__(self, string_variables_list, integer_variables_list, input_output):
        self._variables = string_variables_list + integer_variables_list
        self._input_output = input_output
        self.plist = ProgramList()
        self._outputs = set()
        self.closed_list = set()

    def init_env(self, inout):
        env = {}
        for v in self._variables:
            env[v] = inout[v]
        return env

    def has_equivalent(self, program):
        p_out = []
        for inout in self._input_output:
            env = self.init_env(inout)
            out = program.interpret(env)
            if out is not None:
                p_out.append(out)
            else:
                return True

        tuple_out = tuple(p_out)

        if tuple_out not in self._outputs:
            self._outputs.add(tuple_out)
            return False
        return True

    def grow(self, operations, size):
        new_programs = []
        for op in operations:
            for new_program in op.grow(self.plist, size):
                if new_program.toString() not in self.closed_list and not self.has_equivalent(new_program):
                    self.closed_list.add(new_program)
                    new_programs.append(new_program)
                    yield new_program

        for new_program in new_programs:
            self.plist.insert(new_program)

    def search(self, bound, operations, string_literals_list, integer_literals_list,
               boolean_literals_list, string_variables_list,
               integer_variables_list):

        self.plist.init_plist(string_literals_list, integer_literals_list, boolean_literals_list, string_variables_list,
                              integer_variables_list, self._input_output)

        logging.info('Number of programs: ' + str(self.plist.get_number_programs()))

        number_evaluations = 0
        current_size = 0

        while current_size <= bound:

            number_evaluations_bound = 0

            for _ in self.grow(operations, current_size):
                number_evaluations += 1
                number_evaluations_bound += 1

            logging.info('Size: ' + str(current_size) + ' Evaluations: ' + str(number_evaluations_bound))
            current_size += 1

        return None, number_evaluations

    def synthesize(self, bound, operations, string_literals_list, integer_literals_list,
                   boolean_literals_list, string_variables_list,
                   integer_variables_list):

        BustlePCFG.initialize(operations, string_literals_list, integer_literals_list, boolean_literals_list,
                              string_variables_list,
                              integer_variables_list)

        solution, evaluations = self.search(bound, operations, string_literals_list, integer_literals_list,
                                            boolean_literals_list,
                                            string_variables_list, integer_variables_list)

        return solution, evaluations


def find_random_programs(string_variable, all_programs, existing_programs_set, number_of_programs):
    programs = []

    filter_programs = []
    for program_t in all_programs:
        if string_variable in program_t.toString() and program_t not in existing_programs_set:
            filter_programs.append(program_t)

    if len(filter_programs) < number_of_programs:
        programs.extend(filter_programs)
    else:
        programs.extend(random.sample(filter_programs, number_of_programs))

    existing_programs_set.update(programs)
    return programs


def populate_property_value(data_point, property_index, property_encoding):
    property_str = "prop" + str(property_index) + "_"
    for encoding_index, encoding_value in enumerate(property_encoding):
        data_point[property_str + str(encoding_index)] = encoding_value


def get_adjacency_list(intermediate_child_program):
    adjacency_training_data_point = {}
    programs_list = [intermediate_child_program]
    program_index = 0
    edges = []
    while program_index < len(programs_list):
        current_program = programs_list[program_index]
        argument_programs = current_program.get_argument_programs()
        if argument_programs is not None:
            for argument_program in argument_programs:
                edges.append([program_index, len(programs_list)])
                edges.append([len(programs_list), program_index])
                programs_list.append(argument_program)
        program_index += 1

    adjacency_training_data_point["adjacency_list_of_intermediate_program"] = edges
    return adjacency_training_data_point


def get_gnn_encoding(intermediate_child_program, parent_input_outputs):
    encoding_training_data_point = {}
    programs_list = [intermediate_child_program]
    program_index = 0
    encodings = []
    while program_index < len(programs_list):
        current_program = programs_list[program_index]
        argument_programs = current_program.get_argument_programs()
        if argument_programs is not None:
            for argument_program in argument_programs:
                programs_list.append(argument_program)
        if isinstance(current_program, tuple(TERMINALS)):
            encodings.append(get_vo_property_signature(current_program, parent_input_outputs))
        else:
            encodings.append(get_rule_encoding(current_program))
        program_index += 1

    encoding_training_data_point["encoding_of_intermediate_program"] = encodings
    return encoding_training_data_point


def generate_training_data(program_synthesizer, gen_training_data_set,
                           gnn_adjacency_training_data_set,
                           gnn_encoding_training_data,
                           random_inputs, string_variables_list):
    programs = program_synthesizer.plist.get_programs(8, STR_TYPES['type'])
    random_programs = set()
    property_encodings = {
        AllTrue: EncodedAllTrue,
        AllFalse: EncodedAllFalse,
        Mixed: EncodedMixed,
        Padding: EncodedPadding
    }

    for string_variable in string_variables_list:
        find_random_programs(string_variable, programs, random_programs, 200)

    random_programs = list(random_programs)

    for program in random_programs:
        positive_training_data_point = {}
        negative_training_data_point = {}

        parent_input_outputs = []

        for random_input in random_inputs:
            input_output = random_input.copy()
            output = program.interpret(input_output)
            input_output['out'] = output
            parent_input_outputs.append(input_output)

        property_index = 0
        max_string_variables = 3

        string_variables_present = []

        for string_variable in string_variables_list:
            if string_variable in program.toString():
                string_variables_present.append(True)
            else:
                string_variables_present.append(False)

        # PARENT PROPERTY SIGNATURE CALCULATION

        # Input strings string-only properties
        for string_variable_index, string_variable in enumerate(string_variables_list):
            if string_variables_present[string_variable_index]:
                input_strings = [parent_input_output.get(string_variable)
                                 for parent_input_output in parent_input_outputs]
                for StringProperty in StringProperties:
                    property_value = StringProperty(input_strings)
                    property_index += 1
                    populate_property_value(positive_training_data_point, property_index,
                                            property_encodings[property_value])
                    populate_property_value(negative_training_data_point, property_index,
                                            property_encodings[property_value])
            else:
                for _ in StringProperties:
                    property_value = Padding
                    property_index += 1
                    populate_property_value(positive_training_data_point, property_index,
                                            property_encodings[property_value])
                    populate_property_value(negative_training_data_point, property_index,
                                            property_encodings[property_value])

        for padding_index in range(0, max_string_variables - len(string_variables_list)):
            for _ in StringProperties:
                property_value = Padding
                property_index += 1
                populate_property_value(positive_training_data_point, property_index,
                                        property_encodings[property_value])
                populate_property_value(negative_training_data_point, property_index,
                                        property_encodings[property_value])

        # input integer with integer only properties
        """integer_inputs = [input.get(integer_variables[0]) for input in parent_input_outputs]
        if (None not in integer_inputs):
            for property in IntegerProperties:
                property_value = property(integer_inputs)
                property_index += 1
                positive_training_data_point["prop"+str(property_index)] = property_value
                negative_training_data_point["prop"+str(property_index)] = property_value
        else:
            for property in IntegerProperties:
                property_value = Mixed
                property_index += 1
                positive_training_data_point["prop"+str(property_index)] = property_value
                negative_training_data_point["prop"+str(property_index)] = property_value"""

        # output string with string only properties
        output_strings = [parent_input_output['out'] for parent_input_output in parent_input_outputs]
        for StringProperty in StringProperties:
            property_value = StringProperty(output_strings)
            property_index += 1
            populate_property_value(positive_training_data_point, property_index,
                                    property_encodings[property_value])
            populate_property_value(negative_training_data_point, property_index,
                                    property_encodings[property_value])

        # input integer and output string with integer-string properties
        """if (None not in integer_inputs):
            for property in InputIntegerOutputStringProperties:
                property_value = property(parent_input_outputs,integer_variables[0])
                property_index += 1
                positive_training_data_point["prop"+str(property_index)] = property_value
                negative_training_data_point["prop"+str(property_index)] = property_value
        else:
            for property in InputIntegerOutputStringProperties:
                property_value = Mixed
                property_index += 1
                positive_training_data_point["prop"+str(property_index)] = property_value
                negative_training_data_point["prop"+str(property_index)] = property_value"""

        # input strings and output string with string-string properties
        for string_variable_index, string_variable in enumerate(string_variables_list):
            if string_variables_present[string_variable_index]:
                for StringProperty in InputStringOutputStringProperties:
                    property_value = StringProperty(parent_input_outputs, string_variable)
                    property_index += 1
                    populate_property_value(positive_training_data_point, property_index,
                                            property_encodings[property_value])
                    populate_property_value(negative_training_data_point, property_index,
                                            property_encodings[property_value])
            else:
                for _ in InputStringOutputStringProperties:
                    property_value = Padding
                    property_index += 1
                    populate_property_value(positive_training_data_point, property_index,
                                            property_encodings[property_value])
                    populate_property_value(negative_training_data_point, property_index,
                                            property_encodings[property_value])

        for padding_index in range(0, max_string_variables - len(string_variables_list)):
            for _ in InputStringOutputStringProperties:
                property_value = Padding
                property_index += 1
                populate_property_value(positive_training_data_point, property_index,
                                        property_encodings[property_value])
                populate_property_value(negative_training_data_point, property_index,
                                        property_encodings[property_value])

        # FINDING POSITIVE CHILD PROGRAM
        positive_child = None
        child_programs_set = set()
        program.getProgramIds(child_programs_set)
        child_size = 0
        while child_size < 4:
            positive_child = random.choice(list(child_programs_set))
            child_size = positive_child.size

        # FINDING NEGATIVE CHILD PROGRAM
        children = random.sample(program_synthesizer.plist.get_programs_all(6), 2)
        negative_child = children[0]
        if children[0] in child_programs_set:
            negative_child = children[1]

        positive_child_input_outputs = []
        negative_child_input_outputs = []
        pos_property_index = property_index
        neg_property_index = property_index

        for input_index, random_input in enumerate(random_inputs):
            positive_input_output = random_input.copy()
            negative_input_output = random_input.copy()
            positive_output = positive_child.interpret(positive_input_output)
            negative_output = negative_child.interpret(negative_input_output)
            positive_input_output['cout'] = positive_output
            negative_input_output['cout'] = negative_output
            positive_input_output['out'] = parent_input_outputs[input_index]['out']
            negative_input_output['out'] = parent_input_outputs[input_index]['out']
            positive_child_input_outputs.append(positive_input_output)
            negative_child_input_outputs.append(negative_input_output)

        # POSITIVE CHILD PROPERTY SIGNATURE CALCULATION

        outputs = [output['cout'] for output in positive_child_input_outputs]

        # boolean output of subexpression with boolean only properties
        if positive_child.getReturnType() == BOOL_TYPES['type']:
            for StringProperty in BooleanProperties:
                property_value = StringProperty(outputs)
                pos_property_index += 1
                populate_property_value(positive_training_data_point, pos_property_index,
                                        property_encodings[property_value])

        else:
            for _ in BooleanProperties:
                property_value = Padding
                pos_property_index += 1
                populate_property_value(positive_training_data_point, pos_property_index,
                                        property_encodings[property_value])

        # integer output of expression with integer only properties
        if positive_child.getReturnType() == INT_TYPES['type']:
            for StringProperty in IntegerProperties:
                property_value = StringProperty(outputs)
                pos_property_index += 1
                populate_property_value(positive_training_data_point, pos_property_index,
                                        property_encodings[property_value])

        else:
            for _ in IntegerProperties:
                property_value = Padding
                pos_property_index += 1
                populate_property_value(positive_training_data_point, pos_property_index,
                                        property_encodings[property_value])

        # string output of subexpression with string only properties
        if positive_child.getReturnType() == STR_TYPES['type']:
            for StringProperty in StringProperties:
                property_value = StringProperty(outputs)
                pos_property_index += 1
                populate_property_value(positive_training_data_point, pos_property_index,
                                        property_encodings[property_value])

        else:
            for _ in StringProperties:
                property_value = Padding
                pos_property_index += 1
                populate_property_value(positive_training_data_point, pos_property_index,
                                        property_encodings[property_value])

        # integer output of subexpression and string output of main expression with integer-string properties
        if positive_child.getReturnType() == INT_TYPES['type']:
            for StringProperty in InputIntegerOutputStringProperties:
                property_value = StringProperty(positive_child_input_outputs, 'cout')
                pos_property_index += 1
                populate_property_value(positive_training_data_point, pos_property_index,
                                        property_encodings[property_value])
        else:
            for _ in InputIntegerOutputStringProperties:
                property_value = Padding
                pos_property_index += 1
                populate_property_value(positive_training_data_point, pos_property_index,
                                        property_encodings[property_value])

        # string output of subexpression and string output of main expression with string-string properties
        if positive_child.getReturnType() == STR_TYPES['type']:
            for StringProperty in InputStringOutputStringProperties:
                property_value = StringProperty(positive_child_input_outputs, 'cout')
                pos_property_index += 1
                populate_property_value(positive_training_data_point, pos_property_index,
                                        property_encodings[property_value])
        else:
            for _ in InputStringOutputStringProperties:
                property_value = Padding
                pos_property_index += 1
                populate_property_value(positive_training_data_point, pos_property_index,
                                        property_encodings[property_value])

        # NEGATIVE CHILD PROPERTY SIGNATURE CALCULATION

        outputs = [output['cout'] for output in negative_child_input_outputs]

        # boolean output of subexpression with boolean only properties
        if negative_child.getReturnType() == BOOL_TYPES['type']:
            for StringProperty in BooleanProperties:
                property_value = StringProperty(outputs)
                neg_property_index += 1
                populate_property_value(negative_training_data_point, neg_property_index,
                                        property_encodings[property_value])
        else:
            for _ in BooleanProperties:
                property_value = Padding
                neg_property_index += 1
                populate_property_value(negative_training_data_point, neg_property_index,
                                        property_encodings[property_value])

        # integer output of expression with integer only properties
        if negative_child.getReturnType() == INT_TYPES['type']:
            for StringProperty in IntegerProperties:
                property_value = StringProperty(outputs)
                neg_property_index += 1
                populate_property_value(negative_training_data_point, neg_property_index,
                                        property_encodings[property_value])
        else:
            for _ in IntegerProperties:
                property_value = Padding
                neg_property_index += 1
                populate_property_value(negative_training_data_point, neg_property_index,
                                        property_encodings[property_value])

        # string output of subexpression with string only properties
        if negative_child.getReturnType() == STR_TYPES['type']:
            for StringProperty in StringProperties:
                property_value = StringProperty(outputs)
                neg_property_index += 1
                populate_property_value(negative_training_data_point, neg_property_index,
                                        property_encodings[property_value])
        else:
            for _ in StringProperties:
                property_value = Padding
                neg_property_index += 1
                populate_property_value(negative_training_data_point, neg_property_index,
                                        property_encodings[property_value])

        # integer output of subexpression and string output of main expression with integer-string properties
        if negative_child.getReturnType() == INT_TYPES['type']:
            for StringProperty in InputIntegerOutputStringProperties:
                property_value = StringProperty(negative_child_input_outputs, 'cout')
                neg_property_index += 1
                populate_property_value(negative_training_data_point, neg_property_index,
                                        property_encodings[property_value])
        else:
            for _ in InputIntegerOutputStringProperties:
                property_value = Padding
                neg_property_index += 1
                populate_property_value(negative_training_data_point, neg_property_index,
                                        property_encodings[property_value])

        # string output of subexpression and string output of main expression with string-string properties
        if negative_child.getReturnType() == STR_TYPES['type']:
            for StringProperty in InputStringOutputStringProperties:
                property_value = StringProperty(negative_child_input_outputs, 'cout')
                neg_property_index += 1
                populate_property_value(negative_training_data_point, neg_property_index,
                                        property_encodings[property_value])
        else:
            for _ in InputStringOutputStringProperties:
                property_value = Padding
                neg_property_index += 1
                populate_property_value(negative_training_data_point, neg_property_index,
                                        property_encodings[property_value])

        positive_training_data_point['label'] = 1
        negative_training_data_point['label'] = 0

        gen_training_data_set.append(positive_training_data_point)
        gen_training_data_set.append(negative_training_data_point)

        gnn_adjacency_training_data_set.append(get_adjacency_list(positive_child))
        gnn_adjacency_training_data_set.append(get_adjacency_list(negative_child))

        gnn_encoding_training_data.append(get_gnn_encoding(positive_child, parent_input_outputs))
        gnn_encoding_training_data.append(get_gnn_encoding(negative_child, parent_input_outputs))


if __name__ == "__main__":

    log_filename = logs_directory + "gnn_training_data_generator.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    random_inputs_filename = config_directory + "bustle_random_strings.csv"

    training_data_filename = data_directory + "bustle_training_data.csv"
    gnn_training_data_filename = data_directory + "gnn_adjacency_training_data.csv"
    gnn_encoding_data_filename = data_directory + "gnn_encoding_training_data.csv"

    os.makedirs(os.path.dirname(training_data_filename), exist_ok=True)

    if len(sys.argv) == 2:
        slurm_task_id = sys.argv[1]
        logging.basicConfig(filename=log_filename,
                            filemode='a',
                            format="[Task: " + str(slurm_task_id) + "] " + '%(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
    else:
        logging.basicConfig(filename=log_filename,
                            filemode='a',
                            format='%(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

    dsl_functions = [StrConcat, StrReplace,
                     StrSubstr, StrIte, StrIntToStr, StrCharAt, StrTrim, StrLower,
                     StrUpper, StrLeftSubstr, StrRightSubstr,
                     StrReplaceMulti, StrReplaceAdd, IntStrToInt, IntPlus,
                     IntMinus, IntLength, IntIteInt, IntIndexOf, IntFirstIndexOf, BoolEqual, BoolContain,
                     BoolSuffixof, BoolPrefixof, BoolGreaterThan, BoolGreaterThanEqual]

    string_literals = ['', '/', ' ', ',', '-', '.']

    string_variables = ['arg0', 'arg1', 'arg2']
    integer_variables = []
    integer_literals = [0, 1, 2, 3]
    boolean_literals = [True, False]

    dataFrame = pd.read_csv(random_inputs_filename)
    random_input_strings_list = dataFrame.to_dict('records')

    number_of_io_pairs = dataFrame.shape[1]
    number_of_input_strings = dataFrame.shape[0] - 1

    training_data_set = []
    gnn_adjacency_list_training_data_set = []
    gnn_encoding_training_data_set = []
    start_time = datetime.now()
    logging.info("generation start time: " + str(start_time))
    for search_index in range(0, 50):

        begin_time = datetime.now()
        logging.info("start time: " + str(datetime.now()))
        arg0 = random_input_strings_list[random.randint(0, number_of_input_strings)]
        arg1 = random_input_strings_list[random.randint(0, number_of_input_strings)]
        arg2 = random_input_strings_list[random.randint(0, number_of_input_strings)]

        io_pairs = []

        for index in range(number_of_io_pairs):
            arg_key = 'arg' + str(index)
            io_pair = {'arg0': str(arg0[arg_key]), 'arg1': str(arg1[arg_key]), 'arg2': str(arg2[arg_key])}
            io_pairs.append(io_pair)

        logging.info("examples: " + str(io_pairs))

        synthesizer = BottomUpSearch(string_variables, integer_variables, io_pairs)
        p, num = synthesizer.synthesize(8, dsl_functions,
                                        string_literals,
                                        integer_literals,
                                        boolean_literals,
                                        string_variables,
                                        integer_variables)

        generate_training_data(synthesizer, training_data_set, gnn_adjacency_list_training_data_set,
                               gnn_encoding_training_data_set,
                               io_pairs, string_variables)
        logging.info("end time: " + str(datetime.now()))
        logging.info("Time taken: " + str(datetime.now() - begin_time))

    logging.info("training dataset size: " + str(len(training_data_set)))
    dataFrame = pd.DataFrame(training_data_set)
    logging.info("Saving the training data to csv file...")
    dataFrame.to_csv(training_data_filename, index=False, mode='a',
                     header=not os.path.exists(training_data_filename))

    logging.info("gnn adjacency dataset size: " + str(len(gnn_adjacency_list_training_data_set)))
    gnn_dataFrame = pd.DataFrame(gnn_adjacency_list_training_data_set)
    logging.info("Saving the adjacency list training data to csv file...")
    gnn_dataFrame.to_csv(gnn_training_data_filename, index=False, mode='a',
                         header=not os.path.exists(gnn_training_data_filename))

    logging.info("gnn encoding dataset size: " + str(len(gnn_encoding_training_data_set)))
    gnn_encoding_dataFrame = pd.DataFrame(gnn_encoding_training_data_set)
    logging.info("Saving the encoding training data to csv file...")
    gnn_encoding_dataFrame.to_csv(gnn_encoding_data_filename, index=False, mode='a',
                                  header=not os.path.exists(gnn_encoding_data_filename))
