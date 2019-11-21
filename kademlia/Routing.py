import time
import heapq
import Utils
import asyncio
import operator

from itertools import chain
from collections import OrderedDict

class KBucket():
    def __init__(self, lower_range, upper_range, ksize):
        self.ksize = ksize
        self.touch_last_updated()
        self.nodes = OrderedDict()
        self.replacement_nodes = OrderedDict()
        self.range = (lower_range, upper_range)

    def touch_last_updated(self):
        self.last_updated = time.monotonic()

    def get_nodes(self):
        return list(self.nodes.values())

    def add_node(self, node):
        """
        Add a Node to the KBucket
        :param node: Node
        :return: Return True if successful, False if the bucket is full
        """
        if node in self:
            self.nodes.move_to_end(node.id)
            return True
        elif len(self) < self.ksize:
            self.nodes[node.id] = node
            return True
        else:
            if node.id in self.replacement_nodes:
                self.replacement_nodes.move_to_end(node.id)
            return False
        return True

    def remove_node(self, node):
        if node.id in self.replacement_nodes:
            del self.replacement_nodes[node.id]

        if node in self:
            del self.nodes[node.id]

            if self.replacement_nodes:
                newnode_id, newnode = self.replacement_nodes.popitem()
                self.nodes[newnode_id] = newnode

    def split(self):
        midpoint = (self.range[0] + self.range[1]) / 2
        one = KBucket(self.range[0], midpoint, self.ksize)
        two = KBucket(midpoint + 1, self.range[1], self.ksize)
        nodes = list(chain(self.nodes.values(), self.replacement_nodes.values()))
        for node in nodes:
            bucket = one if node.id <= midpoint else two
            bucket.add_node(node)
        return (one, two)

    def head(self):
        return list(self.nodes.values())[0]

    def depth(self):
        v = self.nodes.values()
        sprefix = shared_prefix([long_id(node.id) for node in v])
        return len(sprefix)

    def in_range(self, node):
        return self.range[0] <= node.id <= self.range[1]

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, node):
        return self.nodes.__contains__(node.id)

class TableTraverser():
    def __init__(self, rtable, startNode):
        idx = rtable.get_bucket(startNode)
        rtable.buckets[idx].touch_last_update()
        self.current_nodes = rtable.buckets[idx].get_nodes()
        self.left_buckets = rtable.buckets[:idx]
        self.right_buckets = rtable.buckets[(idx+1):]
        self.left = True

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_nodes:
            return self.current_nodes.pop()

        if self.left and self.left_buckets:
            self.current_nodes = self.left_buckets.pop().get_nodes()
            self.left = False
            return next(self)

        if self.right_buckets:
            self.current_nodes = self.right_buckets.pop(0).get_nodes()
            self.left = True
            return next(self)

        raise StopIteration

class RoutingTable():
    def __init__(self, protocol, ksize, node):
        self.node = node
        self.protocol = protocol
        self.ksize = ksize
        self.buckets = [KBucket(0, 2 ** 160, self.ksize)]

    def get_bucket(self, node):
        """
        :param node: Node
        :return: Get the index of the bucket that the given node would fall into.
        """
        for idx, bucket in enumerate(self.buckets):
            if node.id < bucket.range[1]:
                return idx
        return None

    def split_bucket(self, index):
        one, two = self.buckets[index].split()
        self.buckets[index] = one
        self.buckets.insert(index + 1, two)

    def add_contact(self, node):
        idx = self.get_bucket(node)
        bucket = self.buckets[idx]

        # this will succeed unless the bucket is full
        if bucket.add_node(node):
            return

        if bucket.in_range(node) or bucket.depth() % 5 != 0:
            self.split(index)
            self.add_contact(node)
        else:
            asyncio.ensure_future(self.protocol.call_ping(bucket.head()))

    def remove_contact(self, node):
        index = self.get_bucket_for(node)
        self.buckets[index].remove_node(node)

    def find_neighbors(self, node, k=None, exclude=None):
        k = k or self.ksize
        nodes = []
        for neighbor in TableTraverser(self, node):
            notexcluded = exclude is None or not neighbor.same_home_as(node)
            if neighbor.id != node.id and notexcluded:
                heapq.heappush(nodes, (node.distance_to(neighbor), neighbor))
            if len(nodes) == k:
                break
        return list(map(operator.itemgetter(1), heapq.nsmallest(k, nodes)))