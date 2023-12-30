from python_tca2.alignment_utils import print_frame


def dice_match1(word1, word2, dice_min_counting_score):
    # print_frame()
    word1_lower_case = word1.lower()
    word2_lower_case = word2.lower()

    unique_bigrams1 = {
        word1_lower_case[i : i + 2] for i in range(len(word1_lower_case) - 1)
    }
    unique_bigrams2 = {
        word2_lower_case[i : i + 2] for i in range(len(word2_lower_case) - 1)
    }

    count_bigrams1 = len(unique_bigrams1)
    count_bigrams2 = len(unique_bigrams2)

    count_shared_bigrams = len(unique_bigrams1.intersection(unique_bigrams2))

    dice_score = (
        (2 * count_shared_bigrams) / (count_bigrams1 + count_bigrams2)
        if count_bigrams1 != 0 and count_bigrams2 != 0
        else 0
    )

    return dice_score >= dice_min_counting_score


def dice_match2(word_a, word_b, word_c, type_, dice_min_counting_score):
    # print_frame()
    phrase_word1, phrase_word2 = "", ""
    word = ""

    if type_ == "2-1":
        phrase_word1 = word_a
        phrase_word2 = word_b
        word = word_c
    elif type_ == "1-2":
        word = word_a
        phrase_word1 = word_b
        phrase_word2 = word_c
    else:
        # ### program error
        return False

    word_lower_case = word.lower()
    phrase_word1_lower_case = phrase_word1.lower()
    phrase_word2_lower_case = phrase_word2.lower()

    unique_bigrams_in_word = {}
    count_bigrams_in_word = 0
    for i in range(len(word_lower_case) - 1):
        unique_bigrams_in_word[word_lower_case[i : i + 2]] = 1
    count_bigrams_in_word = len(unique_bigrams_in_word)

    unique_bigrams_in_phrase_word1 = {}
    count_bigrams_in_phrase_word1 = 0
    for i in range(len(phrase_word1_lower_case) - 1):
        unique_bigrams_in_phrase_word1[phrase_word1_lower_case[i : i + 2]] = 1
    count_bigrams_in_phrase_word1 = len(unique_bigrams_in_phrase_word1)

    count_shared_bigrams1 = 0
    for bigram in unique_bigrams_in_word.keys():
        if bigram in unique_bigrams_in_phrase_word1:
            count_shared_bigrams1 += 1

    unique_bigrams_in_phrase_word2 = {}
    count_bigrams_in_phrase_word2 = 0
    for i in range(len(phrase_word2_lower_case) - 1):
        unique_bigrams_in_phrase_word2[phrase_word2_lower_case[i : i + 2]] = 1
    count_bigrams_in_phrase_word2 = len(unique_bigrams_in_phrase_word2)

    count_shared_bigrams2 = 0
    for bigram in unique_bigrams_in_word.keys():
        if bigram in unique_bigrams_in_phrase_word2:
            count_shared_bigrams2 += 1

    dice_score1 = 0.0
    if count_bigrams_in_word != 0 and count_bigrams_in_phrase_word1 != 0:
        dice_score1 = count_shared_bigrams1 / count_bigrams_in_phrase_word1

    dice_score2 = 0.0
    if count_bigrams_in_word != 0 and count_bigrams_in_phrase_word2 != 0:
        dice_score2 = count_shared_bigrams2 / count_bigrams_in_phrase_word2

    return (dice_score1 >= dice_min_counting_score) and (
        dice_score2 >= dice_min_counting_score
    )


def anchor_match(compiled_anchor_pattern, word):
    # print_frame()
    # is the word word an occurrence of the anchor word anchor_word?
    matcher = compiled_anchor_pattern.match(word)
    return bool(matcher)


def bad_length_correlation(length1, length2, element_count1, element_count2, ratio):
    # print_frame()
    kill_limit = 0.5  # less tolerant limit for 1-2 and 2-1, above which such alignments score lethally low
    c = 2 * abs(0.0 + ratio * length1 - length2) / (ratio * length1 + length2)
    return (
        element_count1 > 0 and element_count2 > 0 and element_count1 != element_count2
    ) and (c > kill_limit)


def adjust_for_length_correlation(
    score, length1, length2, element_count1, element_count2, ratio
):
    # print_frame()
    new_score = 0.0
    lower_limit = 0.4
    upper_limit = 1.0
    kill_limit = 0.5
    c = 2 * abs(0.0 + ratio * length1 - length2) / (ratio * length1 + length2)

    if element_count1 > 0 and element_count2 > 0 and element_count1 != element_count2:
        if c < lower_limit / 2:
            new_score = score + 2
        elif c < lower_limit:
            new_score = score + 1
        elif c > kill_limit:
            new_score = -99999.0  # or any other low score value
        else:
            new_score = score
    else:
        if c < lower_limit / 2:
            new_score = score + 2
        elif c < lower_limit:
            new_score = score + 1
        elif c > upper_limit:
            new_score = score / 3
        else:
            new_score = score

    return new_score
