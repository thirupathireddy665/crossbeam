import sys
# Util code for processing the property_ranks.csv_considered to find final ranks

# import pandas as pd
# import numpy as np
# import utils
#
# property_ranks_file = utils.config_directory+"property_ranks.csv"
# dataframe = pd.read_csv(property_ranks_file)
# dataframe = dataframe.sum()
# ranks_sum = dataframe.values.tolist()
# print(ranks_sum)
# properties_sorted = list(np.argsort(ranks_sum))
# print("")
# print("final order of the properties ranked based on submodular optimization: ")
# print(properties_sorted)



# Util code for printing the generated properties (uncomment to use)
from bustle_properties import *
print(4 * (
            4 * len(StringProperties) +
            len(IntegerProperties) +
            len(StringProperties) +
            len(IntegerProperties) +
            len(BooleanProperties) +
            len(InputIntegerOutputStringProperties) +
            len(InputIntegerOutputIntegerProperties) +
            len(InputIntegerOutputBoolProperties) +
            4 * len(InputStringOutputStringProperties) +
            4 * len(InputStringOutputIntegerProperties) +
            4 * len(InputStringOutputBoolProperties) ))#+
            # len(BooleanProperties) +
            # len(IntegerProperties) +
            # len(StringProperties) +
            # len(InputIntegerOutputStringProperties) +
            # len(InputStringOutputStringProperties) +
            # len(InputIntegerOutputIntegerProperties) +
            # len(InputStringOutputIntegerProperties) +
            # len(InputIntegerOutputBoolProperties) +
            # len(InputStringOutputBoolProperties)))
if True:
    print("string only properties: ",len(StringProperties))
    print("integer only properties: ", len(IntegerProperties))
    print("boolean properties: ",len(BooleanProperties))
    print("input integer output string properties: ",len(InputIntegerOutputStringProperties))
    print("input string output string properties: ",len(InputStringOutputStringProperties))
    print("input integer output integer properties: ", len(InputIntegerOutputIntegerProperties))
    print("input string output integer properties: ", len(InputStringOutputIntegerProperties))
    print("input integer output bool properties: ",len(InputIntegerOutputBoolProperties))
    print("input string output bool properties: ", len(InputStringOutputBoolProperties))

sys.exit()
for property_t in InputStringOutputStringProperties:
    test =[{'asd':'random', 'out': 'random'},{'asd':'random123', 'out': 'random'}]
    #print(property_t(test, 'asd'))

for property_t in TopInputStringOutputStringProperties:
    test =[{'asd':'random', 'out': 'random'},{'asd':'random123', 'out': 'random'}]
    #a = property_t(test, 'asd')
    #print(property_t(test, 'asd'))

for property_t in BottomInputStringOutputStringProperties:
    test =[{'asd':'random', 'out': 'random'},{'asd':'random123', 'out': 'random'}]
    a = property_t(test, 'asd')
    #print(property_t(test, 'asd'))

'''
property position calculator

inputs string only:  1
output string only:  43
inputs string  and output string :  57
child output boolean:  357
child output integer:  358
child output string:  365
child integer output and final string output:  379
child string output and final string output:  386
final child property index not used:  486

starting of properties: 57
next index is 57+len(properties)
next index is 57+2*len(properties)
next index is 57+3*len(properties)+29

'''
