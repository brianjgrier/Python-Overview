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
#
# Alternate for python 2.x:
# print(example.func_doc)


print('The return value of "example" is: ', example())

i = 1
j = 2.0

print(type(i))
print(type(j))
print(type('hello'))
