"""This is a very basic template example. This template do nothing, just
print a message in stdout. Of course, it not very useful :)
"""

import random
from time import sleep

def hello():
    print "Hello world!"

def bye():
    print "Good bye cruel world..."

@async
def launch_async(arg):
    sleep(random.randint(2,10))
    print "Hola %s" % arg

@serial
def pfinish():
    print "Finished!"

def main(*args):
    # next two in serial
    hello()
    bye()
    # next in parallel
    for x in args:
        launch_async(x)
    pfinish()

