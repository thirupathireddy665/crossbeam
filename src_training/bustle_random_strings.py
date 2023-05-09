# crossbeam code to generate random input strings
import random
import string

CHARSETS = [
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ',  # Uppercase letters
    'abcdefghijklmnopqrstuvwxyz',  # Lowercase letters
    '0123456789',  # Digits
    ' ',  # Space
    '.,-+_@$/',  # Common punctuation
]


def bustle_input_generator():
    # GenerateData::randomInput
    length = random.randint(1, 10)
    usable_charsets = [charset for charset in CHARSETS
                       if random.random() < 0.25]
    if not usable_charsets:
        usable_charsets.append(CHARSETS[1])  # Lowercase letters
    return ''.join(random.choice(random.choice(usable_charsets))
                   for _ in range(length))


def random_inputs_dict_generator(num_inputs, num_examples):
    random_characters = list(string.ascii_lowercase)
    random_characters.extend(list(string.ascii_uppercase))
    random_characters.extend(list(string.digits))
    random_characters.extend([" "])
    random_characters.extend([".", "-", "+", "_", "@", "$", "/"])

    inputs_dict = {'arg{}'.format(i): []
                   for i in range(num_inputs)}

    for _ in range(num_examples):
        for i in range(num_inputs):
            random_string_len = random.randint(8, 15)
            random_character_list = []
            for _ in range(random_string_len):
                random_character_list.append(random.choice(random_characters))
            inputs_dict['arg{}'.format(i)].append("".join(random_character_list))

    return inputs_dict


def bustle_inputs_dict_generator(num_inputs, num_examples):
    num_formats = random.randint(1, 2)

    # formats[f][i] is a list of symbols for the i-th input in the f-th format.
    formats = []
    max_symbol = 0
    for _ in range(num_formats):
        # Choose number of slots for each input.
        slots_per_input = [random.randint(1, 3) for _ in range(num_inputs)]
        num_symbols = sum(slots_per_input)
        max_symbol = max(max_symbol, num_symbols - 1)
        # Choose symbols for each input.
        form = []
        for num_slots in slots_per_input:
            form.append([random.randrange(num_symbols) for _ in range(num_slots)])
        formats.append(form)

    # Choose some symbols to be "example-persistent".
    example_persistent_symbols = {}
    for s in range(max_symbol):
        if random.random() < 0.25:
            example_persistent_symbols[s] = bustle_input_generator()

    # Create inputs dict.
    inputs_dict = {'arg{}'.format(i): []
                   for i in range(num_inputs)}
    for _ in range(num_examples):
        form = random.choice(formats)
        symbol_map = example_persistent_symbols.copy()
        for i in range(num_inputs):
            inp = ''
            for symbol in form[i]:
                if symbol not in symbol_map:
                    symbol_map[symbol] = bustle_input_generator()
                inp += symbol_map[symbol]
            inputs_dict['arg{}'.format(i)].append(inp)
    return inputs_dict


print(random_inputs_dict_generator(3, 3))
