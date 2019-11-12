import heapq

class Node():
    def __init__(self, node_id, ip=None, port=None):
        """
        :param node_id: (int) A value between 0 and 2^160
        :param ip: (string) Optional IP address where this Node lives
        :param port: (int) Optional port for this Node (set when IP is set)
        """
        self.ip = ip
        self.port = port
        self.id = node_id

    def __iter__(self):
        return iter([self.id, self.ip, self.port])

    def __repr__(self):
        return repr([self.id, self.ip, self.port])

    def __str__(self):
        return '%s:%s' %  (self.ip, str(self.port))

    def distance_to(self, node):
        return self.id ^ node.id

class NodeHeap():
    """
    A heap of nodes ordered by distance to a given node.
    """
    def __init__(self, node, maxsize):
        """
        :param node: (Node) The node to measure all distances from.
        :param maxsize: (int) The maximum size that this heap can grow to.
        """
        self.heap = []
        self.node = node
        self.maxsize = maxsize

    def push(self, nodes):
        """
        :param nodes: This can be a single item or a C{list}.
        :return: Push nodes onto heap.
        """
        if not isinstance(nodes, list):
            nodes = [nodes]

        for node in nodes:
            if node not in self:
                distance = self.node.distance_to(node)
                heapq.heappush(self.heap, (distance, node))

    def remove(self, nodes):
        """
        :param nodes: This can be a single item or a C{list}.
        :return: Remove nodes of heap.
        """
        l = set(nodes)
        nheap = []
        for d, node in self.heap:
            if node.id not in l:
                heapq.heappush(nheap, (d, node))
        self.heap = nheap

    def get_node(self, node_id):
        """
        :param node_id: (int)
        :return: The Node with id = node_id if exists
        """
        for _, node in self.heap:
            if node.id == node_id:
                return node
        return None

    def __len__(self):
        return min(len(self.heap), self.maxsize)

    def __iter__(self):
        return heapq.nsmallest(self.maxsize, self.heap)

    def __contains__(self, node):
        for _, other in self.heap:
            if node.id == other.id:
                return True
        return False
