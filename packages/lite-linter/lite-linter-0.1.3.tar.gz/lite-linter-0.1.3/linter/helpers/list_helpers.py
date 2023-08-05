def index_of_string_in_list(string: str, lines: list):
    for line in lines:
        if string in line:
            return lines.index(line) + 1

    return -1
