# Workout on Prime numbers, Amicable number, Factorial number, Armstrong number

print('-------------------------Prime Number --------------------------')
n = int(input(' enter a number'))
if n <= 1:
    print(False)
else:
    prime = True

    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            prime = False
            break

    print(prime)


print('------------------------- Amicable Number --------------------------')

x = int(input('Enter number 1: '))
y = int(input('Enter number 2: '))
sum1 = 0
sum2 = 0

for i in range(1, x):
    if x % i == 0:
        sum1 += i

for j in range(1, y):
    if y % j == 0:
        sum2 += j

if (sum1 == y and sum2 == x):
    print('Amicable!')
else:
    print('Not Amicable!')


print('------------------------- Factorial Number --------------------------')

def find_factors(n):
    factors = []
    for i in range(1, n + 1):
        if n % i == 0:
            factors.append(i)


print('------------------------Arm Strong Number ---------------------------')            
n = int(input("Enter a number: "))

temp = n
sum = 0
digits = len(str(n))

while temp > 0:
    digit = temp % 10
    sum = sum + digit ** digits
    temp = temp // 10

if sum == n:
    print("Armstrong Number")
else:
    print("Not an Armstrong Number")

print('----------------------- prime or co-prime---------------------------')
n = int(input("Enter a number: "))

if n <= 1:
    print("Not a Prime Number")
else:
    prime = True

    for i in range(2, n):
        if n % i == 0:
            prime = False
            break

    if prime:
        print("Prime Number")
    else:
        print("Not a Prime Number")
