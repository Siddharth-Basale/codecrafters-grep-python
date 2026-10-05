import sys

# import pyparsing - available if you need it!
# import lark - available if you need it!


def match_pattern(input_line, pattern):
    print(f"patern is : {pattern}")
    print(f"string is : {input_line}")

    # First
    if len(pattern) == 1:
        return pattern in input_line
    
    # For \d character class
    elif pattern == "\d":
        for char in input_line:
            if char.isdigit() :
                return True           
        return False

    # For \w character class
    elif pattern == "\w":
        for char in input_line:
            if char.isalnum() or char == "_" :
                return True           
        return False 

    # For positive character group
    elif pattern[0] == "[" and pattern[-1]=="]":
        pattern = pattern[1:]
        pattern = pattern[:-1]
        print(pattern)
        tmp = True
        for char in input_line:
            if char in pattern:
                return True

        return False

    # For negative character group
    elif pattern[0] == "[" and pattern[-1]=="]" and pattern[1] == "^":
        pass


    else:
        raise RuntimeError(f"Unhandled pattern: {pattern}")


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
