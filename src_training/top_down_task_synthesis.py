import logging
import os
import random
import sys
from datetime import datetime

import numpy as np
import tensorflow.keras.models as keras_model
import pandas as pd

import synthetic_task_generator
from bustle_properties import *
from bustle_string_dsl import *
from utils import *


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

        max_string_variables = 3
        max_integer_variables = 1

        """

        Property Signature composition:

                main_program:

                1. input strings with string only properties (3*14 = 42)
                2. input integer with integer only properties (1*7 = 7)
                3. output string with string only properties (1*14 = 14)
                4. input integer and output string with integer-string properties (1*7 =7)
                5. input strings and output string with string-string properties (3*17 = 51)
                
                sub_program:

                6. boolean output with boolean only properties (1*1 = 1)
                7. integer output with integer only properties (1*7 = 7)
                8. string output with string only properties (1*14 = 14)
                9. integer output and string output of main program with integer-string properties (1*7 = 7)
                10. string output and string output of main program with string-string properties (1*17 = 17)
                
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
                if new_program is not None and new_program.toString() not in self.closed_list and not self.has_equivalent(
                        new_program):
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
    model_filename = models_directory + "BustleModelForPS.hdf5"
    os.makedirs(os.path.dirname(model_filename), exist_ok=True)
    BustleModel = keras_model.load_model(model_filename)


def populate_training_property_value(data_point, property_index, property_encoding):
    property_str = "prop" + str(property_index) + "_"
    for encoding_index, encoding_value in enumerate(property_encoding):
        data_point[property_str + str(encoding_index)] = encoding_value


def generate_datapoint(program, sub_program, input_output_examples_list,
                       string_variables_list, integer_variables_list):
    property_encodings = {
        AllTrue: EncodedAllTrue,
        AllFalse: EncodedAllFalse,
        Mixed: EncodedMixed,
        Padding: EncodedPadding
    }

    data_point = {}

    parent_input_outputs = input_output_examples_list.copy()
    property_index = 0
    max_string_variables = 3
    max_integer_variables = 1

    string_variables_present = []
    integer_variables_present = []

    for string_variable in string_variables_list:
        if string_variable in program.toString():
            string_variables_present.append(True)
        else:
            string_variables_present.append(False)

    for integer_variable in integer_variables_list:
        if integer_variable in program.toString():
            integer_variables_present.append(True)
        else:
            integer_variables_present.append(False)

    # PARENT PROPERTY SIGNATURE CALCULATION

    # Input strings string-only properties
    for string_variable_index, string_variable in enumerate(string_variables_list):
        if string_variables_present[string_variable_index]:
            input_strings = [parent_input_output.get(string_variable)
                             for parent_input_output in parent_input_outputs]
            for StringProperty in StringProperties:
                property_value = StringProperty(input_strings)
                property_index += 1
                populate_training_property_value(data_point, property_index,
                                                 property_encodings[property_value])
        else:
            for _ in StringProperties:
                property_value = Padding
                property_index += 1
                populate_training_property_value(data_point, property_index,
                                                 property_encodings[property_value])

    for padding_index in range(0, max_string_variables - len(string_variables_list)):
        for _ in StringProperties:
            property_value = Padding
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    # input integer with integer only properties
    for integer_variable_index, integer_variable in enumerate(integer_variables_list):
        if integer_variables_present[integer_variable_index]:
            input_integers = [parent_input_output.get(integer_variable)
                              for parent_input_output in parent_input_outputs]
            for IntegerProperty in IntegerProperties:
                property_value = IntegerProperty(input_integers)
                property_index += 1
                populate_training_property_value(data_point, property_index,
                                                 property_encodings[property_value])
        else:
            for _ in IntegerProperties:
                property_value = Padding
                property_index += 1
                populate_training_property_value(data_point, property_index,
                                                 property_encodings[property_value])

    for padding_index in range(0, max_integer_variables - len(integer_variables_list)):
        for _ in IntegerProperties:
            property_value = Padding
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    # checking the output types
    task_outputs = [parent_input_output['out'] for parent_input_output in parent_input_outputs]
    output_type = "str"
    if isinstance(task_outputs[0], int):
        output_type = "int"
    elif isinstance(task_outputs[0], bool):
        output_type = "bool"

    # output string with string only properties
    output_strings = [parent_input_output['out'] for parent_input_output in parent_input_outputs]
    if output_type == "str":
        for StringProperty in StringProperties:
            property_value = StringProperty(output_strings)
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])
    else:
        for _ in StringProperties:
            property_value = Padding
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    # input integer and output string with integer-string properties
    for integer_variable_index, integer_variable in enumerate(integer_variables_list):
        if integer_variables_present[integer_variable_index] and output_type == "str":
            for IntegerStringProperty in InputIntegerOutputStringProperties:
                property_value = IntegerStringProperty(parent_input_outputs, integer_variable)
                property_index += 1
                populate_training_property_value(data_point, property_index,
                                                 property_encodings[property_value])
        else:
            for _ in InputIntegerOutputStringProperties:
                property_value = Padding
                property_index += 1
                populate_training_property_value(data_point, property_index,
                                                 property_encodings[property_value])

    for padding_index in range(0, max_integer_variables - len(integer_variables_list)):
        for _ in InputIntegerOutputStringProperties:
            property_value = Padding
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    # input strings and output string with string-string properties
    for string_variable_index, string_variable in enumerate(string_variables_list):
        if string_variables_present[string_variable_index] and output_type == "str":
            for InputStringOutputStringProperty in InputStringOutputStringProperties:
                property_value = InputStringOutputStringProperty(parent_input_outputs, string_variable)
                property_index += 1
                populate_training_property_value(data_point, property_index,
                                                 property_encodings[property_value])
        else:
            for _ in InputStringOutputStringProperties:
                property_value = Padding
                property_index += 1
                populate_training_property_value(data_point, property_index,
                                                 property_encodings[property_value])

    for padding_index in range(0, max_string_variables - len(string_variables_list)):
        for _ in InputStringOutputStringProperties:
            property_value = Padding
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    child_input_outputs = []

    for input_output_example in input_output_examples_list:
        child_input_output = input_output_example.copy()
        child_output = sub_program.interpret(input_output_example)
        child_input_output['cout'] = child_output
        child_input_outputs.append(child_input_output)

    # CHILD PROPERTY SIGNATURE CALCULATION

    outputs = [output['cout'] for output in child_input_outputs]
    if None in outputs:
        return None

    # boolean output of subexpression with boolean only properties
    if sub_program.getReturnType() == BOOL_TYPES['type']:
        for BooleanProperty in BooleanProperties:
            property_value = BooleanProperty(outputs)
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    else:
        for _ in BooleanProperties:
            property_value = Padding
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    # integer output of expression with integer only properties
    if sub_program.getReturnType() == INT_TYPES['type']:
        for IntegerProperty in IntegerProperties:
            property_value = IntegerProperty(outputs)
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    else:
        for _ in IntegerProperties:
            property_value = Padding
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    # string output of subexpression with string only properties
    if sub_program.getReturnType() == STR_TYPES['type']:
        for StringProperty in StringProperties:
            property_value = StringProperty(outputs)
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    else:
        for _ in StringProperties:
            property_value = Padding
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    # integer output of subexpression and string output of main expression with integer-string properties
    if sub_program.getReturnType() == INT_TYPES['type'] and output_type == "str":
        for IntegerStringProperty in InputIntegerOutputStringProperties:
            property_value = IntegerStringProperty(child_input_outputs, 'cout')
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])
    else:
        for _ in InputIntegerOutputStringProperties:
            property_value = Padding
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    # string output of subexpression and string output of main expression with string-string properties
    if sub_program.getReturnType() == STR_TYPES['type'] and output_type == "str":
        for StringStringProperty in InputStringOutputStringProperties:
            property_value = StringStringProperty(child_input_outputs, 'cout')
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])
    else:
        for _ in InputStringOutputStringProperties:
            property_value = Padding
            property_index += 1
            populate_training_property_value(data_point, property_index,
                                             property_encodings[property_value])

    return data_point


def generate_retrain_data(bus_synthesizer, task_solution, input_output_examples_list,
                          string_variables_list, integer_variables_list):
    iterative_training_data_filename = data_directory + "iterative_training_data.csv"
    solution_size = task_solution.size
    solution_subprograms = set()
    task_solution.getProgramIds(solution_subprograms)
    all_programs = []
    for program_size in range(4, solution_size):
        all_programs.extend(bus_synthesizer.program_list.get_programs_all(program_size))
    non_solution_programs = list(
        filter(lambda program: program not in solution_subprograms, all_programs))

    negative_programs_size = len(solution_subprograms)
    if len(non_solution_programs) >= negative_programs_size:
        negative_programs = random.sample(non_solution_programs, negative_programs_size)
    else:
        negative_programs = non_solution_programs

    positive_programs = solution_subprograms
    positive_programs.remove(task_solution)

    logging.info("positive data points: "+str(len(positive_programs)))
    logging.info("negative data points: "+str(len(negative_programs)))

    iterative_training_data = []
    for positive_program in positive_programs:
        positive_datapoint = generate_datapoint(task_solution, positive_program, input_output_examples_list,
                                                string_variables_list, integer_variables_list)
        positive_datapoint['label'] = 1
        iterative_training_data.append(positive_datapoint)

    for negative_program in negative_programs:
        negative_datapoint = generate_datapoint(task_solution, negative_program, input_output_examples_list,
                                                string_variables_list, integer_variables_list)
        negative_datapoint['label'] = 0
        iterative_training_data.append(negative_datapoint)

    logging.info("training dataset size: " + str(len(iterative_training_data)))
    dataFrame = pd.DataFrame(iterative_training_data)
    logging.info("dataframe size: " + str(dataFrame.shape[0]))
    logging.info("Saving the training data to csv file...")
    dataFrame.to_csv(iterative_training_data_filename, index=False, mode='a',
                     header=not os.path.exists(iterative_training_data_filename))


if __name__ == "__main__":

    TaskId = None
    log_filename = logs_directory + "bustle_output.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    if len(sys.argv) == 2:
        slurm_task_id = sys.argv[1]
        TaskId = int(slurm_task_id)
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

    if TaskId is None:
        sys.exit()

    synthetic_task = synthetic_task_generator.get_synthetic_task(TaskId)
    specifications = synthetic_task.get_specifications()
    benchmark = "synthetic_task_" + str(TaskId)
    logging.info('TaskId: ' + str(TaskId))
    logging.info("\n")

    dsl_functions = [StrConcat, StrReplace,
                     StrSubstr, StrIte, StrIntToStr, StrCharAt, StrTrim, StrLower,
                     StrUpper, StrLeftSubstr, StrRightSubstr,
                     StrReplaceMulti, StrReplaceAdd, IntStrToInt, IntPlus,
                     IntMinus, IntLength, IntIteInt, IntIndexOf, IntFirstIndexOf, BoolEqual, BoolContain,
                     BoolSuffixof, BoolPrefixof, BoolGreaterThan, BoolGreaterThanEqual]

    string_variables = specifications[0]
    string_literals = specifications[1]
    integer_variables = specifications[2]
    integer_literals = specifications[3]

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

    if solution is not None:
        logging.info("Benchmark: " + str(benchmark))
        logging.info("Result: Success")
        logging.info("Program: " + solution.toString())
        logging.info("Number of evaluations: " + str(num))
        logging.info(str(datetime.now()))
        logging.info("Time taken: " + str(datetime.now() - begin_time))
        generate_retrain_data(synthesizer, solution, input_output_examples, string_variables,
                              integer_variables)
    else:
        logging.info("Benchmark: " + str(benchmark))
        logging.info("Result: Fail")
        logging.info("Program: None")
        logging.info("Number of evaluations: " + str(num))
        logging.info(str(datetime.now()))
        logging.info("Time taken: " + str(datetime.now() - begin_time))

        logging.info("\n\n")
