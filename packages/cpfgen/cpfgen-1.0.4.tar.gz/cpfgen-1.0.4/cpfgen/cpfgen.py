#! /usr/bin/python3

from random import seed
from random import randint

cpf = []
seed()

for _ in range(9):
	cpf.append(randint(0,9))

sum = 0
weight = 10

for i in range(9):
	sum = sum + cpf[i]*weight
	weight = weight - 1

digit = 0

if sum % 11 >= 2:
	digit = 11 - (sum % 11)

cpf.append(digit)

sum = 0
weight = 11

for i in range(10):
	sum = sum + cpf[i]*weight
	weight = weight - 1

if sum % 11 >= 2:
	digit = 11 - (sum % 11)

cpf.append(digit)

print(''.join(map(str, cpf)))
