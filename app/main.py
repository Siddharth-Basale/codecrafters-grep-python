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

        elif(pattern[i] == "+"):
            if pattern[i-2] == "\\":
                tokens.pop()
                tokens.append(pattern[i-2:i+1])
            else:
                tokens.pop()
                tokens.append(pattern[i-1:i+1])
            i+=1

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
    print(f"input line: {input_line}")
    print(f"pattern: {pattern}")

    match_from_start = pattern.startswith("^")
    if match_from_start:
        pattern = pattern[1:]

    match_to_end = pattern.endswith("$")
    if match_to_end:
        pattern = pattern[:-1]

    tokens = tokenize_pattern(pattern)
    print(f"tokens are {tokens}")

    # Empty pattern handling
    if not tokens:
        if match_to_end and match_from_start:
            return len(input_line) == 0
        return True

    # Determine allowed start positions
    if match_from_start:
        starting_indices = [0]
    else:
        starting_indices = range(len(input_line) + 1)

    # Slide through starting positions
    for start_idx in starting_indices:
        matched = True
        current_char_idx = start_idx
        skip_remaining = False

        for t_idx in range(len(tokens)):
            if skip_remaining:
                break

            token = tokens[t_idx]

            if current_char_idx >= len(input_line):
                matched = False
                break

            if token.endswith("+"):
                base_token = token[:-1]

                if not match_char(input_line[current_char_idx], base_token):
                    matched = False
                    break

                print("Bingo")

                plus_start = current_char_idx

                while (
                    current_char_idx < len(input_line)
                    and match_char(input_line[current_char_idx], base_token)
                ):
                    print(
                        f"starcurrent_char_idx is: {current_char_idx} "
                        f"and character to check is: {input_line[current_char_idx]}, "
                        f"with token is {tokens[t_idx]}"
                    )
                    current_char_idx += 1

                # Try the remaining tokens
                while current_char_idx > plus_start:
                    temp_idx = current_char_idx
                    remaining_matched = True

                    for next_idx in range(t_idx + 1, len(tokens)):
                        next_token = tokens[next_idx]

                        if temp_idx >= len(input_line):
                            remaining_matched = False
                            break

                        if next_token.endswith("+"):
                            next_base = next_token[:-1]

                            if not match_char(input_line[temp_idx], next_base):
                                remaining_matched = False
                                break

                            while (
                                temp_idx < len(input_line)
                                and match_char(input_line[temp_idx], next_base)
                            ):
                                temp_idx += 1

                        else:
                            if not match_char(input_line[temp_idx], next_token):
                                remaining_matched = False
                                break

                            temp_idx += 1

                    if remaining_matched:
                        current_char_idx = temp_idx
                        skip_remaining = True
                        break

                    current_char_idx -= 1

                else:
                    matched = False
                    break

            else:
                if not match_char(input_line[current_char_idx], token):
                    matched = False
                    break

                current_char_idx += 1

        if matched:
            if match_to_end:
                if current_char_idx == len(input_line):
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
