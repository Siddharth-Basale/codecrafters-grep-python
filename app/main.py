import sys

# import pyparsing - available if you need it!
# import lark - available if you need it!


def tokenize_pattern(pattern):
    tokens = []
    i = 0 
    while i < len(pattern):
        if pattern[i] == "\\" and i+1 < len(pattern):
            tokens.append(pattern[i:i+2])
            i+=2

        elif pattern[i] == "[":
            end = pattern.find("]", i)
            tokens.append(pattern[i : end + 1])
            i = end + 1

        else:
            tokens.append(pattern[i])
            i+=1
    return tokens

def match_char(char, token):
    if token == r"\d":
        return char.isdigit()
    elif token == r"\w":
        return char.isalnum() or char == "_"
    elif token.startswith("[^") and token.endswith("]"):
        excluded = token[2:-1]
        return char not in excluded
    elif token.startswith("[") and token.endswith("]"):
        included = token[1:-1]
        return char in included
    else:
        return char == token


def match_pattern(input_line, pattern):
    # 1. Detect anchors independently
    match_from_start = pattern.startswith("^")
    if match_from_start:
        pattern = pattern[1:]

    match_to_end = pattern.endswith("$")
    if match_to_end:
        pattern = pattern[:-1]

    tokens = tokenize_pattern(pattern)

    # Empty pattern handling
    if not tokens:
        if match_to_end and match_from_start:
            return len(input_line) == 0
        return True

    # 2. Determine allowed start positions
    if match_from_start:
        starting_indices = [0]
    else:
        starting_indices = range(len(input_line) + 1)

    # 3. Slide through starting positions
    for start_idx in starting_indices:
        matched = True
        for t_idx in range(len(tokens)):
            current_char_idx = start_idx + t_idx

            if current_char_idx >= len(input_line):
                matched = False
                break

            if not match_char(input_line[current_char_idx], tokens[t_idx]):
                matched = False
                break

        if matched:
            # If $ is present, the match MUST reach the very end of input_line
            if match_to_end:
                if start_idx + len(tokens) == len(input_line):
                    return True
            else:
                return True

    return False
    


def main():
    pattern = sys.argv[2]
    input_line = sys.stdin.read()

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # TODO: Uncomment the code below to pass the first stage
    if match_pattern(input_line, pattern):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
