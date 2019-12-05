import logging
import asyncio
import sys
import pickle

from network import Server

if len(sys.argv) != 4:
    print("Usage: python get.py <bootstrap node> <bootstrap port> <key>")
    sys.exit(1)

# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M',
                    filemode='w')

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# add the handler to the root logger
logging.getLogger(__name__).addHandler(console)

loop = asyncio.get_event_loop()
loop.set_debug(True)

server = Server()
loop.run_until_complete(server.listen(8469))
bootstrap_node = (sys.argv[1], int(sys.argv[2]))
loop.run_until_complete(server.bootstrap([bootstrap_node]))
result = loop.run_until_complete(server.get(sys.argv[3]))
server.stop()
loop.close()

print("Get result:", pickle.loads(result))
