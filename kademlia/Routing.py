import time

from collections import OrderedDict

class KBucket():
    def __init__(self, lower_range, upper_range, ksize):
        self.ksize = ksize
        self.nodes = OrderedDict()
        self.range = (lower_range, upper_range)

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
            self.nodes[node.node_id] = node
            return True
        return False
        # El node no cabe en el bucket que hacer ???
        # reemplacement list???

    def remove_node(self, node):
        if node in self:
            del self.nodes[node.node_id]

    def split(self):
        midpoint = (self.range[0] + self.range[1]) / 2
        one = KBucket(self.range[0], midpoint, self.ksize)
        two = KBucket(midpoint + 1, self.range[1], self.ksize)
        # reemplacement list???
        for node in nodes:
            bucket = one if node.id <= midpoint else two
            bucket.add_node(node)

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, node):
        return self.nodes.__contains__(node.node_id)


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
        for idx, bucket in self.buckets:
            if node.node_id < bucket.range[1]:
                return idx
        return None

    def split_bucket(self, index):
        one, two = self.buckets[index].split()
        self.buckets[index] = one
        self.buckets.insert(index + 1, two)

    def add_contact(self, node):
        idx = self.get_bucket_for(node)
        bucket = self.buckets[idx]

        # this will succeed unless the bucket is full
        if bucket.add_node(node):
            return

        # ... magia negra!!!

    def remove_contact(self, node):
        index = self.get_bucket_for(node)
        self.buckets[index].remove_node(node)

if __name__ == '__main__':
    d = OrderedDict()
    d['a'] = 'A'
    d['b'] = 'B'
    d['c'] = 'C'
    l = [1, 2, 3, 4, 5]
    for i in enumerate(l):
        print(i)
