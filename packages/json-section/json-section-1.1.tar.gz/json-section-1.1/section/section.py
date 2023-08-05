import sys

def get_stdin():
    input_list = list()
    for line in sys.stdin:
        input_list.append(line)
    return input_list

def find_opening_bracket(position, stdin_list):
    for i in reversed(range(position-1)):
        if "{" in stdin_list[i] and "}" not in stdin_list[i]:
            return i
    return -1

def has_brackets(sentence):
    sum = 0
    if "{" in sentence:
        sum += 1
    if "}" in sentence:
        sum += -1
    return sum


def process_stdin(word, stdin_list):
    word_position_list = []
    bracket_counter = 0

    # define bracket stuff
    opening_bracket_line = int()
    bracket_counter = 0
    ignore_index = -1

    for i in range(len(stdin_list)):
        if i > ignore_index:
            sentence = stdin_list[i]
            if word in sentence:
                opening_bracket_line = find_opening_bracket(i, stdin_list)
                bracket_counter += 1+has_brackets(sentence)
                pointer = i+1
                while bracket_counter > 0:
                    this_sentence = stdin_list[pointer]
                    bracket_counter += has_brackets(this_sentence)
                    pointer += 1
                closing_bracket_line = pointer
                word_position_list.append((opening_bracket_line,
                closing_bracket_line))
                ignore_index = closing_bracket_line


    return word_position_list

def query():
    expression = sys.argv[1]
    ingest_data = get_stdin()
    indexes = process_stdin(expression, ingest_data)
    if len(indexes) == 0:
        exit()
    for index_map in indexes:
        for i in range(index_map[0], index_map[1]):
            sentence_to_print = ingest_data[i]
            if sentence_to_print != "\n":
                print(sentence_to_print)
