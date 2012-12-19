import time
import sys

stack = list()
messages = list()
 
def push(cnt=1):
    for _ in range(cnt):
        stack.append(time.time())

def pop(cnt=1):
    ret = None
    for _ in range(cnt):
        ret = stack.pop()
    return ret

def replace():
    pop()
    push()

def getTime(back = 0):
    slen = len(stack)
    if back >= slen or back == -1:
        back = slen - 1
    return stack[slen - back - 1]

def msg(message, back = 0):
    timediff= time.time() - getTime(back)
    messages.append(message.format(time=timediff))
    
def printAll():
    for message in messages:
        sys.stderr.write(message + "\n")
