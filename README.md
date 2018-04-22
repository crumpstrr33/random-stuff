# Random Stuff
These are just random bits of code based on ideas and random curiosity. Mostly done for learning purposeful and such. They are each described below.

## bftree.py
Will print out a breadth-first tree of a given list. Any branch factor can be given along with some other changeable options.

## bouncing.py
Uses the tkinter module to simulate bouncing squares and collision detection and response using conservation of energy and momentum.
#### TODO
Will add accurate collision

Maybe a rotational aspect in the future

## file_renaming.py
Given a directory, this code will give random names to files with a type contained in the _ftype_ keyword based on what is passed to the other keywords as described in the code triple-quote comments.
#### TODO
Ability to sepcific the exact order you want the characters (e.g. lowercase, then uppercase, then number, then lowercase, etc.)
Add a character set for allowable special characters

## fouriest.py
<img src="http://www.smbc-comics.com/comics/20130201.gif" align="right" width="306" height="335" />

This code was inspired by this comic from the webcomic Saturday Morning Breakfast Cereal which I highly recommend checking out. The direct link to the comic is found in the code.

Given a number in base 10, the code will find the "fouriest" base(s) (since multiple bases could have the same number of fours) and print them out along with their corresponding numbers. Although only 62 digits are used (lowercase, uppercase and 0-9), it can find numbers above base 62 given that the number does not use a digit 62. If this is the case, the number isn't found.
#### TODO
Allow the input of any base number
Allow the code to find numbers above base 62 with a digit above 62 if it is indeed the fouriest

## matrix_functions.py
Various functions for an NxN matrix
#### TODO
Add cooler functions

## imgur_pic_downloader.py
You give this program the hash of an imgur album (those random characters the comes at the end of the URL). It will first try downloading by using the Imgur API. This requires a valid access token to do so. If the token is invalid, or no token is given (this is done with an .ini file), it will first try to obtain a new access token using the refresh token from the .ini file and retry. If this fails, then the code will find the links of the images in the album from the HTML plain text which is probably much less reliable.

## regions_in_grid.py
Given a 2D array of 1's and 0's it will return a list of each region where a region is defined as a group of 1's that are connected either in the four cardinal directions or in the four diagonal directions. Each row of the array does not need to be the same length.
#### TODO
Add an option for periodic boundaries
Generalize to nD arrays
Allow the option for specifying what elements should be considered part of a group (can be converted to 1's and 0's easily with numpy though)

## cypher_word_adding.py
Inspired by a cypher used in an after-school program as a fun/thoughtful challenge for the kids, this code will convert words into number using the cypher (as described in the code) and add them together and return the resulting word from the sum.
#### TODO
Allow cypher grids bigger than 10x10
Allow 3 or maybe 4 dimensional grids
Allow non-square grids or grids with rows with varying lengths

## calnder
A functional calender. Not much more. Takes into account leap years.
#### TODO
Actually be able to do something with it
