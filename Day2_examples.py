a=1
b=2
c='2'
myList = [1, 3, 129, 500]
myDict = {
    1   : 'The Number one',
    'it': 'The label "it"',
    }

if a == b:
    print "same"

if a != b:
    print "different"

if a == b:
    print "same"
else:
    print "not same"
    
if a in myList:
    print "Found it!"

if b not in myList:
    print "Not here"

if a in myDict:
    print myDict[a]
    
#
# for really old versions (python 2.4 and earlier)
#
if a in myDict.keys():
    print(myDict[a])

#
# There is no 'C' switch-case/default statement
# You have to implement with if/elif statements
#
# if
# elif
# else
#
if a == b:
    print 1
elif c == str(b):
    print "same"
elif "hello" == "hello":
    print "should not get here'
else:
    print "nothing worked"


#
# Compound if
# You can stack as many as you want BUT...
# You are still limited to a single line which means you cannot format
# your statement for readability.
#
# if expr conjunction expr conjuntion expr:
#
if a != b and b == int(c):
    print "that worked"
else:
    print "that didn't work"

#
# Other languages allow you to do this:
# if a != b AND
#    b == int(c):


#
# The for statement (with range statement)
#

for i in range(1,10):
    print i

for i in range(1, 10, 2):
    print i

#
# Range defaults to a positive step so this does not work
#
for i in range(1, -10):
    print i

#
# But adding a negative step will let it work
#
for i in range(1, -10, -1):
    print i

#
# for more information on range/xrange please refer to:
#     http://pythoncentral.io/pythons-range-function-explained/
#

#
# The 'else' statement used with the 'for' statement
#
# For some reason unbeknownest to me...
# These statements will not cut and paste into IDLE's interactive window
# 
a = 10
for i in range(0, 20, 3):
    if a == i:
        print "leaving the for loop"
        break
else:
    print 'made it all the way through'

a = 9
for i in range(0, 20, 3):
    if a == i:
        print "leaving the for loop"
        break
else:
    print 'made it all the way through'



#
# Procedures
#

def myProc1():
    pass

#
# unlike other languages you DO NOT define a return type
# You just return a value. But please document it.
#
def myProc2():
    '''
    myProc - Does nothing
             Parameters - None
             Returns    - True
    '''
    return True

def myAdd(a, b):
    '''
    myAdd - Does my special version of addition
            Parameters - value1, value2
            return     - the result of my special function
    '''
    if a > b:
        step = -1
    else:
        step = 1
    result = 0
    for i in range(a, b, step):
        result += i
    return result

def myAdd2(a=0, b=10):
    '''
    myAdd - Does my special version of addition
            Parameters - value1 (default value = 0)
                         value2 (default value = 10)
            return     - the result of my special function
    '''
    if a > b:
        step = -1
    else:
        step = 1
    result = 0
    for i in range(a, b, step):
        result += i
    return result


#
myAdd(1,10)

#
# you can use the parameter names in your program
#
myAdd(a=1, b=10)

#
# Using paramter names you can put parameters in any order
#
myAdd(b=10, a=1)

#
# If you have default values you can leave parameters
#
myAdd2()
myAdd2(b=100)

