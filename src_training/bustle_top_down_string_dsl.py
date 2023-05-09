import copy
import random

from topdown_cfg import BustlePCFG
from utils import *


class Str:
    def __init__(self):
        self.size = 0

    @classmethod
    def getReturnType(cls):
        return STR_TYPES['type']

    @classmethod
    def name(cls):
        return cls.__name__


class StrLiteral(Str):
    def __init__(self, value):
        self.value = value

    def toString(self):
        return '\"' + self.value + '\"'

    def interpret(self, env):
        return self.value

    def get_sub_programs(self, sub_programs):
        pass


class StrVar(Str):
    def __init__(self, name):
        self.value = name

    def toString(self):
        return self.value

    def interpret(self, env):
        return copy.deepcopy(env[self.value])

    def get_sub_programs(self, sub_programs):
        pass


class StrConcat(Str):
    ARITY = 2

    def __init__(self, prefix, suffix):
        self.prefix = prefix
        self.suffix = suffix

    def toString(self):
        return 'concat(' + self.prefix.toString() + ", " + self.suffix.toString() + ")"

    def interpret(self, env):
        try:
            return self.prefix.interpret(env) + self.suffix.interpret(env)
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.prefix.get_sub_programs(sub_programs)
        self.suffix.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        prefix = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        suffix = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if prefix and suffix:
            return StrConcat(prefix, suffix)
        return None


class StrReplace(Str):
    ARITY = 3

    def __init__(self, input_str, old_str, new_str):
        self.str = input_str
        self.old = old_str
        self.new = new_str

    def toString(self):
        return self.str.toString() + '.replace(' + self.old.toString() + ", " + self.new.toString() + ")"

    def interpret(self, env):
        try:
            return self.str.interpret(env).replace(self.old.interpret(env), self.new.interpret(env), 1)
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)
        self.old.get_sub_programs(sub_programs)
        self.new.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        old_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        new_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if input_str and old_str and new_str:
            return StrReplace(input_str, old_str, new_str)
        return None


class StrSubstr(Str):
    ARITY = 3

    def __init__(self, input_str, start, end):
        self.str = input_str
        self.start = start
        self.end = end

    def toString(self):
        return self.str.toString() + ".Substr(" + self.start.toString() + "," + self.end.toString() + ")"

    def interpret(self, env):
        try:
            return self.str.interpret(env)[self.start.interpret(env): self.end.interpret(env)]
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)
        self.start.get_sub_programs(sub_programs)
        self.end.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        start = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        end = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        if input_str and start and end:
            return StrSubstr(input_str, start, end)
        return None


class StrIte(Str):
    ARITY = 3

    def __init__(self, condition, true_case, false_case):
        self.condition = condition
        self.true_case = true_case
        self.false_case = false_case

    def toString(self):
        return "(if" + self.condition.toString() + " then " + self.true_case.toString() + " else " + self.false_case.toString() + ")"

    def interpret(self, env):
        try:
            if self.condition.interpret(env):
                return self.true_case.interpret(env)
            else:
                return self.false_case.interpret(env)
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.condition.get_sub_programs(sub_programs)
        self.true_case.get_sub_programs(sub_programs)
        self.false_case.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        condition = BustlePCFG.get_instance().generate_program(BOOL_TYPES['type'], height)
        true_case = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        false_case = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if condition and true_case and false_case:
            return StrIte(condition, true_case, false_case)
        return None


class StrIntToStr(Str):
    ARITY = 1

    def __init__(self, input_int):
        self.int = input_int

    def toString(self):
        return self.int.toString() + ".IntToStr()"

    def interpret(self, env):
        try:
            return str(self.int.interpret(env))
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.int.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_int = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        if input_int:
            return StrIntToStr(input_int)
        return None


# bustle additional classes
class StrReplaceAdd(Str):
    ARITY = 4

    def __init__(self, input_str, start, end, add_str):
        self.str = input_str
        self.start = start
        self.end = end
        self.add_str = add_str

    def toString(self):
        return self.str.toString() + "[:" + self.start.toString() + "] + " + self.add_str.toString() + " + " + self.str.toString() + "[" + self.end.toString() + ":]"

    def interpret(self, env):
        try:
            return self.str.interpret(env)[:self.start.interpret(env)] + self.add_str.interpret(
                env) + self.str.interpret(
                env)[self.end.interpret(env):]
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)
        self.start.get_sub_programs(sub_programs)
        self.end.get_sub_programs(sub_programs)
        self.add_str.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        add_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        start = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        end = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)

        if input_str and add_str and start and end:
            return StrReplaceAdd(input_str, start, end, add_str)

        return None


class StrReplaceMulti(Str):
    ARITY = 4

    def __init__(self, input_str, old, new, count):
        self.str = input_str
        self.old = old
        self.new = new
        self.count = count

    def toString(self):
        return self.str.toString() + '.replace(' + self.old.toString() + ", " + self.new.toString() + "," + self.count.toString() + ")"

    def interpret(self, env):
        try:
            return self.str.interpret(env).replace(self.old.interpret(env), self.new.interpret(env),
                                                   self.count.interpret(env))
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)
        self.old.get_sub_programs(sub_programs)
        self.new.get_sub_programs(sub_programs)
        self.count.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        old = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        new = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        count = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)

        if input_str and old and new and count:
            return StrReplaceMulti(input_str, old, new, count)
        return None


class StrTrim(Str):
    ARITY = 1

    def __init__(self, input_str):
        self.str = input_str

    def toString(self):
        return self.str.toString() + ".strip()"

    def interpret(self, env):
        try:
            interpreted_string = self.str.interpret(env)
            if interpreted_string is None:
                return None
            return self.str.interpret(env).strip()
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if input_str:
            return StrTrim(input_str)
        return None


class StrLower(Str):
    ARITY = 1

    def __init__(self, input_str):
        self.str = input_str

    def toString(self):
        return self.str.toString() + ".lower()"

    def interpret(self, env):
        try:
            return self.str.interpret(env).lower()
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if input_str:
            return StrLower(input_str)
        return None


class StrUpper(Str):
    ARITY = 1

    def __init__(self, input_str):
        self.str = input_str

    def toString(self):
        return self.str.toString() + ".upper()"

    def interpret(self, env):
        try:
            return self.str.interpret(env).upper()
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if input_str:
            return StrUpper(input_str)
        return None


class StrProper(Str):
    ARITY = 1

    def __init__(self, input_str):
        self.str = input_str

    def toString(self):
        return self.str.toString() + ".title()"

    def interpret(self, env):
        try:
            return self.str.interpret(env).title()
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if input_str:
            return StrProper(input_str)
        return None


class StrRepeat(Str):
    ARITY = 2

    def __init__(self, input_str, input_int):
        self.str = input_str
        self.int = input_int

    def toString(self):
        return self.str.toString() + "*" + self.int.toString()

    def interpret(self, env):
        try:
            string_element = self.str.interpret(env)
            integer_element = self.int.interpret(env)
            if len(string_element) > 1000 or integer_element > 1000:
                return None
            if len(string_element) * integer_element > 1000:
                return None
            return self.str.interpret(env) * self.int.interpret(env)
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)
        self.int.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        input_int = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        if input_str and input_int:
            return StrRepeat(input_str, input_int)
        return None


class StrLeftSubstr(Str):
    ARITY = 2

    def __init__(self, input_str, input_int):
        self.str = input_str
        self.int = input_int

    def toString(self):
        return self.str.toString() + "[:" + self.int.toString() + "]"

    def interpret(self, env):
        try:
            return self.str.interpret(env)[:self.int.interpret(env)]
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)
        self.int.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        input_int = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        if input_str and input_int:
            return StrLeftSubstr(input_str, input_int)
        return None


class StrRightSubstr(Str):
    ARITY = 2

    def __init__(self, input_str, input_int):
        self.str = input_str
        self.int = input_int

    def toString(self):
        return self.str.toString() + "[" + self.int.toString() + ":]"

    def interpret(self, env):
        try:
            return self.str.interpret(env)[self.int.interpret(env):]
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)
        self.int.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        input_int = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        if input_str and input_int:
            return StrRightSubstr(input_str, input_int)
        return None


# end bustle additional classes

class StrCharAt(Str):
    ARITY = 2

    def __init__(self, input_str, pos):
        self.str = input_str
        self.pos = pos

    def toString(self):
        return self.str.toString() + ".CharAt(" + self.pos.toString() + ")"

    def interpret(self, env):
        try:
            index = self.pos.interpret(env)
            string_element = self.str.interpret(env)
            if 0 <= index < len(string_element):
                return string_element[index]
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)
        self.pos.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        input_int = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        if input_str and input_int:
            return StrCharAt(input_str, input_int)
        return None


# Contains all operations with return type int

class Int:
    def __init__(self):
        self.size = 0

    @classmethod
    def getReturnType(cls):
        return INT_TYPES['type']

    @classmethod
    def name(cls):
        return cls.__name__


class IntLiteral(Int):
    def __init__(self, value):
        self.value = value

    def toString(self):
        return str(self.value)

    def interpret(self, env):
        return self.value

    def get_sub_programs(self, sub_programs):
        pass


class IntVar(Int):
    def __init__(self, name):
        self.value = name

    def toString(self):
        return self.value

    def interpret(self, env):
        return copy.deepcopy(env[self.value])

    def get_sub_programs(self, sub_programs):
        pass


class IntStrToInt(Int):
    ARITY = 1

    def __init__(self, input_str):
        self.str = input_str

    def toString(self):
        return self.str.toString() + ".StrToInt()"

    def interpret(self, env):
        try:
            value = self.str.interpret(env)
            if regex_only_digits.search(value) is not None:
                return int(value)
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if input_str:
            return IntStrToInt(input_str)
        return None


class IntPlus(Int):
    ARITY = 2

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " + " + self.right.toString() + ")"

    def interpret(self, env):
        try:
            return self.left.interpret(env) + self.right.interpret(env)
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.left.get_sub_programs(sub_programs)
        self.right.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        left = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        right = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        if left and right:
            return IntPlus(left, right)
        return None


class IntMinus(Int):
    ARITY = 2

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " - " + self.right.toString() + ")"

    def interpret(self, env):
        try:
            return self.left.interpret(env) - self.right.interpret(env)
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.left.get_sub_programs(sub_programs)
        self.right.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        left = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        right = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        if left and right:
            return IntMinus(left, right)
        return None


class IntLength(Int):
    ARITY = 1

    def __init__(self, input_str):
        self.str = input_str

    def toString(self):
        return self.str.toString() + ".Length()"

    def interpret(self, env):
        try:
            return len(self.str.interpret(env))
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if input_str:
            return IntLength(input_str)
        return None


class IntIteInt(Int):
    ARITY = 3

    def __init__(self, condition, true_case, false_case):
        self.condition = condition
        self.true_case = true_case
        self.false_case = false_case

    def toString(self):
        return "(if" + self.condition.toString() + " then " + self.true_case.toString() + " else " + self.false_case.toString() + ")"

    def interpret(self, env):
        try:
            if self.condition.interpret(env):
                return self.true_case.interpret(env)
            else:
                return self.false_case.interpret(env)
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.condition.get_sub_programs(sub_programs)
        self.true_case.get_sub_programs(sub_programs)
        self.false_case.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        condition = BustlePCFG.get_instance().generate_program(BOOL_TYPES['type'], height)
        true_case = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        false_case = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        if condition and true_case and false_case:
            return IntIteInt(condition, true_case, false_case)
        return None


class IntIndexOf(Int):
    ARITY = 3

    def __init__(self, input_str, substr, start):
        self.input_str = input_str
        self.substr = substr
        self.start = start

    def toString(self):
        return self.input_str.toString() + ".IndexOf(" + self.substr.toString() + "," + self.start.toString() + ")"

    def interpret(self, env):
        start_position = self.start.interpret(env)
        sub_string = self.substr.interpret(env)
        super_string = self.input_str.interpret(env)
        index = None
        try:
            index = super_string.index(sub_string, start_position)
        except:
            pass
        return index

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.input_str.get_sub_programs(sub_programs)
        self.substr.get_sub_programs(sub_programs)
        self.start.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        sub_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        start = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        if input_str and sub_str and start:
            return IntIndexOf(input_str, sub_str, start)
        return None


# bustle additional integer classes
class IntFirstIndexOf(Int):
    ARITY = 2

    def __init__(self, input_str, substr):
        self.input_str = input_str
        self.substr = substr

    def toString(self):
        return self.input_str.toString() + ".IndexOf(" + self.substr.toString() + ")"

    def interpret(self, env):
        sub_string = self.substr.interpret(env)
        super_string = self.input_str.interpret(env)
        index = None
        try:
            index = super_string.index(sub_string)
        except:
            pass
        return index

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.input_str.get_sub_programs(sub_programs)
        self.substr.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        sub_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if input_str and sub_str:
            return IntFirstIndexOf(input_str, sub_str)
        return None


# Contains all operations with return type bool

class Bool:
    def __init__(self):
        self.size = 0

    @classmethod
    def getReturnType(cls):
        return BOOL_TYPES['type']

    @classmethod
    def name(cls):
        return cls.__name__


class BoolLiteral(Bool):
    def __init__(self, boolean):
        self.bool = True if boolean is True else False

    def toString(self):
        return str(self.bool)

    def interpret(self, env):
        return self.bool

    def get_sub_programs(self, sub_programs):
        pass


class BoolEqual(Bool):
    ARITY = 2

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toString(self):
        return "Equal(" + self.left.toString() + "," + self.right.toString() + ")"

    def interpret(self, env):
        try:
            return True if self.left.interpret(env) == self.right.interpret(env) else False
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.left.get_sub_programs(sub_programs)
        self.right.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        return_type = random.choice([STR_TYPES['type'], INT_TYPES['type'], BOOL_TYPES['type']])
        left = BustlePCFG.get_instance().generate_program(return_type, height)
        right = BustlePCFG.get_instance().generate_program(return_type, height)
        if left and right:
            return BoolEqual(left, right)
        return None


class BoolContain(Bool):
    ARITY = 2

    def __init__(self, input_str, substr):
        self.str = input_str
        self.substr = substr

    def toString(self):
        return self.str.toString() + ".Contain(" + self.substr.toString() + ")"

    def interpret(self, env):
        try:
            return True if self.substr.interpret(env) in self.str.interpret(env) else False
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)
        self.substr.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        sub_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if input_str and sub_str:
            return BoolContain(input_str, sub_str)
        return None


class BoolSuffixof(Bool):
    ARITY = 2

    def __init__(self, input_str, suffix):
        self.str = input_str
        self.suffix = suffix

    def toString(self):
        return self.suffix.toString() + ".SuffixOf(" + self.str.toString() + ")"

    def interpret(self, env):
        try:
            return True if self.str.interpret(env).endswith(self.suffix.interpret(env)) else False
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)
        self.suffix.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        sub_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if input_str and sub_str:
            return BoolSuffixof(input_str, sub_str)
        return None


class BoolPrefixof(Bool):
    ARITY = 2

    def __init__(self, input_str, prefix):
        self.str = input_str
        self.prefix = prefix

    def toString(self):
        return self.prefix.toString() + ".Prefixof(" + self.str.toString() + ")"

    def interpret(self, env):
        try:
            return True if self.str.interpret(env).startswith(self.prefix.interpret(env)) else False
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.str.get_sub_programs(sub_programs)
        self.prefix.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        input_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        sub_str = BustlePCFG.get_instance().generate_program(STR_TYPES['type'], height)
        if input_str and sub_str:
            return BoolPrefixof(input_str, sub_str)
        return None


# bustle additional bool classes

class BoolGreaterThan(Bool):
    ARITY = 2

    def __init__(self, first_int, second_int):
        self.first_int = first_int
        self.second_int = second_int

    def toString(self):
        return self.first_int.toString() + " > " + self.second_int.toString()

    def interpret(self, env):
        try:
            return True if self.first_int.interpret(env) > self.second_int.interpret(env) else False
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.first_int.get_sub_programs(sub_programs)
        self.second_int.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        first_int = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        second_int = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        if first_int and second_int:
            return BoolGreaterThan(first_int, second_int)
        return None


class BoolGreaterThanEqual(Bool):
    ARITY = 2

    def __init__(self, first_int, second_int):
        self.first_int = first_int
        self.second_int = second_int

    def toString(self):
        return self.first_int.toString() + " >= " + self.second_int.toString()

    def interpret(self, env):
        try:
            return True if self.first_int.interpret(env) >= self.second_int.interpret(env) else False
        except:
            pass
        return None

    def get_sub_programs(self, sub_programs):
        sub_programs.add(self)
        self.first_int.get_sub_programs(sub_programs)
        self.second_int.get_sub_programs(sub_programs)

    @staticmethod
    def grow(height):
        first_int = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        second_int = BustlePCFG.get_instance().generate_program(INT_TYPES['type'], height)
        if first_int and second_int:
            return BoolGreaterThanEqual(first_int, second_int)
        return None
