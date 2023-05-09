import re

# paths
# PATH_TO_STR_BENCHMARKS = "./strings"
PATH_TO_STR_BENCHMARKS = "../sygus_string_tasks/"
config_directory = "../config/"
pickle_files_directory = "../pickle_files/"
models_directory = "../models/"
logs_directory = "../logs/"
property_data_directory = "../property_data/"
PATH_TO_38_BENCHMARKS = "../src_all_sygus/38_benchmarks.json"
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
