import copy
from utils import PATH_TO_38_BENCHMARKS
import json
import string
"""
USAGE:
    1- Create an instance of the class.
    2- Call instance.parse() - 2 will yield results.
"""


class StrParser38():
    """
    Returns:
            str_var: variables to represent input string data
            str_literals: string constants
            int_var: variables to represent input int data
            int_literals: integer literals
            input: input values (for str_var or int_var)
            output: output string database
    """

    def __init__(self, filename):
        self.str_var = []
        self.str_literals = [" ", ""]
        self.int_var = []
        self.int_literals = [-4,-3,-2,-1,0,1,2,3,4,15]
        self.input = []
        self.output = []
        self.problem = filename
        self.test_cases = []
        self.benchmark = None

    def reset(self):
        self.str_var = []
        self.str_literals = []
        self.int_var = []
        self.int_literals = []
        self.input = []
        self.output = []
        self.test_cases = []
        self.benchmark = None


    def extract_benchmark(self):
        dataset = open(PATH_TO_38_BENCHMARKS, "r")
        parsed_dataset = json.loads(dataset.read())
        for entry in parsed_dataset:
            if entry['name'] == self.problem:
                self.benchmark = copy.deepcopy(entry)
                break
        assert self.benchmark is not None, "Benchmark not found"
        dataset.close()

    def parse_constants(self):
        expectedSolution = self.benchmark['expectedProgram']
        i = 0
        while i < len(expectedSolution):
            if expectedSolution[i] == '"':
                start = i
                i += 1
                while expectedSolution[i] != '"':
                    i += 1
                self.str_literals.append(expectedSolution[start + 1:i])
            i += 1

    def parse_output(self, output):
        if output == "TRUE":
            return True
        elif output == "FALSE":
            return False
        return output

    def parse_vars(self):
        testExamples = self.benchmark['testExamples']
        firstExample = testExamples[0]
        for index in range(len(firstExample['inputs'])):
            self.str_var.append("arg_" + str(index))
    
    def parse_io_pairs(self):
        examples = ['trainExamples', 'testExamples']
        for example in examples:
            testExamples = self.benchmark[example]
            for example in testExamples:
                io_dict = {}
                for index, input_value in enumerate(example['inputs']):
                    io_dict[self.str_var[index]] = input_value
                io_dict['out'] = self.parse_output(example['output'])
                self.test_cases.append(io_dict)

    def parse_args_const(self):
        self.parse_constants()
        self.parse_vars()

    def parse(self):
        self.extract_benchmark()
        self.parse_args_const()
        self.parse_io_pairs()
        return [self.str_var, list(set(self.str_literals)), self.int_var, self.int_literals, self.test_cases, self.problem]