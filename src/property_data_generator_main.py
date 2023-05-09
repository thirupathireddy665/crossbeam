from bustle_string_dsl import *
from sygus_parser import StrParser
import logging
import random
import pandas as pd
from bustle_generated_properties import *
from utils import *
from datetime import datetime
import os
import sys


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
            program = StrLiteral(string_literal)
            self.insert(program)

        for integer_literal in integer_literals_list:
            program = IntLiteral(integer_literal)
            self.insert(program)

        for boolean_literal in boolean_literals_list:
            program = BoolLiteral(boolean_literal)
            self.insert(program)

        for str_var in string_variables_list:
            program = StrVar(str_var)
            self.insert(program)

        for int_var in integer_variables_list:
            program = IntVar(int_var)
            self.insert(program)

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
            for program in op.grow(self.plist, size):
                if program.toString() not in self.closed_list and not self.has_equivalent(program):
                    self.closed_list.add(program)
                    new_programs.append(program)
                    yield program

        for program in new_programs:
            self.plist.insert(program)

    def search(self, bound, operations, string_literals_list, integer_literals_list, boolean_literals_list,
               string_variables_list, integer_variables_list):

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
                   boolean_literals_list,
                   string_variables_list, integer_variables_list):

        BustlePCFG.initialize(operations, string_literals_list, integer_literals_list, boolean_literals_list,
                              string_variables_list, integer_variables_list)

        solution, evaluations = self.search(bound, operations, string_literals_list, integer_literals_list,
                                            boolean_literals_list, string_variables_list, integer_variables_list)

        return solution, evaluations


def generate_property_data(search_synthesizer, gen_property_data_set, random_inputs, string_variables_list):
    programs = []

    for program_size in range(5, 10):
        programs.extend(search_synthesizer.plist.get_programs(program_size, STR_TYPES['type']))

    sample_programs = set()

    while len(sample_programs) <= 2000:

        number_of_string_variables_in_program = 0
        program = random.choice(programs)

        for string_variable in string_variables_list:
            if string_variable in program.toString():
                number_of_string_variables_in_program += 1

        if number_of_string_variables_in_program == 1 and program not in sample_programs:

            sample_programs.add(program)

            parent_input_outputs = []

            for random_input in random_inputs:
                input_output = random_input.copy()
                output = program.interpret(input_output)
                input_output['out'] = output
                parent_input_outputs.append(input_output)

            property_data_point = {}

            for property_index, property_t in enumerate(InputStringOutputStringProperties):
                property_value = property_t(parent_input_outputs, string_variable)
                property_data_point["prop" + str(property_index)] = property_value

            property_data_point["program"] = program.toString().replace(string_variable, "arg")
            gen_property_data_set.append(property_data_point)


if __name__ == "__main__":

    property_filename = property_data_directory+"property_data.csv"
    os.makedirs(os.path.dirname(property_filename), exist_ok=True)

    log_filename = logs_directory+"property_data_generator.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    if len(sys.argv) == 2:
        slurm_task_id = sys.argv[1]
        property_filename = property_data_directory+"property_data_" + str(slurm_task_id) + ".csv"
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

    with open(config_directory+"bustle_benchmarks.txt") as f:
        benchmarks = f.read().splitlines()

    benchmark = None
    random_strings = set()

    for benchmark in benchmarks:
        specification_parser = StrParser(benchmark)
        specifications = specification_parser.parse()

        string_variables = specifications[0]
        for variable in string_variables:
            for io_example in specifications[4]:
                random_strings.add(io_example[variable])

    random_strings_list = list(random_strings)

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

    number_of_io_pairs = random.choice([1, 2, 3, 4])

    training_data_set = []
    property_data_set = []

    for search_index in range(0, 1):

        begin_time = datetime.now()
        logging.info("start time: " + str(datetime.now()))
        arg0 = random.sample(random_strings_list, number_of_io_pairs)
        arg1 = random.sample(random_strings_list, number_of_io_pairs)
        arg2 = random.sample(random_strings_list, number_of_io_pairs)

        io_pairs = []

        for index in range(number_of_io_pairs):
            io_pair = {'arg0': arg0[index], 'arg1': arg1[index], 'arg2': arg2[index]}
            io_pairs.append(io_pair)

        logging.info("examples: " + str(io_pairs))

        synthesizer = BottomUpSearch(string_variables, integer_variables, io_pairs)
        p, num = synthesizer.synthesize(7, dsl_functions,
                                        string_literals,
                                        integer_literals,
                                        boolean_literals,
                                        string_variables,
                                        integer_variables)

        generate_property_data(synthesizer, property_data_set, io_pairs, string_variables)
        logging.info("end time: " + str(datetime.now()))
        logging.info("Time taken: " + str(datetime.now() - begin_time))

    logging.info("property dataset size: " + str(len(property_data_set)))
    property_dataFrame = pd.DataFrame(property_data_set)
    logging.info("Saving the property data to csv file...")
    property_dataFrame.to_csv(property_filename, index=False, mode='a', header=not os.path.exists(property_filename))
