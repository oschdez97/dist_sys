import sys
import pickle
import asyncio

from utils import digest
from storage import AwsomeStorage

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

async def add(file_list, tag_list, server):
    for t in tag_list:
        for f in file_list:
            await server.set(t, f)

async def add_tags(tag_query, tag_list, server):
    response = await list(tag_query, server)
    for t in tag_list:
        for f in response:
            try:
                r = pickle.loads(await server.get(t))
                if f not in r:
                    await server.set(t, f)
            except:
                await server.set(t, f)

async def list(tag_query, server, prt=False):
    """
    :param tag_query:
    :param server:
    :param prt:
    :return: List FileIds
    """
    if len(tag_query) == 1:
        file_ids = pickle.loads(await server.get(tag_query[0]))
        files = []
        for f in file_ids:
            files.append(pickle.loads(await server.get(f, False)))

        if prt:
            print("Get result:", end=" ")
            print(files)
        return files

    else:
        tokens = infix_postfix(tag_query)
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
                    # hacer try catch porque cuando se hace una query que no cumple nadie
                    # da None y a eso no se le puede hacer pickle... mantener la consistencia
                    # de la funcion
                    f1 = pickle.loads(await server.get(op1))
                    f2 = pickle.loads(await server.get(op2))
                    if item == 'and':
                        # stack.append(op1 and op2)
                        stack.append(f1.intersection(f2))
                    else:
                        # stack.append(op1 or op2)
                        stack.append(f1.union(f2))
            else:
                stack.append(item)
        result = stack.pop()
        if prt:
            files = [item[1] for item in result]
            print("Get result:", end=" ")
            print(files)
        return result

async def delete(tag_query, server):
    files = await list(tag_query, server)
    for f in files:
        await server.delete(f)

async def delete_tags(tag_query, tag_list, server):
    files = await list(tag_query, server)
    for t in tag_list:
        for f in files:
            await server.delete_tag(t, f)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python3 client.py <client ip> <client port > <bootstrap routing_node> <bootstrap routing_port>")
        sys.exit(1)

    loop = asyncio.get_event_loop()
    server = Server(storage=AwsomeStorage())
    loop.run_until_complete(server.listen(int(sys.argv[2]), sys.argv[1]))
    bootstrap_node = (sys.argv[3], int(sys.argv[4]))
    loop.run_until_complete(server.bootstrap([bootstrap_node]))

    while True:
        try:
            print(' >>', end=' ')
            loop.run_until_complete(operation(parse(input()), server))
        except Exception:
            break

    server.stop()
    loop.close()