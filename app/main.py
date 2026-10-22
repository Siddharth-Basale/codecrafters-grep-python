import sys


def parse_tokens(pattern):
    """
    Parses a pattern string into a structured regex tree.
    Supports:
      - Literal characters
      - Escaped characters (\\d, \\w, \\\\, etc.)
      - Character classes ([abc], [^abc])
      - Quantifiers (?, +, *)
      - Alternation (|)
      - Grouping ((...))
    """
    def parse_expr(i):
        branches = []
        current_seq = []

        while i < len(pattern):
            char = pattern[i]

            if char == "|":
                branches.append(current_seq)
                current_seq = []
                i += 1

            elif char == ")":
                branches.append(current_seq)
                return ("ALT", branches), i + 1

            elif char == "(":
                sub_node, i = parse_expr(i + 1)
                # Check for a trailing quantifier on the group: (abc)+, (cat|dog)?
                quantifier = None
                if i < len(pattern) and pattern[i] in "?+*":
                    quantifier = pattern[i]
                    i += 1
                current_seq.append((sub_node, quantifier))

            elif char == "\\":
                if i + 1 >= len(pattern):
                    raise ValueError("Trailing escape")
                tok = pattern[i:i + 2]
                i += 2
                quantifier = None
                if i < len(pattern) and pattern[i] in "?+*":
                    quantifier = pattern[i]
                    i += 1
                current_seq.append((("CHAR", tok), quantifier))

            elif char == "[":
                end = pattern.find("]", i + 1)
                if end == -1:
                    raise ValueError("Unclosed character class")
                tok = pattern[i:end + 1]
                i = end + 1
                quantifier = None
                if i < len(pattern) and pattern[i] in "?+*":
                    quantifier = pattern[i]
                    i += 1
                current_seq.append((("CHAR", tok), quantifier))

            elif char in "?+*":
                raise ValueError("Quantifier without preceding token")

            elif char == ".":
                i += 1
                quantifier = None
                if i < len(pattern) and pattern[i] in "?+*":
                    quantifier = pattern[i]
                    i += 1
                current_seq.append((("CHAR", "."), quantifier))

            else:
                tok = char
                i += 1
                quantifier = None
                if i < len(pattern) and pattern[i] in "?+*":
                    quantifier = pattern[i]
                    i += 1
                current_seq.append((("CHAR", tok), quantifier))

        branches.append(current_seq)
        return ("ALT", branches), i

    ast, _ = parse_expr(0)
    return ast


def match_char(char, token):
    if token == ".":
        return char != "\n"

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


def match_node(node, text, char_idx):
    """
    Returns a set of possible character indices in text after matching `node`.
    `node` is a tuple (node_type, data), e.g.:
      - ("CHAR", token_str)
      - ("ALT", list_of_sequences)
    """
    kind, data = node

    if kind == "CHAR":
        if char_idx < len(text) and match_char(text[char_idx], data):
            return {char_idx + 1}
        return set()

    if kind == "ALT":
        branches = data
        results = set()
        for branch in branches:
            results.update(match_sequence(branch, text, char_idx))
        return results

    return set()


def match_sequence(seq, text, char_idx):
    """
    Matches an ordered list of (node, quantifier) elements.
    Returns all valid ending character indices.
    """
    current_positions = {char_idx}

    for item, quantifier in seq:
        next_positions = set()

        for pos in current_positions:
            if quantifier is None:
                next_positions.update(match_node(item, text, pos))

            elif quantifier == "?":
                # 0 matches
                next_positions.add(pos)
                # 1 match
                next_positions.update(match_node(item, text, pos))

            elif quantifier == "+":
                # 1 or more matches
                frontier = match_node(item, text, pos)
                seen = set(frontier)
                while frontier:
                    nxt = set()
                    for p in frontier:
                        more = match_node(item, text, p) - seen
                        nxt.update(more)
                        seen.update(more)
                    frontier = nxt
                next_positions.update(seen)

            elif quantifier == "*":
                # 0 or more matches
                seen = {pos}
                frontier = {pos}
                while frontier:
                    nxt = set()
                    for p in frontier:
                        more = match_node(item, text, p) - seen
                        nxt.update(more)
                        seen.update(more)
                    frontier = nxt
                next_positions.update(seen)

        current_positions = next_positions
        if not current_positions:
            return set()

    return current_positions


def match_pattern(text, pattern):
    anchored_start = pattern.startswith("^")
    if anchored_start:
        pattern = pattern[1:]

    anchored_end = pattern.endswith("$")
    if anchored_end:
        pattern = pattern[:-1]

    ast = parse_tokens(pattern)

    # Grep checks match per line or anywhere in the text
    starts = [0] if anchored_start else range(len(text) + 1)

    for start in starts:
        ends = match_node(ast, text, start)
        for end in ends:
            if not anchored_end or end == len(text):
                return True

    return False


def main():
    if len(sys.argv) != 3 or sys.argv[1] != "-E":
        print("Usage: ./your_program.sh -E <pattern>", file=sys.stderr)
        sys.exit(1)

    pattern = sys.argv[2]
    text = sys.stdin.read()

    # Strip single trailing newline if input came from echo without -n
    if text.endswith("\n"):
        text = text[:-1]

    try:
        matched = match_pattern(text, pattern)
    except ValueError as error:
        print(f"Invalid pattern: {error}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0 if matched else 1)


if __name__ == "__main__":
    main()