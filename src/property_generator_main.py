from bustle_string_dsl import *
from utils import *
import logging
import sys
import pickle
import os


class ProgramList:

    def __init__(self):
        self.plist = {}
        self.number_programs = 0

    def insert(self, new_program):

        if new_program.size not in self.plist:
            self.plist[new_program.size] = {}

        if new_program.getReturnType() not in self.plist[new_program.size]:
            self.plist[new_program.size][new_program.getReturnType()] = []

        self.plist[new_program.size][new_program.getReturnType()].append(new_program)
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

    def get_programs_all(self, programs_size):

        if programs_size in self.plist:
            programs_list = []
            for value in self.plist[programs_size].values():
                programs_list.extend(value)
            return programs_list

        return []

    def get_programs(self, desired_program_size, return_type):

        if desired_program_size in self.plist:
            if return_type in self.plist[desired_program_size]:
                return self.plist[desired_program_size][return_type]

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

    def has_equivalent(self, equivalent_program):
        p_out = []
        for inout in self._input_output:
            env = self.init_env(inout)
            out = equivalent_program.interpret(env)
            if out is not None:
                p_out.append(out)
            else:
                return True

        tuple_out = tuple(p_out)

        if tuple_out not in self._outputs:
            self._outputs.add(tuple_out)
            return False
        return True

    def grow(self, operations, current_program_size):
        new_programs = []
        for op in operations:
            for new_program in op.grow(self.plist, current_program_size):
                if new_program.toString() not in self.closed_list and not self.has_equivalent(new_program):
                    self.closed_list.add(new_program)
                    new_programs.append(new_program)
                    yield new_program

        for new_program in new_programs:
            self.plist.insert(new_program)

    def search(self, bound, operations, string_literals_list, integer_literals_list,
               boolean_literals_list, string_variables_list, integer_variables_list):

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

    def synthesize(self, bound, operations, string_literals_list, integer_literals_list, boolean_literals_list,
                   string_variables_list, integer_variables_list):

        BustlePCFG.initialize(operations, string_literals_list, integer_literals_list, boolean_literals_list,
                              string_variables_list, integer_variables_list)

        solution, evaluations = self.search(bound, operations, string_literals_list, integer_literals_list,
                                            boolean_literals_list, string_variables_list, integer_variables_list)

        return solution, evaluations


def save_object(obj, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as outp:  # Overwrites any existing file.
        pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":

    log_filename = logs_directory+"property_generator.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

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
                     StrUpper,
                     StrReplaceMulti, StrReplaceAdd, IntStrToInt, IntPlus,
                     IntMinus, IntLength, IntIteInt, IntIndexOf, IntFirstIndexOf, BoolEqual, BoolContain,
                     BoolSuffixof, BoolPrefixof, BoolGreaterThan, BoolGreaterThanEqual]

    string_literals = ['', '/', ' ', ',', '-', '.']
    string_variables = ['arg']
    integer_variables = []
    integer_literals = [0, 1, 2, 3]
    boolean_literals = [True, False]

    # Program Dataset generation used for property filtering based on their distinguishability
    io_pairs = []
    number_of_io_pairs = 2

    for index in range(0, number_of_io_pairs):
        io_pair = {string_variables[0]: "randomstring" + str(index)}
        io_pairs.append(io_pair)

    synthesizer = BottomUpSearch(string_variables, integer_variables, io_pairs)
    task_solution, num_evaluations = synthesizer.synthesize(18, dsl_functions, [], [], [],
                                                            string_variables,
                                                            integer_variables)

    programs_using_arg = []
    required_program_set_size = 10000
    program_count_so_far = 0

    for program_size in range(0, 19):
        if program_count_so_far >= required_program_set_size:
            break
        string_programs = synthesizer.plist.get_programs(program_size, STR_TYPES['type'])
        for string_program in string_programs:
            if string_variables[0] in string_program.toString():
                programs_using_arg.append(string_program)
                program_count_so_far += 1
                if program_count_so_far >= required_program_set_size:
                    break

    programs_outputs = []
    for program in programs_using_arg:
        outputs = []
        for io_pair in io_pairs:
            output = program.interpret(io_pair)
            outputs.append(output)
        programs_outputs.append(outputs)

    # Properties generation
    input_string_programs = []
    input_integer_programs = []

    for program_size in range(0, 5):
        string_programs = synthesizer.plist.get_programs(program_size, STR_TYPES['type'])
        integer_programs = synthesizer.plist.get_programs(program_size, INT_TYPES['type'])
        for string_program in string_programs:
            if string_variables[0] in string_program.toString():
                input_string_programs.append(string_program)
        for integer_program in integer_programs:
            if string_variables[0] in integer_program.toString():
                input_integer_programs.append(integer_program)

    string_variables = ['out']
    io_pairs = []
    number_of_io_pairs = 2

    for index in range(0, number_of_io_pairs):
        io_pair = {string_variables[0]: "randomstring" + str(index)}
        io_pairs.append(io_pair)

    synthesizer = BottomUpSearch(string_variables, integer_variables, io_pairs)
    task_solution, num_evaluations = synthesizer.synthesize(4, dsl_functions, [], [], [],
                                                            string_variables,
                                                            integer_variables)

    output_string_programs = []
    output_integer_programs = []

    for program_size in range(0, 5):
        string_programs = synthesizer.plist.get_programs(program_size, STR_TYPES['type'])
        integer_programs = synthesizer.plist.get_programs(program_size, INT_TYPES['type'])
        for string_program in string_programs:
            if string_variables[0] in string_program.toString():
                output_string_programs.append(string_program)
        for integer_program in integer_programs:
            if string_variables[0] in integer_program.toString():
                output_integer_programs.append(integer_program)

    string_boolean_rules = [BoolEqual, BoolContain, BoolSuffixof, BoolPrefixof]
    integer_boolean_rules = [BoolEqual, BoolGreaterThan, BoolGreaterThanEqual]

    properties = []

    for input_string_program in input_string_programs:
        for output_string_program in output_string_programs:
            for string_boolean_rule in string_boolean_rules:
                properties.append(string_boolean_rule(input_string_program, output_string_program))
                if string_boolean_rule != BoolEqual:
                    properties.append(string_boolean_rule(output_string_program, input_string_program))

    for input_integer_program in input_integer_programs:
        for output_integer_program in output_integer_programs:
            for integer_boolean_rule in integer_boolean_rules:
                properties.append(integer_boolean_rule(input_integer_program, output_integer_program))

    # Filtering the generated properties using the Program Dataset

    filtered_properties = []
    property_input = 'arg'
    property_output = 'out'

    random_input_strings = []
    for index in range(0, number_of_io_pairs):
        random_input_strings.append("randomstring" + str(index))

    for property_t in properties:
        output_set = set()
        for programs_output in programs_outputs:
            property_values = []
            for index in range(0, number_of_io_pairs):
                property_env = {property_input: random_input_strings[index], property_output: programs_output[index]}
                property_values.append(property_t.interpret(property_env))
            property_values_set = set(property_values)
            if len(property_values_set) == 1:
                if True in property_values_set:
                    output_set.add(-1)
                if False in property_values_set:
                    output_set.add(0)
            else:
                output_set.add(1)
        if len(output_set) > 1:
            filtered_properties.append(property_t)

    print("Number of properties: ", len(filtered_properties))
    filtered_properties.sort(key=lambda property_f: property_f.size)

    for index in range(0, 100):
        save_object(filtered_properties[index], pickle_files_directory+"prop"+str(index)+".pkl")
