"""
General catchall for functions that don't make sense as methods.
"""
import hashlib
import operator
import asyncio

ops = ['or', 'and', 'not']
prec = { 'and': 1, 'or': 1, 'not': 2, '(': 0, ')': 0 }

async def gather_dict(dic):
    cors = list(dic.values())
    results = await asyncio.gather(*cors)
    return dict(zip(dic.keys(), results))


def digest(string):
    if not isinstance(string, bytes):
        string = str(string).encode('utf8')
    return hashlib.sha1(string).digest()


def shared_prefix(args):
    """
    Find the shared prefix between the strings.

    For instance:

        sharedPrefix(['blahblah', 'blahwhat'])

    returns 'blah'.
    """
    i = 0
    while i < min(map(len, args)):
        if len(set(map(operator.itemgetter(i), args))) != 1:
            break
        i += 1
    return args[0][:i]


def bytes_to_bit_string(bites):
    bits = [bin(bite)[2:].rjust(8, '0') for bite in bites]
    return "".join(bits)


def split(args):
    l1 = args.replace('(', '( ')
    l2 = l1.replace(')', ' )')
    return l2.split()

def parse(args):
    # syntax <add> <-f> <file-list> <-t> <tag-list>
    inst = split(args)
    if inst[0] == 'add':
        if inst.__contains__('-f') and inst.__contains__('-t'):
            try:
                idx = inst.index('-t')
                files = inst[2:idx]
                tags = inst[(idx+1):]
                if not len(files) or not len(tags):
                    raise Exception('syntax error: <file-list> and <tag-list> must have files and tags to store')
            except:
                raise Exception('syntax error: <add> <-f> <file-list> <-t> <tag-list>')
            return inst[0], files, tags
        else:
            raise Exception('syntax error: <add> <-f> <file-list> <-t> <tag-list>')
    # syntax <delete> <-q> <tag-query>
    elif inst[0] == 'delete':
        if inst.__contains__('-q'):
            try:
                idx = inst.index('-q')
                tags = inst[(idx+1):]
                if not len(tags):
                    raise Exception("syntax error: tags can't be empty")
            except:
                raise Exception('syntax error: <delete> <-q> <tag-query>')
            return inst[0] , tags
        else:
            raise Exception('syntax error: <delete> <-q> <tag-query>')
    # syntax <list> <-q> <tag-query>
    elif inst[0] == 'list':
        if inst.__contains__('-q'):
            try:
                idx = inst.index('-q')
                tags = inst[(idx+1):]
                if not len(tags):
                    raise Exception("syntax error: tags can't be empty")
            except:
                raise Exception('syntax error: <list> <-q> <tag-query>')
            return inst[0] , tags
        else:
            raise Exception('syntax error: <list> <-q> <tag-query>')
    # syntax <add-tags> <-q> <tag-query> <-t> <tag-list>
    elif inst[0] == 'add-tags':
        if inst.__contains__('-q') and inst.__contains__('-t'):
            try:
                idx = inst.index('-t')
                query = inst[2:idx]
                tags = inst[(idx+1):]
                if not len(query) or not len(tags):
                    raise Exception('syntax error: <tag-query> and <tag-list> must have files and tags to store')
            except:
                raise Exception('syntax error: <add-tags> <-q> <tag-query> <-t> <tag-list>')
            return inst[0], query, tags
        else:
            raise Exception('syntax error: <add-tags> <-q> <tag-query> <-t> <tag-list>')
    # syntax <delete-tags> <-q> <tag-query> <-t> <tag-list>
    elif inst[0] == 'delete-tags':
        if inst.__contains__('-q') and inst.__contains__('-t'):
            try:
                idx = inst.index('-t')
                query = inst[2:idx]
                tags = inst[(idx+1):]
                if not len(query) or not len(tags):
                    raise Exception('syntax error: <tag-query> and <tag-list> must have files and tags to store')
            except:
                raise Exception('syntax error: <delete-tags> <-q> <tag-query> <-t> <tag-list>')
            return inst[0], query, tags
        else:
            raise Exception('syntax error: <delete-tags> <-q> <tag-query> <-t> <tag-list>')
    elif inst[0] == 'get':
        if inst.__contains__('-q'):
            try:
                idx = inst.index('-q')
                tags = inst[(idx + 1):]
                if not len(tags):
                    raise Exception("syntax error: tags can't be empty")
            except:
                raise Exception('syntax error: <get> <-q> <tag-query>')
            return inst[0], tags
        else:
            raise Exception('syntax error: <get> <-q> <tag-query>')
    else:
        raise Exception('syntax error: unknown command %s', inst[0])

def infix_postfix(tokens):
    stack = []
    output = []
    for item in tokens:
        if item in ops:
            while stack and prec[stack[-1]] >= prec[item]:
                output.append(stack.pop())
            stack.append(item)
        elif item == "(":
            stack.append("(")
        elif item == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            stack.pop()
        else:
            output.append(item)
    while stack:
        output.append(stack.pop())
    return output
