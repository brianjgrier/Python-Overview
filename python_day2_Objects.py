def dump(obj):
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))


#
# Class  - a description of an object
#       Attributes
#       Actions (Method/function)
# Object - an instance of a class
#

class Animal():
    legs = 2
    covering  = None
    mass      = 0
#    tail      = None

    def __init__(self, weight, hasTail=None):
        print('Creating an animal')
        self.tail = hasTail
        self.mass = weight

    def speak(self):
        print('I am Groot')


class Bird(Animal):

    def __init__(self, weight, hasFeathers=True):
        Animal.__init__(self, weight, hasTail='No')
        print('Turning the animal into a type of bird')
        if hasFeathers == True:
            self.covering = 'Feathers'
        else:
            self.covering = 'Hair like feathers'

    def speak(self):
        print('Chirp')


class Canine(Animal):

    def __init__(self, weight, hasFur=True):
#
# This will work in python 2.x or 3.x
        Animal.__init__(self, weight, hasTail='Yes')
        print('Turning the animal into a type of dog')
        self.legs = 4
        if hasFur == True:
            self.covering = 'Fur'
        else:
            self.covering = 'Hairless'

    def speak(self):
        print('Woof')

#
# If you are coing from a different OO language you may be used to using
# the "super" class nomenclature. This is how this works in Python.
#
# the Python 2.x object definition

class Bear(Animal, object):
    def __init__(self, weight, hasFur=True):
        super(Bear, self).__init__(weight, hasTail='Yes, a tiny one')

        print('Turning the animal into a type of bear')
        self.legs = 4
        if hasFur == True:
            self.covering = 'Fur'
        else:
            self.covering = 'Nope'

    def speak(self):
        print('GRRR')

    def sayWhat(self):
        super(Bear, self).speak()
#
# The Python 3.x way
#class Bear(Animal):
#        super().__init__(weight, hasTail='Yes, a tiny one')
#        print('Turning the animal into a type of bear')
#        self.legs = 4
#        if hasFur == True:
#            self.covering = 'Fur'
#        else:
#            self.covering = 'Nope'
#
#    def speak(self):
#        print('GRRR')
#
#    def sayWhat(self):
#        super().speak()
#

#
# The main program starts here...
#

emu = Bird(hasFeathers = False, weight=100)

mutt = Canine(weight=15)

grizzly = Bear(weight=1200)

emu.speak()
mutt.speak()
grizzly.speak()
grizzly.sayWhat()
