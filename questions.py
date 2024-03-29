import os
import random
import string
import sys

CONSTANT_STRING_LENGTH_MIN = 3
CONSTANT_STRING_LENGTH_MAX = 10

EMPTY_STRING = "\'\'"


class QuestionGenerator:
    def __init__(self):
        pass

    @staticmethod
    def get_random_string_fixed_length(n):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for _ in range(n))
        return result_str

    def get_random_string(self):
        n = random.randint(CONSTANT_STRING_LENGTH_MIN, CONSTANT_STRING_LENGTH_MAX)
        return self.get_random_string_fixed_length(n)

    @staticmethod
    def get_random_start_stop_step(s):
        n = len(s)
        i_min, i_max = -n, n - 1
        result = [random.randint(i_min, i_max) for _ in range(3)]
        result[-1] = random.randint(-3, 3)  # Restrict step to between -3 and 3
        return result

    @staticmethod
    def parse_question(random_string, start, stop=None, step=None):
        if step is None and stop is None:
            question_string = f"\'{random_string}\'[{start}]"
            answer_string = f"\'{random_string[start]}\'"
        elif step is None:  # and stop is not None
            question_string = f'\'{random_string}\'[{start}:{stop}]'
            answer_string = f"\'{random_string[start:stop]}\'"
        else:
            question_string = f'\'{random_string}\'[{start}:{stop}:{step}]'
            answer_string = f"\'{random_string[start:stop:step]}\'" if step != 0 else 'ValueError'

        if not answer_string:
            answer_string = EMPTY_STRING
        return question_string, answer_string

    def get_question(self):
        random_string = self.get_random_string()
        start, stop, step = self.get_random_start_stop_step(random_string)

        random_roll = random.randint(1, 10)
        if random_roll <= 2:  # P(only start index) = 0.2
            question_string, answer_string = self.parse_question(random_string, start)
        elif random_roll <= 6:  # P(start:stop) = 0.4
            question_string, answer_string = self.parse_question(random_string, start, stop)
        else:  # P(start:stop:step) = 0.4
            question_string, answer_string = self.parse_question(random_string, start, stop, step)

        # Extra code to reduce chances of empty string (empirically found that it's empty most of the time)
        if answer_string == EMPTY_STRING:
            if 3 <= random_roll <= 5:  # i.e. only start, stop  # 3/4 chance to swap start and stop
                question_string, answer_string = self.parse_question(random_string, stop, start)
            elif 7 <= random_roll <= 9:  # 3/4 chance to swap start and stop
                question_string, answer_string = self.parse_question(random_string, stop, start, step)

        return question_string, answer_string


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main():
    f = open(resource_path('art.txt'), 'r')
    print(''.join([line for line in f.readlines()]))
    print('Implemented by Nicholas Mak\n')

    question_generator = QuestionGenerator()
    question_number = 1
    while True:
        question_string, answer_string = question_generator.get_question()
        print(f'Question Number {question_number}')
        print(question_string)
        user_input = input('Input your answer: ')
        print(f'Expected answer: {answer_string}\n')
        question_number += 1


if __name__ == '__main__':
    main()
