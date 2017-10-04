'''
A programmatic approach to the cypher played with after school.

For each letter, transform it into a two digit number based on a square cypher
(The number of rows must equal the number of columns). This code will add
together two numbers together and print the new word formed (with a little
editing with a modulo for digits out of range on the cypher). Pass it N words
and it will try the NChooseM that are available and print them out.
'''
from itertools import product, combinations_with_replacement, combinations
from argparse import ArgumentParser


CYPHER5 = [['a', 'b', 'c', 'd', 'e'],
           ['f', 'g', 'h', 'i', 'j'],
           ['k', 'l', 'm', 'n', 'o'],
           ['p', 'q', 'r', 's', 't'],
           ['u', 'v', 'w', 'x', 'yz']]
CYPHER6 = [['a', 'b', 'c', 'd', 'e', 'f'],
           ['g', 'h', 'i', 'j', 'k', 'l'],
           ['m', 'n', 'o', 'p', 'q', 'r'],
           ['s', 't', 'u', 'v', 'w', 'x'],
           ['yz', ' ', '1', '2', '3', '4'],
           ['5', '6', '7', '8', '9', '0']]
CYPHER = CYPHER5

def let_to_num(let):
    '''
    Using CYPHER array to return the two digit number that the given letter
    is represented by. Returns as a string.

    Parameters:
    let - Letter to convert to number
    '''
    for coord in product(range(len(CYPHER)), range(len(CYPHER))):
        if let in CYPHER[coord[0]][coord[1]]:
            return ''.join(map(lambda x: str(x + 1), coord))


def words_to_cyph_nums(*words):
    '''
    Passed n words, it will converted each word to its represented number by
    calling let_to_num on each letter and returning a list of the numbers.

    Paramters:
    words - Args of words to convert to a number
    '''
    cyph_nums = ['' for _ in range(len(words))]
    for n, word in enumerate(words):
        for char in word:
            let = let_to_num(char.lower())
            if let is None:
                raise Exception("Character '{}' ".format(let) +
                                "in word '{}' not found in cypher".format(word))
            cyph_nums[n] += let

    return cyph_nums


def add_cyph_nums(cyph_nums):
    '''
    Given a list of cypher numbers, it will add them all together and modulo
    digits greater than the size of the cypher by the length of the cypher.
    If the resulting number has an odd number of digits (due to carrying over
    to tens place) then the leading number is cut off.

    Parameters:
    cyph_nums - List of cypher numbers to add together
    '''
    new_num = ''.join(map(lambda x: str((int(x) - 1) % len(CYPHER) + 1),
                          str(sum(map(int, cyph_nums)))))
    # If there's an odd num, remove the leading digit
    if len(new_num) % 2:
        new_num = new_num[1:]
    return new_num


def decypher_num(cyph_num):
    '''
    Splits a cypher number into each letter (i.e. a list of every two digits)
    and converts that into the appropriate letter from CYPHER.

    Parameters:
    cyph_num - Number to convert back to a word
    '''
    # Creates the number pairs through some pythonic magic
    cypher_lets = list(map(''.join, zip(*[iter(cyph_num)] * 2)))
    word = ''

    for num in cypher_lets:
        # Subtract that 1 we add cause... 'human beings'
        row, col = map(lambda x: int(x) - 1, num)
        let = CYPHER[row][col]

        # Add parentheses if choice is an ambiguous one
        if len(let) > 1:
            let = '(' + let + ')'
        word += let

    return word


def calc_every_comb(*words, wta, keep_cyphers, duplicate, check_match):
    '''
    Calculates the resulting word from every combination of 2 words from the
    words given and then prints the data out. Words are tested with themselves.

    Parameters:
    words - Args parameters of every word to use
    wta - The number of words to sum for each sum
    keep_cyphers - Boolean of whether to print the cypher numbers along with
                   the words or not
    duplicate - Boolean of whether the combination of words to use should
                have duplicates (combination with replace vs. without)
    check_match - If true it will only print out the sums that create a word
                  found in words
    '''
    wta = int(wta)
    if duplicate:
        comb = combinations_with_replacement(words, wta)
    else:
        comb = combinations(words, wta)

    word_combs, cyph_nums_list, sum_nums_list, new_words = [], [], [], []
    for word_comb in comb:
        word_combs.append(word_comb)
        # First turn words into numbers
        cyph_nums_list.append(words_to_cyph_nums(*word_comb))
        # Then sum those numbers up
        sum_nums_list.append(add_cyph_nums(cyph_nums_list[-1]))
        # Then create the new word
        new_words.append(decypher_num(sum_nums_list[-1]))

    # Print stuff!
    # Constant lengths used for printing
    max_len_w = len(max(words, key=len))
    max_len_n = len(max(new_words, key=len))
    fdict = {'w': max_len_w if max_len_w > 8 else 8,
             'c': 2*max_len_w if 2*max_len_w > 10 else 10,
             'n': max_len_n if max_len_n > 10 else 10}

    # Templates for title, bar under title and for each word combo row
    row = '|' + wta * '{:^{w}}|' + '{:^{n}}|' + \
                keep_cyphers * (wta + 1) * '{:^{c}}|'
    row_titles = ['Word ' + str(x + 1) for x in range(wta)] + ['New Word'] + \
                 keep_cyphers * (['Cypher ' + str(x + 1)
                                  for x in range(wta)] + ['Sum'])
    row_bar = '|' + (wta + keep_cyphers * (wta + 1)) * '{}+' + '{}|'
    row_ext = '+' + '-' * (keep_cyphers*((1 + fdict['c']) * (wta + 1)) + \
                          wta + fdict['n'] + wta*fdict['w']) + '+'

    # Printing everything out
    print(row_ext)
    print(row.format(*row_titles, **fdict))
    print(row_bar.format(*['-' * fdict['w']] * wta, '-' * fdict['n'],
                         *['-' * fdict['c']] * (wta + 1)))
    for n, word_comb in enumerate(word_combs):
        if check_match and new_words[n] not in set(words):
            continue
        print(row.format(*word_comb, new_words[n], *cyph_nums_list[n],
                         sum_nums_list[n], **fdict))
    print(row_ext)


def print_cypher():
    '''
    Prints out cypher.
    '''
    max_len = len(max(sum(CYPHER, []), key=len))
    cols = map(lambda x: str(x).rjust(max_len), range(1, len(CYPHER) + 1))
    print(' |' + '|'.join(cols) + '|')
    for n, row in enumerate(CYPHER):
        print(n + 1, end='|')
        for let in row:
            print((max_len - len(let)) * ' ' + let, end='|')
        print()


def input_words_main():
    '''
    Give it words to sum from command line either by typing the words at the
    command line or using the --file flag to specify a txt file with space-
    separated words or use both. The -n flag tells how many words to sum. The
    -c flag is whether to print the cypher numbers along with the words. The -d
    flag is whether to allow summing duplicates of a word. And the -m flag will
    only print out sums that are a word found in the list of words given.
    '''
    parser = ArgumentParser(description='Cypher words and return the word ' +
                            'created by their sum.')
    parser.add_argument('-f', '--file', help='Text file with space-separated ' +
                        'words to sum. If words are also given along with a ' +
                        'text file, these words will be considered along ' +
                        'with the words in the text file')
    parser.add_argument('-n', '--num', help='Number of words to sum')
    parser.add_argument('-c', action='store_true', help='Will print the ' +
                        'cypher numbers along with the words')
    parser.add_argument('-d', action='store_true', help='Will allow for ' +
                        'duplicates of words to be summed')
    parser.add_argument('-m', action='store_true', help='Will only print ' +
                        'a sum if that sum matches a word in the given set ' +
                        'of words.')
    parser.add_argument('--print-cypher', action='store_true', help='Will ' +
                        'print out the cypher being used')
    parser.add_argument('words', help='Words to sum', nargs='*')
    args = parser.parse_args()

    if args.print_cypher:
        print_cypher()
    else:
        if args.file is not None:
            with open(args.file, 'r') as f:
                args.words += f.read().split()
        args.words = list(set(args.words))
        args.words.sort()

        if not args.d and len(args.words) < int(args.num or 2):
            raise Exception('The number of words must be at least equal to the ' +
                            'number of words being summed if no replacement.')

        calc_every_comb(*args.words, wta=args.num or 2, keep_cyphers=args.c,
                        duplicate=args.d, check_match=args.m)


if __name__ == "__main__":
    input_words_main()
