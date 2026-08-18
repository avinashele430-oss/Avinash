#Write a program to remove lowercase substrings from a given string.
print('remove lowercase substrings from a given string')
s = input("Enter a string: ")

result = ""

for ch in s:
    if not ch.islower():
        result += ch

print("After removing lowercase characters:", result)

expression = input("Enter an expression: ")

result = eval(expression)

print("Result:", result)

#program to read an expression and evaluate it

expression = input("Enter an expression: ")

result = eval(expression)

print("Result:", result)

#Insert spaces between words starting with capital letters
print('Insert spaces between words starting with capital letters')
s = input("Enter a string: ")

result = ""

for ch in s:
    if ch.isupper() and result:
        result += " "
    result += ch

print("Result:", result)

#Remove the parenthesis area in a string
print('Remove the parenthesis area in a string')
s = input("Enter a string: ")

result = ""
inside = False

for ch in s:
    if ch == '(':
        inside = True
    elif ch == ')':
        inside = False
    elif not inside:
        result += ch

print("Result:", result)

# split a string with multiple delimiters.
print(' split a string with multiple delimiters')
import re

s = input("Enter a string: ")

result = re.split(r'[,;: ]+', s)

print("Split string:", result)

#find all adverbs and their positions in a given sentence.
print(' find all adverbs and their positions in a given sentence')

import re

s = input("Enter a sentence: ")

words = s.split()

for i, word in enumerate(words):
    clean_word = re.sub(r'[^\w]', '', word)

    if clean_word.lower().endswith("ly"):
        print("Adverb:", clean_word, "Position:", i + 1)
