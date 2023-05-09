import logging
import os
import random
import sys
from datetime import datetime

import pandas as pd

from bustle_generated_properties import *
from bustle_string_dsl import *
from utils import *
from bustle_random_strings import *


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
                   string_variables_list, integer_variables_list):
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
                if (
                        new_program is not None) and new_program.toString() not in self.closed_list and not self.has_equivalent(
                    new_program):
                    self.closed_list.add(new_program)
                    new_programs.append(new_program)
                    yield new_program

        for new_program in new_programs:
            self.plist.insert(new_program)

    def search(self, bound, operations, string_literals_list, integer_literals_list,
               boolean_literals_list, string_variables_list,
               integer_variables_list):

        self.plist.init_plist(string_literals_list, integer_literals_list, boolean_literals_list, string_variables_list,
                              integer_variables_list)

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


def generate_training_data(program_synthesizer, gen_training_data_set, random_inputs,
                           string_variables_list):
    programs = program_synthesizer.program_list.get_programs(8, STR_TYPES['type'])
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

        # FINDING POSITIVE CHILD PROGRAMS
        positive_child_programs_set = set()
        program.getProgramIds(positive_child_programs_set)
        string_return_type_programs = list(
            filter(lambda child_program: child_program.getReturnType() == STR_TYPES['type'],
                   positive_child_programs_set))
        if len(string_return_type_programs) <= 0:
            continue

        positive_data_points = []
        for positive_child in string_return_type_programs:
            positive_data_point = positive_training_data_point.copy()
            positive_child_input_outputs = []
            pos_property_index = property_index

            for input_index, random_input in enumerate(random_inputs):
                positive_input_output = random_input.copy()
                positive_output = positive_child.interpret(positive_input_output)
                positive_input_output['cout'] = positive_output
                positive_input_output['out'] = parent_input_outputs[input_index]['out']
                positive_child_input_outputs.append(positive_input_output)

            # POSITIVE CHILD PROPERTY SIGNATURE CALCULATION

            # string output of subexpression and string output of main expression with string-string properties
            for StringProperty in InputStringOutputStringProperties:
                property_value = StringProperty(positive_child_input_outputs, 'cout')
                pos_property_index += 1
                populate_property_value(positive_data_point, pos_property_index,
                                        property_encodings[property_value])

            positive_data_point['label'] = 1
            positive_data_points.append(positive_data_point)

        # FINDING NEGATIVE CHILD PROGRAMS
        string_child_programs = program_synthesizer.program_list.get_programs(6, STR_TYPES['type'])
        if len(string_child_programs) < 1:
            continue
        children = random.sample(string_child_programs, 6)
        negative_childs = set()
        for negative_child in children:
            child_programs_set = set()
            negative_child.getProgramIds(child_programs_set)
            negative_childs.update(child_programs_set)

        negative_childs -= positive_child_programs_set
        negative_childs = random.sample(negative_childs, len(positive_child_programs_set))

        negative_data_points = []
        for negative_child in negative_childs:
            negative_data_point = negative_training_data_point.copy()
            negative_child_input_outputs = []
            neg_property_index = property_index

            for input_index, random_input in enumerate(random_inputs):
                negative_input_output = random_input.copy()
                negative_output = negative_child.interpret(negative_input_output)
                negative_input_output['cout'] = negative_output
                negative_input_output['out'] = parent_input_outputs[input_index]['out']
                negative_child_input_outputs.append(negative_input_output)

            # NEGATIVE CHILD PROPERTY SIGNATURE CALCULATION

            # string output of subexpression and string output of main expression with string-string properties
            for StringProperty in InputStringOutputStringProperties:
                property_value = StringProperty(negative_child_input_outputs, 'cout')
                neg_property_index += 1
                populate_property_value(negative_data_point, neg_property_index,
                                        property_encodings[property_value])

            negative_data_point['label'] = 0
            negative_data_points.append(negative_data_point)

        for data_index, positive_data_point in enumerate(positive_data_points):
            gen_training_data_set.append(positive_data_point)
            gen_training_data_set.append(negative_data_points[data_index])


if __name__ == "__main__":

    log_filename = logs_directory + "expand_bustle_training.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    training_data_filename = data_directory + "expand_bustle_training_data.csv"
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

    string_literals = ['', '/', ' ', ',', '-', '.', '+', '_', '@', '$']

    integer_variables = []
    integer_literals = [0, 1, 2, 3]
    boolean_literals = [True, False]

    number_of_io_pairs = 3
    number_of_input_strings = 3

    training_data_set = []
    start_time = datetime.now()
    logging.info("generation start time: " + str(start_time))

    for search_index in range(0, 40):

        begin_time = datetime.now()
        logging.info("start time: " + str(datetime.now()))
        # below line is for strings from crossbeam paper
        args = bustle_inputs_dict_generator(number_of_input_strings, number_of_io_pairs)
        # args = random_inputs_dict_generator(number_of_input_strings, number_of_io_pairs)

        io_pairs = []
        string_variables = []

        for arg_index in range(number_of_input_strings):
            string_variables.append('arg' + str(arg_index))

        for index in range(number_of_io_pairs):
            io_pair = {}
            for arg_index in range(number_of_input_strings):
                arg_key = 'arg' + str(arg_index)
                io_pair[arg_key] = args[arg_key][index]
            io_pairs.append(io_pair)

        logging.info("examples: " + str(io_pairs))

        synthesizer = BottomUpSearch(string_variables, integer_variables, io_pairs)
        p, num = synthesizer.synthesize(8, dsl_functions,
                                        string_literals,
                                        integer_literals,
                                        boolean_literals,
                                        string_variables,
                                        integer_variables)

        generate_training_data(synthesizer, training_data_set, io_pairs, string_variables)
        logging.info("end time: " + str(datetime.now()))
        logging.info("Time taken: " + str(datetime.now() - begin_time))

    logging.info("total generation time: " + str(datetime.now() - start_time))
    logging.info("training dataset size: " + str(len(training_data_set)))
    dataFrame = pd.DataFrame(training_data_set)

    logging.info("dataframe size: " + str(dataFrame.shape[0]))
    logging.info("Saving the training data to csv file...")
    dataFrame.to_csv(training_data_filename, index=False, mode='a',
                     header=not os.path.exists(training_data_filename))
