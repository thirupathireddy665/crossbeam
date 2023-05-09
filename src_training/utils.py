import re
from os.path import expanduser

home_directory = expanduser("~")
scratch_directory = home_directory+"/scratch/"
# scratch_directory = "../"
# paths
# PATH_TO_STR_BENCHMARKS = "./strings"
PATH_TO_STR_BENCHMARKS = "../sygus_string_tasks/"
config_directory = "../config/"
pickle_files_directory = scratch_directory+"/pickle_files/"
task_files_directory = scratch_directory+"/task_files/"
models_directory = scratch_directory+"/models/"
logs_directory = scratch_directory+"/logs/"
property_data_directory = scratch_directory+"/property_data/"
data_directory = scratch_directory+"/data/"

# sygus parser constants
NT_STRING = "ntString String"
NT_INT = "ntInt Int"
CONSTRAINT = "constraint"
STRING_VAR = "string"
INTEGER_VAR = "integer"
EMPTY_STRING = "\"\""

# Regex properties
regex_digit = re.compile('\d')
regex_only_digits = re.compile('^\d+$')
regex_alpha = re.compile('[a-zA-Z]')
regex_alpha_only = re.compile('^[a-zA-Z]+$')

# String type
STR_TYPES = {'type': 'str'}

# Integer type
INT_TYPES = {'type': 'integer'}

# Boolean type
BOOL_TYPES = {'type': 'boolean'}
