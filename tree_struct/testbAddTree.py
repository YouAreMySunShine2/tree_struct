import unittest
from tree_struct.spiders import bAddTree


class BtreeTestCase(unittest.TestCase):
    test_list = []
    leaf = 4
    _inter_node_num = 4

    def setUp(self) -> None:
        for i in range(1, 30):
            key = i
            value = i
            self.test_list.append(bAddTree.KeyValue(key, value))

    def tearDown(self) -> None:
        print()

    def test_insert_node(self):
        bp_tree = bAddTree.Btree(4, 4)
        for kv in self.test_list:
            bp_tree.insert(kv)

    def test_leaf_node(self):
        leaf_node = bAddTree.BtreeLeaf(self.leaf)
        leaf_node._is_full()
        leaf_node._is_leaf()

    def test_b_tree_split_leaf(self):
        bp_tree = bAddTree.Btree(self.leaf, self._inter_node_num)
        leaf_node = bAddTree.BtreeLeaf(self.leaf)
        for i in range(5):
            leaf_node.v_list.append(self.test_list[i])
        _treeInterNode = bp_tree.split_leaf(leaf_node)
        print(_treeInterNode)

    def test_split_node(self):
        bp_tree = bAddTree.Btree(self.leaf, self._inter_node_num)
        _treeInterNode = self.split_node(bp_tree)
        print(_treeInterNode)

    def split_node(self, bp_tree):
        _inter_node = bAddTree.BtreeInterNode(self._inter_node_num)
        leaf_node1 = bAddTree.BtreeLeaf(self.leaf)
        leaf_node2 = bAddTree.BtreeLeaf(self.leaf)
        leaf_node3 = bAddTree.BtreeLeaf(self.leaf)
        leaf_node4 = bAddTree.BtreeLeaf(self.leaf)
        leaf_node5 = bAddTree.BtreeLeaf(self.leaf)
        leaf_nodes = [leaf_node1, leaf_node2, leaf_node3, leaf_node4, leaf_node5]
        index = -1
        for i in range(20):
            if i % 4 == 0:
                index += 1
            leaf_nodes[index].v_list.append(self.test_list[i])
        _inter_node.tree_leaf_mid_key = [4, 8, 12, 16, 20]
        _inter_node.tree_leaf_list = [leaf_node1, leaf_node2, leaf_node3, leaf_node4, leaf_node5]
        _treeInterNode = bp_tree.split_node(_inter_node)
        return _treeInterNode

    def test_bisect_right_map(self):
        key_value = bAddTree.KeyValue(6, 7)
        print(bAddTree.bisect_right_map(self.test_list, key_value))

    def test_traversal(self):
        bp_tree = bAddTree.Btree(self.leaf, self._inter_node_num)
        for i in range(20):
            bp_tree.insert(self.test_list[i])
        self.split_node(bp_tree)
        result = bp_tree.traversal()
        print(result)

    @staticmethod
    def test_array_split():
        a_array = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        b_array = a_array.pop(a_array.index(4))
        print("a_array")
        print(a_array)
        print("b_array")
        print(b_array)
