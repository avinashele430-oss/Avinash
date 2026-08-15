#Write a program to remove lowercase substrings from a given string.
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

