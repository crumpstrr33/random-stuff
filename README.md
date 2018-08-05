# Random Stuff
These are just random bits of code based on ideas and random curiosity. Mostly done for learning purposeful and such. They are each described below.

## bftree.py
Will print out a breadth-first tree of a given list. Any branch factor can be given along with some other changeable options.

## fouriest.py
<img src="http://www.smbc-comics.com/comics/20130201.gif" align="right" width="306" height="335" />

This code was inspired by this comic from the webcomic Saturday Morning Breakfast Cereal which I highly recommend checking out. The direct link to the comic is found in the code.

Given a number in base 10, the code will find the "fouriest" base(s) (since multiple bases could have the same number of fours) and print them out along with their corresponding numbers. Although only 62 digits are used (lowercase, uppercase and 0-9), it can find numbers above base 62 given that the number does not use a digit 62. If this is the case, the number isn't found.

## imgur_pic_downloader.py
You give this program the hash of an imgur album (those random characters the comes at the end of the URL). It will first try downloading by using the Imgur API. This requires a valid access token to do so. If the token is invalid, or no token is given (this is done with an .ini file), it will first try to obtain a new access token using the refresh token from the .ini file and retry. If this fails, then the code will find the links of the images in the album from the HTML plain text which is probably much less reliable.

## cypher_word_adding.py
Inspired by a cypher used in an after-school program as a fun/thoughtful challenge for the kids, this code will convert words into number using the cypher (as described in the code) and add them together and return the resulting word from the sum.

## orbits.py
Simulates Newtonian orbital dynamics and displays the orbits via Qt.

## calender
A functional calender. Not much more. Takes into account leap years.
