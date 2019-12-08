import sys
import pickle
import asyncio

from utils import digest
from storage import AwesomeStorage

from network import Server
from utils import parse, ops, prec, infix_postfix

async def operation(response, server):
    if response[0] == 'add':
        return await add(response[1], response[2], server)
    elif response[0] == 'add-tags':
        return await add_tags(response[1], response[2], server)
    elif response[0] == 'delete':
        return await delete(response[1], server)
    elif response[0] == 'delete-tags':
        return await delete_tags(response[1], response[2], server)
    elif response[0] == 'list':
        return await list(response[1], server, prt=True)
    elif response[0] == 'get':
        return await get(response[1], server)

async def add(file_list, tag_list, server):
    lfiles = []
    for f in file_list:
        with open(f, 'rb') as lf:
            tmp = lf.read()
        lfiles.append(tmp)

    for t in tag_list:
        for i in range(len(file_list)):
            await server.set(t, file_list[i], lfiles[i])

async def add_tags(tag_query, tag_list, server):
    response = await get_fileIds(tag_query, server)
    for t in tag_list:
        for f in response:
            try:
                r = pickle.loads(await server.get(t, True))
                if f not in r:
                    # print('not match')
                    await server.set(t, None ,f, False)

            except:
                l = (await server.get(f, False))
                # print(l)
                # input()
                f1, tags, name = pickle.loads(l)
                await server.set(t, name ,pickle.loads(f1), True)

#get file ids
"""

async def list(tag_query, server, prt=False):
    files = []
    tokens = infix_postfix(tag_query)
    if len(tokens) == 1:
        try:
            print('here')
            file_ids = pickle.loads(await server.get(tokens[0]))

            for f in file_ids:
                files.append(pickle.loads(await server.get(f, False)))
            print(files)
            # for i in files:
            #     w = open('downloads/' + str(digest(i)), "wb")
            #     w.write(i)
            #     w.close()

            for i in files:
                print(pickle.loads(i[0]))
                print(pickle.loads(i[1]))

            if prt:
                print("Get result:", end=" ")
                print(files)
            return files

        except:
            return files

    else:
        stack = []
        for item in tokens:
            if item in ops:
                if item == 'not':
                    # not tag
                    # v = not stack.pop()
                    # stack.append(v)
                    pass
                else:
                    op1 = stack.pop()
                    op2 = stack.pop()

                    f1 = set()
                    f2 = set()

                    try:
                        if op1 in tokens:
                            f1 = pickle.loads(await server.get(op1))
                    except:
                        pass
                    try:
                        if op2 in tokens:
                            f2 = pickle.loads(await server.get(op2))
                    except:
                        pass

                    if item == 'and':
                        # stack.append(op1 and op2)
                        stack.append(f1.intersection(f2))
                    else:
                        # stack.append(op1 or op2)
                        stack.append(f1.union(f2))
            else:
                stack.append(item)
        result = stack.pop()
        files = []
        for f in result:
            files.append(pickle.loads(await server.get(f, False)))
        if prt:
            print("Get result:", end=" ")
            print(files)
        return files
"""

async def get_fileIds(tag_query, server, prt=False):
    files = []
    tokens = infix_postfix(tag_query)
    if len(tokens) == 1:
        try:
            file_ids = pickle.loads(await server.get(tokens[0], True))

            if prt:
                print("Get result:", end=" ")
                print(file_ids)
            return file_ids

        except:
            return files

    else:
        stack = []
        for item in tokens:
            if item in ops:
                if item == 'not':
                    pass
                else:
                    op1 = stack.pop()
                    op2 = stack.pop()

                    if item == 'and':
                        # stack.append(op1 and op2)
                        if not op1 or not op2:
                            stack.append(set())
                        stack.append(op1.intersection(op2))
                    else:
                        # stack.append(op1 or op2)
                        if not op1 and op2:
                            stack.append(op2)
                        elif op1 and not op2:
                            stack.append(op1)
                        elif not op1 and not op2:
                            stack.append(set())
                        else:
                            stack.append(op1.union(op2))
            else:
                load = await server.get(item, True)
                if load:
                    stack.append(pickle.loads(load))
                else:
                    stack.append(set())

        result = stack.pop()
        # files = []
        # for f in result:
        #     files.append(pickle.loads(await server.get(f, False)))
        if prt:
            print("Get result:", end=" ")
            print(result)
        return result

#todo list de verdad
async def list(tag_query, server, prt = False):
    to_return = []
    fids = await get_fileIds(tag_query, server, False)
    if len(fids):
        for f in fids:
            l = (await server.get(f, False))
            if not l:
                print('No results')
                return
            f, tags, name = pickle.loads(l)

            to_return.append((name, pickle.loads(f)))
            result = 'file: ' + name + ' tags:'
            for t in pickle.loads(tags):
                result += ' ' + t

            print(result)
    else:
        print('No results')

    return to_return

async def get(tag_query, server):
    info = await list(tag_query, server)
    # print(info)
    for name, file in info:
        w = open('downloads/' + name, "wb")
        w.write(file)
        w.close()

async def delete(tag_query, server):
    files = await get_fileIds(tag_query, server, False)
    for f in files:
        l = (await server.get(f, False))
        # print(l)
        # input()
        if not l:
            continue
        f1, tags, name = pickle.loads(l)
        tag_list = pickle.loads(tags)
        for t in tag_list:
            await server.delete_tag(t, f)

        await server.delete(f, False)

async def delete_tags(tag_query, tag_list, server):
    files = await get_fileIds(tag_query, server, False)
    for t in tag_list:
        for f in files:
            await server.delete_tag(t, f)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python3 client.py <client ip> <client port > <bootstrap routing_node> <bootstrap routing_port>")
        sys.exit(1)

    loop = asyncio.get_event_loop()
    server = Server(storage=AwesomeStorage())
    loop.run_until_complete(server.listen(int(sys.argv[2]), sys.argv[1]))
    bootstrap_node = (sys.argv[3], int(sys.argv[4]))
    loop.run_until_complete(server.bootstrap([bootstrap_node]))

    inst = ['echo', '', '>', '/Test/output']

    while True:
        try:
            print(' >>', end=' ')
            inp = input()
            if not len(inp):
                continue
            loop.run_until_complete(operation(parse(inp), server))

        except Exception as e:
            if e == KeyboardInterrupt:
                server.close()
                loop.close()
                break
            print(e)