def char_range(char_one, char_two):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for char in range(ord(char_one), ord(char_two) + 1):
        yield chr(char)
        