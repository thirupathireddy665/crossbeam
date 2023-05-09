import logging
import os
import sys
from datetime import datetime

import numpy as np
import tensorflow.keras.models as keras_model

from bustle_properties import *
from sygus_dsl import *
# from bustle_string_dsl import * 
from sygus_parser import StrParser
from utils import *

from string import punctuation
from bm_38_parser import StrParser38 

# ARE_38_TASKS = ?
ARE_38_TASKS = True

def populate_property_value(property_signature, property_encoding):
    for encoding in property_encoding:
        property_signature.append(encoding)


class ProgramList:

    def __init__(self, string_variables_list, integer_variables_list, input_output):
        self.plist = {}
        self.number_programs = 0
        self.parent_input_output = input_output
        self.string_variables = string_variables_list
        self.integer_variables = integer_variables_list
        self.parent_ps = []
        self.batch_jobs = []
        self.property_encodings = {
            AllTrue: EncodedAllTrue,
            AllFalse: EncodedAllFalse,
            Mixed: EncodedMixed,
            Padding: EncodedPadding
        }

        max_string_variables = 4
        max_integer_variables = 1

        """

        Property Signature composition:

                main_program:

                1. input strings with string only properties (4*14 = 56)
                2. input integer with integer only properties (1*7 = 7)
                3. output string with string only properties (1*14 = 14)
                4. output integer with integer only properties (1*7 = 7)
                5. output boolean with boolean only properties (1*1 = 1)
                6. input integer and output string with integer-string properties (1*7 =7)
                7. input integer and output integer with integer-integer properties (1*13 = 13)
                8. input integer and output boolean with integer-boolean properties (1*3 = 3)
                9. input strings and output string with string-string properties (4*17 = 68)
                10. input strings and output integer with string-integer properties (4*7 = 28)
                11. input strings and output boolean with string-boolean properties (4*3 = 12)

                sub_program:

                12. boolean output with boolean only properties (1*1 = 1)
                13. integer output with integer only properties (1*7 = 7)
                14. string output with string only properties (1*14 = 14)
                15. integer output and string output of main program with integer-string properties (1*7 = 7)
                16. string output and string output of main program with string-string properties (1*17 = 17)
                17. integer output and integer output of main program with integer-string properties (1*13 = 13)
                18. string output and integer output of main program with string-string properties (1*7 = 7)
                19. integer output and boolean output of main program with integer-bool properties (1*3 = 3)
                20. string output and boolean output of main program with string-bool properties (1*3 = 3)

        """
        # input strings with string only properties
        for string_variable in string_variables_list:
            input_strings = [parent_input.get(string_variable) for parent_input in self.parent_input_output]
            for StringProperty in StringProperties:
                property_value = StringProperty(input_strings)
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        for padding_index in range(0, max_string_variables - len(string_variables_list)):
            for _ in StringProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        # input integer with integer only properties
        for integer_variable in integer_variables_list:
            input_integers = [parent_input.get(integer_variable) for parent_input in self.parent_input_output]
            for IntegerProperty in IntegerProperties:
                property_value = IntegerProperty(input_integers)
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        for padding_index in range(0, max_integer_variables - len(integer_variables_list)):
            for _ in IntegerProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        task_outputs = [parent_output['out'] for parent_output in self.parent_input_output]
        output_type = "str"
        if isinstance(task_outputs[0], int):
            output_type = "int"
        elif isinstance(task_outputs[0], bool):
            output_type = "bool"

        self.parent_output_type = output_type

        # output string with string only properties
        output_strings = [parent_output['out'] for parent_output in self.parent_input_output]
        if output_type == "str":
            for StringProperty in StringProperties:
                property_value = StringProperty(output_strings)
                populate_property_value(self.parent_ps, self.property_encodings[property_value])
        else:
            for _ in StringProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        # output integer with integer only properties
        output_integers = [parent_output['out'] for parent_output in self.parent_input_output]
        if output_type == "int":
            for IntegerProperty in IntegerProperties:
                property_value = IntegerProperty(output_integers)
                populate_property_value(self.parent_ps, self.property_encodings[property_value])
        else:
            for _ in IntegerProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        # output boolean with boolean only properties
        output_bools = [parent_output['out'] for parent_output in self.parent_input_output]
        if output_type == "bool":
            for BooleanProperty in BooleanProperties:
                property_value = BooleanProperty(output_bools)
                populate_property_value(self.parent_ps, self.property_encodings[property_value])
        else:
            for _ in BooleanProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        # input integer and output string with integer-string properties
        for integer_variable in integer_variables_list:
            if output_type == "str":
                for InputIntegerOutputStringProperty in InputIntegerOutputStringProperties:
                    property_value = InputIntegerOutputStringProperty(self.parent_input_output, integer_variable)
                    populate_property_value(self.parent_ps, self.property_encodings[property_value])
            else:
                for _ in InputIntegerOutputStringProperties:
                    property_value = Padding
                    populate_property_value(self.parent_ps, self.property_encodings[property_value])

        for padding_index in range(0, max_integer_variables - len(integer_variables_list)):
            for _ in InputIntegerOutputStringProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        # input integer and output integer with integer-integer properties
        for integer_variable in integer_variables_list:
            if output_type == "int":
                for InputIntegerOutputIntegerProperty in InputIntegerOutputIntegerProperties:
                    property_value = InputIntegerOutputIntegerProperty(self.parent_input_output, integer_variable)
                    populate_property_value(self.parent_ps, self.property_encodings[property_value])
            else:
                for _ in InputIntegerOutputIntegerProperties:
                    property_value = Padding
                    populate_property_value(self.parent_ps, self.property_encodings[property_value])

        for padding_index in range(0, max_integer_variables - len(integer_variables_list)):
            for _ in InputIntegerOutputIntegerProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        # input integer and output boolean with integer-boolean properties
        for integer_variable in integer_variables_list:
            if output_type == "bool":
                for InputIntegerOutputBoolProperty in InputIntegerOutputBoolProperties:
                    property_value = InputIntegerOutputBoolProperty(self.parent_input_output, integer_variable)
                    populate_property_value(self.parent_ps, self.property_encodings[property_value])
            else:
                for _ in InputIntegerOutputBoolProperties:
                    property_value = Padding
                    populate_property_value(self.parent_ps, self.property_encodings[property_value])

        for padding_index in range(0, max_integer_variables - len(integer_variables_list)):
            for _ in InputIntegerOutputBoolProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        # input strings and output string with string-string properties
        for string_variable in string_variables_list:
            if output_type == "str":
                for InputStringOutputStringProperty in InputStringOutputStringProperties:
                    property_value = InputStringOutputStringProperty(self.parent_input_output, string_variable)
                    populate_property_value(self.parent_ps, self.property_encodings[property_value])
            else:
                for _ in InputStringOutputStringProperties:
                    property_value = Padding
                    populate_property_value(self.parent_ps, self.property_encodings[property_value])

        for padding_index in range(0, max_string_variables - len(string_variables_list)):
            for _ in InputStringOutputStringProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        # input strings and output integer with string-integer properties
        for string_variable in string_variables_list:
            if output_type == "int":
                for InputStringOutputIntegerProperty in InputStringOutputIntegerProperties:
                    property_value = InputStringOutputIntegerProperty(self.parent_input_output, string_variable)
                    populate_property_value(self.parent_ps, self.property_encodings[property_value])
            else:
                for _ in InputStringOutputIntegerProperties:
                    property_value = Padding
                    populate_property_value(self.parent_ps, self.property_encodings[property_value])

        for padding_index in range(0, max_string_variables - len(string_variables_list)):
            for _ in InputStringOutputIntegerProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        # input strings and output boolean with string-bool properties
        for string_variable in string_variables_list:
            if output_type == "bool":
                for InputStringOutputBoolProperty in InputStringOutputBoolProperties:
                    property_value = InputStringOutputBoolProperty(self.parent_input_output, string_variable)
                    populate_property_value(self.parent_ps, self.property_encodings[property_value])
            else:
                for _ in InputStringOutputBoolProperties:
                    property_value = Padding
                    populate_property_value(self.parent_ps, self.property_encodings[property_value])

        for padding_index in range(0, max_string_variables - len(string_variables_list)):
            for _ in InputStringOutputBoolProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

    def insert(self, program):
        self.batch_jobs.append(program)

    def process_batch_jobs(self):

        batch_size = 100000
        total_jobs = len(self.batch_jobs)

        for job_index in range(0, total_jobs, batch_size):

            current_batch = self.batch_jobs[job_index:job_index + batch_size]
            current_batch_ps = []

            for program in current_batch:

                test_row = self.parent_ps.copy()
                child_input_outputs = []

                for index, parent_input in enumerate(self.parent_input_output):
                    child_input_output = parent_input.copy()
                    child_output = program.interpret(child_input_output)
                    child_input_output['cout'] = child_output
                    child_input_output['out'] = self.parent_input_output[index]['out']
                    child_input_outputs.append(child_input_output)

                outputs = [output['cout'] for output in child_input_outputs]

                # boolean output of subexpression with boolean only properties
                if program.getReturnType() == BOOL_TYPES['type']:
                    for BooleanProperty in BooleanProperties:
                        property_value = BooleanProperty(outputs)
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in BooleanProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                # integer output of expression with integer only properties -
                if program.getReturnType() == INT_TYPES['type']:
                    for IntegerProperty in IntegerProperties:
                        property_value = IntegerProperty(outputs)
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in IntegerProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                # string output of subexpression with string only properties
                if program.getReturnType() == STR_TYPES['type']:
                    for StringProperty in StringProperties:
                        property_value = StringProperty(outputs)
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in StringProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                # integer output of subexpression and string output of main expression with integer-string properties
                if program.getReturnType() == INT_TYPES['type'] and self.parent_output_type == "str":
                    for InputIntegerOutputStringProperty in InputIntegerOutputStringProperties:
                        property_value = InputIntegerOutputStringProperty(child_input_outputs, 'cout')
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in InputIntegerOutputStringProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                # string output of subexpression and string output of main expression with string-string properties
                if program.getReturnType() == STR_TYPES['type'] and self.parent_output_type == "str":
                    for InputStringOutputStringProperty in InputStringOutputStringProperties:
                        property_value = InputStringOutputStringProperty(child_input_outputs, 'cout')
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in InputStringOutputStringProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                # integer output of subexpression and integer output of main expression with integer-integer properties
                if program.getReturnType() == INT_TYPES['type'] and self.parent_output_type == "int":
                    for InputIntegerOutputIntegerProperty in InputIntegerOutputIntegerProperties:
                        property_value = InputIntegerOutputIntegerProperty(child_input_outputs, 'cout')
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in InputIntegerOutputIntegerProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                # string output of subexpression and integer output of main expression with string-integer properties
                if program.getReturnType() == STR_TYPES['type'] and self.parent_output_type == "int":
                    for InputStringOutputIntegerProperty in InputStringOutputIntegerProperties:
                        property_value = InputStringOutputIntegerProperty(child_input_outputs, 'cout')
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in InputStringOutputIntegerProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                # integer output of subexpression and boolean output of main expression with integer-bool properties
                if program.getReturnType() == INT_TYPES['type'] and self.parent_output_type == "bool":
                    for InputIntegerOutputBoolProperty in InputIntegerOutputBoolProperties:
                        property_value = InputIntegerOutputBoolProperty(child_input_outputs, 'cout')
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in InputIntegerOutputBoolProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                # string output of subexpression and boolean output of main expression with string-bool properties
                if program.getReturnType() == STR_TYPES['type'] and self.parent_output_type == "bool":
                    for InputStringOutputBoolProperty in InputStringOutputBoolProperties:
                        property_value = InputStringOutputBoolProperty(child_input_outputs, 'cout')
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in InputStringOutputBoolProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                current_batch_ps.append(test_row)

            current_batch_predictions = BustleModel.predict(np.array(current_batch_ps))

            for program_index, program in enumerate(current_batch):

                program_size = program.size

                # Reweighing the size of the program as per BUSTLE algorithm using the neural model

                program_probability = current_batch_predictions[program_index]

                if program_probability <= 0.1:
                    program_size += 5
                elif program_probability <= 0.2:
                    program_size += 4
                elif program_probability <= 0.3:
                    program_size += 3
                elif program_probability <= 0.4:
                    program_size += 2
                elif program_probability <= 0.6:
                    program_size += 1

                # if program_probability <= 0.1:
                #     program_size += 9
                # elif program_probability <= 0.2:
                #     program_size += 8
                # elif program_probability <= 0.3:
                #     program_size += 7
                # elif program_probability <= 0.4:
                #     program_size += 6
                # elif program_probability <= 0.5:
                #     program_size += 5
                # elif program_probability <= 0.6:
                #     program_size += 4
                # elif program_probability <= 0.7:
                #     program_size += 3
                # elif program_probability <= 0.8:
                #     program_size += 2
                # elif program_probability <= 0.9:
                #     program_size += 1

                program.size = program_size

                if program.size not in self.plist:
                    self.plist[program.size] = {}

                if program.getReturnType() not in self.plist[program.size]:
                    self.plist[program.size][program.getReturnType()] = []

                self.plist[program.size][program.getReturnType()].append(program)
                self.number_programs += 1

        self.batch_jobs.clear()

    def init_insert(self, program):

        if program.size not in self.plist:
            self.plist[program.size] = {}

        if program.getReturnType() not in self.plist[program.size]:
            self.plist[program.size][program.getReturnType()] = []

        self.plist[program.size][program.getReturnType()].append(program)
        self.number_programs += 1

    def init_plist(self, string_literals_list, integer_literals_list, boolean_literals,
                   string_variables_list, integer_variables_list):
        for string_literal in string_literals_list:
            init_program = StrLiteral(string_literal)
            self.init_insert(init_program)

        for integer_literal in integer_literals_list:
            init_program = IntLiteral(integer_literal)
            self.init_insert(init_program)

        for boolean_literal in boolean_literals:
            init_program = BoolLiteral(boolean_literal)
            self.init_insert(init_program)

        for str_var in string_variables_list:
            init_program = StrVar(str_var)
            self.init_insert(init_program)

        for int_var in integer_variables_list:
            init_program = IntVar(int_var)
            self.init_insert(init_program)

        # self.process_batch_jobs()

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
        self.plist = ProgramList(string_variables_list, integer_variables_list, input_output)
        self._outputs = set()
        self.closed_list = set()
        self.number_evaluations = 0

    def is_correct(self, p):
        is_program_correct = True

        for inout in self._input_output:
            env = self.init_env(inout)
            out = p.interpret(env)
            if out != inout['out']:
                is_program_correct = False

        return is_program_correct

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
        for operation in operations:
            for new_program in operation.grow(self.plist, size):
                self.number_evaluations += 1
                if new_program.toString() not in self.closed_list and not self.has_equivalent(new_program):
                    self.closed_list.add(new_program)
                    new_programs.append(new_program)
                    yield new_program

        for new_program in new_programs:
            self.plist.insert(new_program)

        self.plist.process_batch_jobs()

    def search(self, bound, operations, string_literals_list, integer_literals_list,
               boolean_literals, string_variables_list,
               integer_variables_list):

        self.plist.init_plist(string_literals_list, integer_literals_list, boolean_literals, string_variables_list,
                              integer_variables_list)

        logging.info('Number of programs: ' + str(self.plist.get_number_programs()))

        number_evaluations = 0
        current_size = 0

        while current_size <= bound:

            number_evaluations_bound = 0

            for new_program in self.grow(operations, current_size):
                number_evaluations += 1
                number_evaluations_bound += 1
                is_p_correct = self.is_correct(new_program)
                if is_p_correct:
                    return new_program, self.number_evaluations

            logging.info('Size: ' + str(current_size) + ' Evaluations: ' + str(number_evaluations_bound))
            current_size += 1

        return None, self.number_evaluations

    def synthesize(self, bound, operations, string_literals_list, integer_literals_list,
                   boolean_literals, string_variables_list,
                   integer_variables_list):

        BustlePCFG.initialize(operations, string_literals_list, integer_literals_list, boolean_literals,
                              string_variables_list,
                              integer_variables_list)

        program_solution, evaluations = self.search(bound, operations, string_literals_list, integer_literals_list,
                                                    boolean_literals, string_variables_list, integer_variables_list)

        return program_solution, evaluations


def load_bustle_model():
    logging.info("Loading bustle model....")
    global BustleModel
    model_filename = models_directory + "all_sygus_0" + sys.argv[2] + ".hdf5"
    os.makedirs(os.path.dirname(model_filename), exist_ok=True)
    BustleModel = keras_model.load_model(model_filename)


if __name__ == "__main__":

    TaskId = None
    log_filename = logs_directory + sys.argv[2] + "/easy.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    if len(sys.argv) == 3:
        slurm_task_id = sys.argv[1]
        TaskId = int(slurm_task_id) - 1
        logging.basicConfig(filename=log_filename,
                            filemode='a',
                            format="[Task: " + str(TaskId) + "] " + '%(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
    else:
        logging.basicConfig(filename=log_filename,
                            filemode='a',
                            format='%(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

    load_bustle_model()
    # return
    # with open("simple_benchmarks_bustle.txt") as f:
    with open(config_directory + "sygus_string_benchmarks.txt") as f:
        benchmarks = f.read().splitlines()
        string_variables = []
        string_literals = []
        integer_variables = []
        integer_literals = []

    accumulate_all = True

    if accumulate_all:
        for index, filename in enumerate(benchmarks):
            specification_parser = StrParser(filename)
            specifications = specification_parser.parse()
            string_variables = list(set(string_variables + specifications[0]))
            string_literals = list(set(string_literals + specifications[1]))
            integer_variables = list(set(integer_variables + specifications[2]))
            integer_literals = list(set(integer_literals + specifications[3]))

    # all_int_literals = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -2, -3, -4, -5, -6, -7, -8, -9]
    # string_literals = list(set(string_literals + all_str_literals))
    # integer_literals = list(set(integer_literals + all_int_literals))
    if(accumulate_all):
        lowercase_alphabets = set(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'])
        uppercase_alphabets = set(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
        string_literals = list(set(string_literals).union(lowercase_alphabets))
        string_literals = list(set(string_literals).union(uppercase_alphabets))
    
        # Do not forget to turn on ARE_38_TASKS flag on the top of the file.
    if(ARE_38_TASKS):
        # Get list of all entries in bustle_38.txt file.
        new_benchmarks = open(config_directory + "bustle_38.txt", "r")
        benchmarks = new_benchmarks.read().splitlines()
        new_benchmarks.close()

    benchmark = None
    for count, filename in enumerate(benchmarks):

        if TaskId is not None and TaskId != count:
            continue

        benchmark = filename

        specification_parser = StrParser(benchmark) if not ARE_38_TASKS else StrParser38(benchmark)
        specifications = specification_parser.parse()
        logging.info('Count: ' + str(count))
        logging.info("\n")

        # Sygus Grammar.
        dsl_functions = [StrConcat, StrReplace, StrSubstr, StrIte, StrIntToStr, StrCharAt, StrLower, StrUpper, IntStrToInt,
                    IntPlus, IntMinus, IntLength, IntIteInt, IntIndexOf, IntFirstIndexOf, IntMultiply, IntModulo, 
                    BoolEqual, BoolContain, BoolSuffixof, BoolPrefixof, BoolGreaterThan, BoolLessThan]

        # BUSTLE grammar.
#         dsl_functions = [StrConcat, StrReplace,
#                      StrSubstr, StrIte, StrIntToStr, StrCharAt, StrTrim, StrLower,
#                      StrUpper, StrLeftSubstr, StrRightSubstr,
#                      StrReplaceMulti, StrReplaceAdd, IntStrToInt, IntPlus,
#                      IntMinus, IntLength, IntIteInt, IntIndexOf, IntFirstIndexOf, BoolEqual, BoolContain,
#                      BoolSuffixof, BoolPrefixof, BoolGreaterThan, BoolGreaterThanEqual]

        if (not accumulate_all):
            string_variables = specifications[0]
            string_literals = specifications[1]
            integer_variables = specifications[2]
            integer_literals = specifications[3]
        else:
            string_literals = list(set(specifications[1] + string_literals))
            integer_literals = list(set(specifications[3] + integer_literals))
            string_variables = specifications[0]
            integer_variables = specifications[2]

        input_output_examples = specifications[4]

        synthesizer = BottomUpSearch(string_variables, integer_variables, input_output_examples)
        logging.info(str(datetime.now()))
        begin_time = datetime.now()
        solution, num = synthesizer.synthesize(40, dsl_functions,
                                               string_literals,
                                               integer_literals,
                                               [True, False],
                                               string_variables,
                                               integer_variables)

        # print(synthesizer.plist.get_number_programs())
        if solution is not None:
            logging.info("Benchmark: " + str(benchmark))
            logging.info("Result: Success")
            logging.info("Program: " + solution.toString())
            logging.info("Number of evaluations: " + str(num))
            logging.info(str(datetime.now()))
            logging.info("Time taken: " + str(datetime.now() - begin_time))
        else:
            logging.info("Benchmark: " + str(benchmark))
            logging.info("Result: Fail")
            logging.info("Program: None")
            logging.info("Number of evaluations: " + str(num))
            logging.info(str(datetime.now()))
            logging.info("Time taken: " + str(datetime.now() - begin_time))

        logging.info("\n\n")
