#
# This is a basic prompt and get response function with a twist...
# The function takes one of two arugments, it will reject both
#
# 1) Prompt="xxx" - returns a string
# 2) List = ['First string', 'Second String', ...'nth String'] - returns index
#
def getUserInput(**kwargs):
    result = None
    if kwargs is not None:
        if 'Prompt' in kwargs.keys():
            if 'List' not in kwargs.keys():
                result = raw_input(kwargs['Prompt'])
        else:
            if 'List' in kwargs.keys():
                inputNotValid = True
                while inputNotValid:
                    cntr = 0
                    for x in kwargs['List']:
                        cntr = cntr + 1
                        print "%s) %s"%(cntr, x)
                    result = raw_input("Enter Selection: ")
                    try:
                        it = int(result)
                        if it > 0 and it <= cntr:
                            inputNotValid = False
                    except ValueError:
                        inputNotValid = True
                        print 'Please enter an integer in the range 1 to %s'%(cntr)
    return result


p1 = ['Yellow', 'Blue', 'Red', 'Orange']
p2='This is a prompt: '
val=getUserInput(List=p1)
val=getUserInput(Prompt=p2)