
import sys


def tokenize_pattern(pattern):
    tokens = []
    i = 0

    while i < len(pattern):
        char = pattern[i]

        if char == "\\":
            if i + 1 >= len(pattern):
                raise ValueError("Trailing escape")

            tokens.append((pattern[i:i + 2], None))
            i += 2

        elif char == "[":
            end = pattern.find("]", i + 1)

            if end == -1:
                raise ValueError("Unclosed character class")

            tokens.append((pattern[i:end + 1], None))
            i = end + 1

        elif char in "?+*":
            if not tokens:
                raise ValueError("Quantifier without preceding token")

            base, quantifier = tokens[-1]

            if quantifier is not None:
                raise ValueError("Repeated quantifier")

            tokens[-1] = (base, char)
            i += 1

        else:
            tokens.append((char, None))
            i += 1

    return tokens


def match_char(char, token):
    if token == r"\d":
        return char.isdigit()

    if token == r"\w":
        return char.isalnum() or char == "_"

    if token.startswith("[") and token.endswith("]"):
        content = token[1:-1]

        if content.startswith("^"):
            return char not in content[1:]

        return char in content

    if token.startswith("\\"):
        return char == token[1:]

    return char == token


def match_tokens(text, tokens, token_idx, char_idx, memo):
    state = (token_idx, char_idx)

    if state in memo:
        return memo[state]

    if token_idx == len(tokens):
        return char_idx

    token, quantifier = tokens[token_idx]
    result = None

    if quantifier is None:
        if char_idx < len(text) and match_char(text[char_idx], token):
            result = match_tokens(
                text, tokens, token_idx + 1,
                char_idx + 1, memo
            )

    elif quantifier == "?":
        # Greedily try one occurrence, then zero.
        if char_idx < len(text) and match_char(text[char_idx], token):
            result = match_tokens(
                text, tokens, token_idx + 1,
                char_idx + 1, memo
            )

        if result is None:
            result = match_tokens(
                text, tokens, token_idx + 1,
                char_idx, memo
            )

    elif quantifier in ("+", "*"):
        end = char_idx

        while end < len(text) and match_char(text[end], token):
            end += 1

        minimum = char_idx + 1 if quantifier == "+" else char_idx

        # Greedy matching with backtracking.
        for candidate in range(end, minimum - 1, -1):
            result = match_tokens(
                text, tokens, token_idx + 1,
                candidate, memo
            )

            if result is not None:
                break

    memo[state] = result
    return result


def match_pattern(text, pattern):
    anchored_start = pattern.startswith("^")

    if anchored_start:
        pattern = pattern[1:]

    anchored_end = pattern.endswith("$")

    if anchored_end:
        pattern = pattern[:-1]

    tokens = tokenize_pattern(pattern)

    starts = (0,) if anchored_start else range(len(text) + 1)

    for start in starts:
        end = match_tokens(text, tokens, 0, start, {})

        if end is not None:
            if not anchored_end or end == len(text):
                return True

    return False


def main():
    if len(sys.argv) != 3 or sys.argv[1] != "-E":
        print("Usage: ./your_program.sh -E <pattern>", file=sys.stderr)
        sys.exit(1)

    pattern = sys.argv[2]
    text = sys.stdin.read()

    try:
        matched = match_pattern(text, pattern)
    except ValueError as error:
        print(f"Invalid pattern: {error}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0 if matched else 1)


if __name__ == "__main__":
    main()
