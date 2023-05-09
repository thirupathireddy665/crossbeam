import json
import logging
import os
import pickle
from datetime import datetime

import synthetic_task
from bustle_top_down_string_dsl import *
from bustle_random_strings import *


class ProgramList:

    def __init__(self, is_complete_top_down_tree=False):
        self.plist = {}
        self.is_complete_tree = is_complete_top_down_tree
        self.terminals_bank = {}
        self.dsl_rules_map = {}

    def insert(self, program):
        if program.size not in self.plist:
            self.plist[program.size] = []

        self.plist[program.size].append(program)

    def init_operations(self, dsl_rules):
        for dsl_rule in dsl_rules:
            if dsl_rule.getReturnType() not in self.dsl_rules_map:
                self.dsl_rules_map[dsl_rule.getReturnType()] = []
            self.dsl_rules_map[dsl_rule.getReturnType()].append(dsl_rule)

    def init_plist(self, string_literals_list, integer_literals_list, boolean_literals_list,
                   string_variables_list, integer_variables_list):

        for string_literal in string_literals_list:
            if STR_TYPES['type'] not in self.terminals_bank:
                self.terminals_bank[STR_TYPES['type']] = []
            self.terminals_bank[STR_TYPES['type']].append(StrLiteral(string_literal))

        for integer_literal in integer_literals_list:
            if INT_TYPES['type'] not in self.terminals_bank:
                self.terminals_bank[INT_TYPES['type']] = []
            self.terminals_bank[INT_TYPES['type']].append(IntLiteral(integer_literal))

        for boolean_literal in boolean_literals_list:
            if BOOL_TYPES['type'] not in self.terminals_bank:
                self.terminals_bank[BOOL_TYPES['type']] = []
            self.terminals_bank[BOOL_TYPES['type']].append(BoolLiteral(boolean_literal))

        for str_var in string_variables_list:
            if STR_TYPES['type'] not in self.terminals_bank:
                self.terminals_bank[STR_TYPES['type']] = []
            self.terminals_bank[STR_TYPES['type']].append(StrVar(str_var))

        for int_var in integer_variables_list:
            if INT_TYPES['type'] not in self.terminals_bank:
                self.terminals_bank[INT_TYPES['type']] = []
            self.terminals_bank[INT_TYPES['type']].append(IntVar(int_var))

    def get_programs_all(self, size):

        if size in self.plist:
            return self.plist[size]
        else:
            return []

    def generate_program(self, return_type, height):

        complete_with_terminal = random.choice([True, False])

        if height == 1:
            if not self.terminals_bank[return_type]:
                return None
            return random.choice(self.terminals_bank[return_type])
        else:
            if self.is_complete_tree:
                random_dsl_rule = random.choice(self.dsl_rules_map[return_type])
                return random_dsl_rule.grow(height - 1)
            else:
                if self.terminals_bank[return_type] and complete_with_terminal:
                    return random.choice(self.terminals_bank[return_type])
                else:
                    random_dsl_rule = random.choice(self.dsl_rules_map[return_type])
                    return random_dsl_rule.grow(height - 1)


class TopDownSearch:

    def __init__(self, string_variables_list, integer_variables_list, input_output, is_complete_top_down_tree=False):
        self.is_complete_tree = is_complete_top_down_tree
        self._variables = string_variables_list + integer_variables_list
        self._input_output = input_output
        self.plist = ProgramList(is_complete_top_down_tree)
        self._outputs = set()
        self.closed_list = set()
        BustlePCFG.initialize(self.plist)

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

    def grow(self, height, number_of_programs):
        program_count = 0
        while program_count < number_of_programs:
            program_made = self.plist.generate_program(STR_TYPES['type'], height)
            if program_made and program_made.toString() not in self.closed_list and not self.has_equivalent(
                    program_made):
                self.closed_list.add(program_made.toString())
                program_made.size = height
                self.plist.insert(program_made)
                program_count += 1
                logging.info("height: " + str(height) + " program count: " + str(program_count))
                # logging.info("program: " + program_made.toString())

    def search(self, max_program_height, operations, string_literals_list, integer_literals_list,
               boolean_literals_list, string_variables_list,
               integer_variables_list, number_of_programs):

        self.plist.init_operations(operations)
        self.plist.init_plist(string_literals_list, integer_literals_list, boolean_literals_list, string_variables_list,
                              integer_variables_list)

        current_height = 3

        while current_height <= max_program_height:
            self.grow(current_height, number_of_programs)
            current_height += 1

    def synthesize(self, bound, operations, string_literals_list, integer_literals_list,
                   boolean_literals_list, string_variables_list,
                   integer_variables_list, number_of_programs):

        self.search(bound, operations, string_literals_list, integer_literals_list,
                    boolean_literals_list,
                    string_variables_list, integer_variables_list, number_of_programs)


def save_object(obj, pickle_filename):
    os.makedirs(os.path.dirname(pickle_filename), exist_ok=True)
    with open(pickle_filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output)


def get_synthetic_task(task_number):
    task_filename = task_files_directory + "synthetic_task_" + str(task_number) + ".pkl"
    with open(task_filename, 'rb') as task_input:
        property_object = pickle.load(task_input)
        return property_object


def load_from_json(pruning_data_filename):
    prune_file = open(pruning_data_filename)
    return json.load(prune_file)


if __name__ == "__main__":

    log_filename = logs_directory + "synthetic_task_generator.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    logging.basicConfig(filename=log_filename,
                        filemode='a',
                        format='%(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    number_of_test_specifications = 50
    number_of_string_variables = None
    number_of_examples = None
    benchmark = None
    task_index = 0

    for test_data_index in range(0, number_of_test_specifications):

        number_of_string_variables = random.randint(2, 3)
        number_of_examples = random.randint(2, 4)
        input_specifications = bustle_inputs_dict_generator(number_of_string_variables, number_of_examples)

        dsl_functions = [StrConcat, StrReplace,
                         StrSubstr, StrIte, StrIntToStr, StrCharAt, StrTrim, StrLower,
                         StrUpper, StrLeftSubstr, StrRightSubstr,
                         StrReplaceMulti, StrReplaceAdd, IntStrToInt, IntPlus,
                         IntMinus, IntLength, IntIteInt, IntIndexOf, IntFirstIndexOf, BoolEqual, BoolContain,
                         BoolSuffixof, BoolPrefixof, BoolGreaterThan, BoolGreaterThanEqual]

        string_variables = list(input_specifications.keys())
        string_literals = ['', '/', ' ', ',', '-', '.', '+', '_', '@', '$']
        integer_variables = []
        integer_literals = [0, 1, 2, 3]
        boolean_literals = [True, False]
        is_complete_tree = True
        max_height = 10  # 20
        max_programs = 50
        input_output_examples = []

        for input_index in range(0, number_of_examples):
            input_output_example = {}
            for string_variable in string_variables:
                input_output_example[string_variable] = input_specifications[string_variable][input_index]
            input_output_examples.append(input_output_example)

        training_data_set = []
        start_time = datetime.now()
        logging.info("generation start time: " + str(start_time))

        synthesizer = TopDownSearch(string_variables, integer_variables, input_output_examples, is_complete_tree)
        synthesizer.synthesize(max_height, dsl_functions,
                               string_literals,
                               integer_literals,
                               boolean_literals,
                               string_variables,
                               integer_variables,
                               max_programs)

        # Select 3-10 height programs as random tasks
        task_height_range = list(range(3, max_height + 1))
        random_programs = []

        for task_height in task_height_range:
            valid_programs = []
            string_return_programs = list(filter(lambda new_program: new_program.getReturnType() == STR_TYPES['type'],
                                                 synthesizer.plist.get_programs_all(task_height)))
            for program in string_return_programs:
                for string_variable in string_variables:
                    if string_variable in program.toString():
                        valid_programs.append(program)
                        break

            random_programs.append(random.choice(valid_programs))

        for program in random_programs:

            program_string = program.toString()

            new_specifications = []
            new_string_variables = []
            new_string_literals = []
            new_integer_variables = []
            new_integer_literals = []
            new_input_output_examples = []

            for string_variable in string_variables:
                if string_variable in program_string:
                    new_string_variables.append(string_variable)

            for string_literal in string_literals:
                if string_literal in program_string:
                    new_string_literals.append(string_literal)

            for integer_variable in integer_variables:
                if integer_variable in program_string:
                    new_integer_variables.append(integer_variable)

            for integer_literal in integer_literals:
                if str(integer_literal) in program_string:
                    new_integer_literals.append(int(integer_literal))

            for input_output_example in input_output_examples:

                io_example = {}
                for string_variable in new_string_variables:
                    io_example[string_variable] = input_output_example[string_variable]

                for integer_variable in new_integer_variables:
                    io_example[integer_variable] = input_output_example[integer_variable]

                io_example['out'] = program.interpret(input_output_example)
                new_input_output_examples.append(io_example)

            new_specifications.append(new_string_variables)
            new_specifications.append(new_string_literals)
            new_specifications.append(new_integer_variables)
            new_specifications.append(new_integer_literals)
            new_specifications.append(new_input_output_examples)

            new_synthetic_task = synthetic_task.SyntheticTask(program, new_specifications)

            task_object_filename = task_files_directory + "synthetic_task_" + str(task_index + 1) + ".pkl"
            task_index += 1
            save_object(new_synthetic_task, task_object_filename)
