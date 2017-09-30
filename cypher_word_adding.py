'''
A programmatic approach to the cypher played with after school.

For each letter, transform it into a two digit number based on a square cypher
(The number of rows must equal the number of columns). This code will add
together two numbers together and print the new word formed (with a little
editing with a modulo for digits out of range on the cypher). Pass it n words
and it will try the nChoose2 that are available and print them all out.
'''
from itertools import product, combinations_with_replacement
from argparse import ArgumentParser


CYPHER = [['a', 'b', 'c', 'd', 'e'],
          ['f', 'g', 'h', 'i', 'j'],
          ['k', 'l', 'm', 'n', 'o'],
          ['p', 'q', 'r', 's', 't'],
          ['u', 'v', 'w', 'x', 'yz']]
'''
CYPHER = [['a', 'b', 'c', 'd', 'e', 'f'],
          ['g', 'h', 'i', 'j', 'k', 'l'],
          ['m', 'n', 'o', 'p', 'q', 'r'],
          ['s', 't', 'u', 'v', 'w', 'x'],
          ['yz', ' ', '1', '2', '3', '4'],
          ['5', '6', '7', '8', '9', '0']]
'''

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
            let = let_to_num(char)
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
    mod_lim = 10 - len(CYPHER)
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


def calc_every_comb(*words, words_to_add):
    '''
    Calculates the resulting word from every combination of 2 words from the
    words given and then prints the data out. Words are tested with themselves.

    Parameters:
    words - Args parameters of every word to use.
    '''
    comb = combinations_with_replacement(words, int(words_to_add))
    word_combs = []
    cyph_nums_list = []
    sum_nums_list = []
    new_words = []

    for word_comb in comb:
        word_combs.append(word_comb)
        # First turn words into numbers
        cyph_nums_list.append(words_to_cyph_nums(*word_comb))
        # Then sum those numbers up
        sum_nums_list.append(add_cyph_nums(cyph_nums_list[-1]))
        # Then create the new word
        new_words.append(decypher_num(sum_nums_list[-1]))

    # Print stuff!
    max_len_w = len(max(words, key=len))
    max_len_n = len(max(new_words, key=len))
    fdict = {'w': max_len_w if max_len_w > 8 else 8,
             'c': 2*max_len_w if 2*max_len_w > 10 else 10,
             'n': max_len_n if max_len_n > 10 else 10}
    row = '|{:^{w}}|{:^{w}}|{:^{n}}|{:^{c}}|{:^{c}}|{:^{c}}|'
    print('+' + '-' * (5 + fdict['n'] + 2*fdict['w'] + 3*fdict['c']) + '+')
    print(row.format('Word 1', 'Word 2', 'New Word', 'Cypher 1', 'Cypher 2',
                     'Sum', **fdict))
    print('|{}+{}+{}+{}+{}+{}|'.format(*['-' * fdict['w']] * 2,
                                       '-' * fdict['n'],
                                       *['-' * fdict['c']] * 3))
    for n, word_comb in enumerate(word_combs):
        print(row.format(*word_comb, new_words[n], *cyph_nums_list[n],
                         sum_nums_list[n], **fdict))
    print('+' + '-' * (5 + fdict['n'] + 2*fdict['w'] + 3*fdict['c']) + '+')


if __name__ == "__main__":
    parser = ArgumentParser(description='Cypher words and return the word of' +
                            'their sums. Give space-separated words to sum.')
    parser.add_argument('-n', metavar='num', help='Number of words to sum')
    parser.add_argument('words', help='Words to sum', nargs='*')
    args = parser.parse_args()

    calc_every_comb(*args.words, words_to_add=args.n or 2)
