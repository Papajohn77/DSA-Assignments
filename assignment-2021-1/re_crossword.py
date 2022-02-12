import sre_yield
import re
import string
import argparse


class WordInformation:
    # parts[0] => The number of the word.
    # parts[1] => The letters of the word ('.' if they are unknown).
    # parts[2::2] => The numbers of the intersected words.
    # parts[3::2] => The positions of the intersections.
    def __init__(self, parts, regexes):
        self.word = parts[0]
        self.answer = ""
        self.pattern = ""
        self.visited = False
        self.length = len(parts[1])
        self.initial_letters = []
        self.filled_letters = []
        self.intersects = {}

        self.check_for_completed_words(parts[1], regexes)

        self.check_for_initial_letters(parts[1])

        self.initialize_intersects(parts[2::2], parts[3::2])

    def check_for_completed_words(self, letters, regexes):
        if not ('.' in letters):
            self.answer = letters
            self.visited = True
            for ptrn in regexes:
                if re.search(ptrn, self.answer):
                    self.pattern = ptrn
                    used_patterns.append(ptrn)
                    break

    def check_for_initial_letters(self, letters):
        for index, letter in enumerate(letters):
            if letter != '.':
                self.initial_letters.append(index)
                self.initial_letters.append(letter)

    def add_filled_letter(self, position, letter):
        self.filled_letters.append(position)
        self.filled_letters.append(letter)

    def initialize_intersects(self, intersected_words, positions):
        for intersected_word, position in zip(intersected_words, positions):
            self.intersects[intersected_word] = position

# ------------------- Outside of the class ------------------------


def create_crossword(filename, regexes):
    crossword = {}
    with open(filename) as crossword_file:
        for line in crossword_file:
            if line.endswith('\n'):
                parts = line[:-1].split(',')
            else:
                parts = line.split(',')
            crossword[parts[0]] = WordInformation(parts, regexes)
    return crossword


def read_regexes(filename):
    regexes = []
    with open(filename) as regexes_file:
        for line in regexes_file:
            if line.endswith('\n'):
                regexes.append(line[:-1])
            else:
                regexes.append(line)
    return regexes


def has_words(crossword):
    for word_info in crossword.values():
        if word_info.visited == False:
            return True
    return False


def choose_word(crossword):
    return max([(word_info.word, (len(word_info.initial_letters)/2 + 
        len(word_info.filled_letters)/2)/word_info.length)
        for word_info in list(crossword.values()) 
        if word_info.visited == False], key=lambda x: x[1])[0]


def check_len(word_length, possible_str):
    return word_length == len(possible_str)


# letters = [position, 'letter', position, 'letter' ...]
def check_letters(letters, possible_str):
    if len(letters) == 0:
        return True

    if possible_str[letters[0]] == letters[1]:
        return check_letters(letters[2:], possible_str)
    return False


# intersected_words = [(word, position), (word, position) ...]
''' Updates the filled_letters of the words that are intersected with 
the word passed as an argument to the method.'''
def update_filled_letters(crossword, word):
    curr_word = crossword[word]
    intersected_words = list(curr_word.intersects.items())

    for inter_word, inter_position in intersected_words:
        intersected_word = crossword[inter_word]
        if intersected_word.answer != '':
            continue
        intersection_position = int(inter_position)
        curr_word_intersection_position = int(
            intersected_word.intersects[curr_word.word])

        # If the method have been called for reset.
        if curr_word.answer == '':
            intersected_word.filled_letters.pop()
            intersected_word.filled_letters.pop()
            continue

        letter = curr_word.answer[curr_word_intersection_position]
        intersected_word.add_filled_letter(intersection_position, letter)


# intersected_words = [(word, position), (word, position) ...]
''' If a word has an initial letter in a position where is intersected 
with another word, this method will make sure that this letter will also
be in the initial letters of the other word as well.'''
def update_initial_letters(crossword):
    for word in crossword.keys():
        curr_word = crossword[word]
        intersected_words = list(curr_word.intersects.items())

        for inter_word, inter_position in intersected_words:
            intersected_word = crossword[inter_word]
            if intersected_word.answer != '':
                continue
            intersection_position = int(inter_position)
            curr_word_intersection_position = int(
                intersected_word.intersects[word])

            # initial_letters = [position, 'letter', position, 'letter' ...]
            if curr_word_intersection_position in curr_word.initial_letters:
                index = curr_word.initial_letters.index(
                    curr_word_intersection_position)
                intersected_word.initial_letters.append(intersection_position)
                intersected_word.initial_letters.append(
                    curr_word.initial_letters[index + 1])


def solve_crossword(crossword, regexes):
    if has_words(crossword):
        word = choose_word(crossword)
        curr_word = crossword[word]
        for pattern in regexes:
            if pattern not in used_patterns:
                for possible_str in sre_yield.AllStrings(pattern, max_count=5,
                charset=string.ascii_uppercase):
                    if not check_len(curr_word.length, possible_str):
                        continue
                    if not check_letters(curr_word.initial_letters, possible_str):
                        continue
                    if not check_letters(curr_word.filled_letters, possible_str):
                        continue
                    
                    curr_word.answer = possible_str
                    curr_word.pattern = pattern
                    curr_word.visited = True
                    update_filled_letters(crossword, word)
                    used_patterns.append(pattern)
                    solve_crossword(crossword, regexes)

                    if not has_words(crossword):
                        return
            
                    # If the answer led to a deadlock, reset
                    curr_word.answer = ''
                    used_patterns.remove(pattern)
                    curr_word.visited = False
                    update_filled_letters(crossword, word)


def print_results(crossword):
    for word_info in sorted(crossword.values(), key=lambda x: int(x.word)):
        print(word_info.word, word_info.pattern, word_info.answer)


if __name__ == '__main__':
    used_patterns = []

    parser = argparse.ArgumentParser()
    parser.add_argument('file1')
    parser.add_argument('file2')
    args = parser.parse_args()

    regexes = read_regexes(args.file2)
    crossword = create_crossword(args.file1, regexes)
    update_initial_letters(crossword)

    solve_crossword(crossword, regexes)
    print_results(crossword)
