def overlaps(pos, length, other_pos, other_length):
    return pos <= other_pos + other_length - 1 and other_pos <= pos + length - 1

def count_words(string):
    return len(string.split())
