"""
This code finds the fouriest number given an input number as inspired by:
http://www.smbc-comics.com/?id=2874

The DIGITS list below contains the digits used. So base 16, for example, will
use 0 to g. So this code can safely calculated base conversions up to base 62.
But can also calculate to an arbitrarily high base given that this conversion
does not use digits higher than the current 62 in DIGITS. For example, given
4048, there are 5 fouriest numbers (each with 2 4's) and one of these is 44 in
base 1011. Alternatively, an arbitrary number of characters can be added on to
or taken off DIGITS as seen fit.
"""
import sys

import numpy as np

DIGITS = list(
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    + "αβΓγΔδεζηΘθικΛλμνΞξΠπρΣσςτυΦφχΨψΩω"
    + "БбвГгДдЁёЖжЗзИиЙйЛлмнптУфЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
)
PLACEHOLDER = "~"


def base10_to_base(n, b):
    """
    Converts a base 10 number to a different base.

    Parameters:
    n - Base 10 number to be converted
    b - Base to convert n into
    """
    # Find the most significant digit in base b
    # e.g. For 10, 8 (2^3) is the most significant digit in base 2
    for i in range(n):
        if n <= b ** i:
            msd = i - 1
            break

    d = []
    for i in range(msd, -1, -1):
        # Find out how many times this digit goes into the number
        # e.g. 2**3 goes into 10 one time so curr_d=1
        curr_d = int(n / b ** i)

        # Will try to grab the appropriate digit, if the digit is too high for
        # digits, it will just return a list of zeros (so the code wont stop
        # at max_num_four > len(d))
        try:
            d.append(DIGITS[curr_d])
        except:
            # print('Cannot print digit, out of range of digit list')
            # print(f'Need digit {curr_d} but max allowed is {len(DIGITS)}.')
            d.append(PLACEHOLDER)

        # Subtract from the number
        # (e.g. subtract 2**3 * 1 from 10 to get 2)
        if curr_d != 0:
            n -= b ** i * curr_d

        # If zero is reached, then the remaining digits will be zero
        if n == 0:
            d += (msd + 1 - len(d)) * ["0"]
            break

    return d


def fouriest_find(num):
    """
    Finds the base(s) and their resulting number(s) with the most number of
    4's.

    Parameters:
    num - Base 10 number whose fouriest number will be found
    """
    max_num_four = 0
    max_fours = np.array([])

    for i in range(2, num):
        d = base10_to_base(num, i)

        # Find how many fours the number d has
        num_fours = d.count("4")

        # If new maximum of number of 4s, start list over
        if num_fours > max_num_four:
            max_num_four = num_fours
            max_fours = np.array([i, "".join(d)])
        # If same number of 4s, add to list
        elif num_fours == max_num_four:
            max_fours = np.append(max_fours, [i, "".join(d)])

        # If our current fouriest numbers have more 4's then the current
        # length of our numbers, then break. We won't find fourier numbers
        if max_num_four > len(d):
            break

    max_fours = max_fours.reshape(-1, 2)

    return max_fours, max_num_four


def main():
    num = int(sys.argv[1])
    max_fours, max_num_four = fouriest_find(num)

    if max_num_four == 0:
        print(f"There are no fourier numbers for {num}.")
    elif len(max_fours) == 1:
        max_four = max_fours[0]
        print(f"The fouriest number for {num} is {max_four[1]} in base {max_four[0]}.")
    else:
        print(f"There are multiple fouriest numbers for {num}.\n\nThey are:")
        for max_four in max_fours:
            print(f"{max_four[1]:>15} in base {max_four[0]:>5}")


if __name__ == "__main__":
    main()
