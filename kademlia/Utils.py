from operator import itemgetter

def get_long_id(bites):
    bits = [bin(int(bite))[2:].rjust(8, '0') for bite in bites]
    return "".join(bits)

def shared_prefix(args):
    i = 0
    while(i < min(map(len, args))):
        if len(set(map(itemgetter(i), args))) != 1:
            break
        i+=1
    return args[0][:i]