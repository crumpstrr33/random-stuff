'''
A programmatic approach to the cypher played with after school.

For each letter, transform it into a two digit number. This code will add
together two numbers together and print the new word formed (with a little
editing for digits > 5). Pass it n words and it will try the nChoose2
possibilities that are available and print them all out.
'''
from itertools import product, combinations_with_replacement
import sys


CYPHER = [['a', 'b', 'c', 'd', 'e'],
          ['f', 'g', 'h', 'i', 'j'],
          ['k', 'l', 'm', 'n', 'o'],
          ['p', 'q', 'r', 's', 't'],
          ['u', 'v', 'w', 'x', '(yz)']]


def let_to_num(let):
    '''
    Using CYPHER array to return the two digit number that the given letter
    is represented by. Returns as a string.

    Parameters:
    let - Letter to convert to number
    '''
    for coord in product(range(5), range(5)):
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
            cyph_nums[n] += let_to_num(char)

    return cyph_nums


def add_cyph_nums(cyph_nums):
    '''
    Given a list of cypher numbers, it will add them all together, subtract 5
    from each digit greater than 5 and change 0 to 5. If the resulting number
    has an odd number of digits (due to carrying over to tens place) then
    the leading number is cut off.

    Parameters:
    cyph_nums - List of cypher numbers to add together
    '''
    new_num = ''.join(map(lambda x: str((int(x) - 1) % 5 + 1),
                          str(sum(map(int, cyph_nums)))))
    # If there's an odd num, removing leading digits. Can be thought of as
    # Taking modulo 5 of last digit place (which overflows into its 10s place)
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
        row, col = map(lambda x: int(x) - 1, num)
        # Subtract that 1 we add cause... 'human beings'
        word += CYPHER[row][col]

    return word


def calc_every_comb(*words):
    '''
    Calculates the resulting word from every combination of 2 words from the
    words given and then prints the data out. Words are tested with themselves.

    Parameters:
    words - Args parameters of every word to use.
    '''
    comb = combinations_with_replacement(words, 2)
    word_combs = []
    cyph_nums_list = []
    sum_nums_list = []
    new_words = []

    for word_comb in comb:
        word_combs.append(word_comb)
        # First turn words into numbers
        cyph_nums_list.append   (words_to_cyph_nums(*word_comb))
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
    calc_every_comb(*sys.argv[1:])
