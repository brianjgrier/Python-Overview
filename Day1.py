import sys
import json

from pprint import pprint as pp


#
# The python 2.4->2.7 version of "dump"
#
# def dump(obj):
#  for attr in dir(obj):
#    print "obj.%s = %s" % (attr, getattr(obj, attr))
#

#
# The python 2.7 and 3.5 version of "dump"
#
def dump(obj):
    for attr in dir(obj):
        print("obj.{} = {}".format(attr, getattr(obj, attr)))


def example():
    """
    This is an example of using the documentation feature within Python
    Usage: example()
            parameters: None
            returns:   None
    """
    #
    # This is a comment line.
    # the '#' can be anywhere ina line, and anything
    print(1 + 1)  # after the '#' will be treated as a comment

    return None


# dump(dump)
# print()
# print()
dump(example)
print()
print()
print('print the variable i')
i = 1 + 2

print(i)

print(example.__doc__)
print("***************************")
help(example)
#
# Alternate for python 2.x:
# print(example.func_doc)


print('The return value of "example" is: ', example())

i = 1
j = 2.0

print(type(i))
print(type(j))
print(type('hello'))


l = [1,2]
help(l)
l.append(7)
help(l.append)

print('Printing a list: {}'.format(l))

#
# Function:
# A group of statements that would otherwise be repeated throughout your code.
#

def is_prime(num):
    if type(num) == int:
        for n in range(2, num):
            if num % n == 0:
                print("Number is not prime")
                break
        else:
            print ("number is prime")
    else:
        print('Value is not an integer')

def is_prime_alt(num):
    if type(num) == int:
        prime_num = True
        for n in range(2, num):
            if num % n == 0:
                print("Number is not prime")
                prime_num = False
                break
        if prime_num == True:
            print("number is prime")

#
# Functions can be defined WITHIN a function. In this instance only the function
# that it is defined within can use this "local" function
#
def some_function():
    variable1 = 'Some String'

    def say_hi():
        print("Hello ", variable1)

    say_hi()



# Lambda Expressions
# a variant of a function but is a SINGLE expression, not a block of statements
# Used to code SIMPLE functions. For complex functions use 'def"
# can be given a label to allow the lamda function to be reused (not typical)
#
# Converting a simple function to a lambda
#
#def version of my_sqrt()
def my_sqrt(num):
    return num**0.5
#
# alternate def of my_sqrt()
def my_sqrt(num): return num**0.5

#
# Lambda variant can be assigned to a label, but typically is not
# Typically lambdas expressions are used to create "anonymous" functions
#
# Labeled lambdas
#
my_sqrt = lambda num: num**0.5

is_even = lambda num: num%2==0

#
# a Lamdba can accept more than one input value and is not limited to
is_special = lambda num1, num2: 'more than' if num1 > num2 else 'less or equals'

# Unlabeled lambdas
#
# in python 2.6 or less you CAN NOT use "print" in a lambda because it is a statement
# not an expression or a function.
#
# For more information of Lambdas and why you might want to use them
# please read this article:
# https://pythonconquerstheuniverse.wordpress.com/2011/08/29/lambda_tutorial/
#

