#!/usr/bin/env python
from bisect import bisect_right
from collections import deque
import math


class InitError(Exception):
    pass


class ParaError(Exception):
    pass


class KeyValue(object):
    __slots__ = ('key', 'value')

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return str((self.key, self.value))

    def __cmp__(self, key):
        if self.key > key:
            return 1
        elif self.key == key:
            return 0
        else:
            return -1


"""B+树，内部节点/索引节点"""


class BtreeInterNode(object):
    def __init__(self, _inter_node_num):
        if not isinstance(_inter_node_num, int):
            raise InitError('M must be int')
        if _inter_node_num <= 3:
            raise InitError('M must be greater then 3')
        else:
            self.__inter_node_num = _inter_node_num
            """子节点"""
            self.tree_leaf_list = []
            """key"""
            self.tree_leaf_mid_key = []
            """下个内部节点指向"""
            self.par = None

    @classmethod
    def is_leaf(cls):
        return False

    def is_full(self):
        return len(self.tree_leaf_mid_key) > self.__inter_node_num

    def is_empty(self):
        return len(self.tree_leaf_mid_key) > 0

    def is_rich(self):
        return len(self.tree_leaf_mid_key) >= math.ceil(self.__inter_node_num - 1) / 2 - 1

    @property
    def get_inter_node_num(self):
        return self.__inter_node_num


""" 叶子节点 """


class BtreeLeaf(object):
    def __init__(self, _leaf_num):
        """key:value"""
        self.v_list = []
        """相连下一叶子节点"""
        self.bro = None
        """内部节点引用"""
        self.par = None
        if not isinstance(_leaf_num, int):
            raise InitError('leaf num must be int')
        else:
            self.___leaf_num = _leaf_num

    @classmethod
    def is_leaf(cls):
        return True

    def is_full(self):
        return len(self.v_list) > self.___leaf_num

    def is_empty(self):
        return len(self.v_list) > 0

    def is_rich(self):
        return len(self.v_list) >= math.ceil((self.___leaf_num - 1) / 2) - 1

    @property
    def get_leaf_num(self):
        return self.___leaf_num


"""数据插入位置"""


def bisect_right_map(first_map, second_map, low=0, high=None):
    if low < 0:
        raise ValueError('low must be non-negative')
    if high is None:
        high = len(first_map)
    while low < high:
        mid = (low + high) // 2
        if second_map.key < first_map[mid].key:
            high = mid
        else:
            low = mid + 1
    return low


def bisect_left_map(first_map, second_map, low=0, high=None):
    if low < 0:
        raise ValueError('low must be non-negative')
    if high is None:
        high = len(first_map)
    while low < high:
        mid = (low + high) // 2
        if first_map[mid].key < second_map.key:
            low = mid + 1
        else:
            high = mid
    return low


class Btree(object):
    def __init__(self, _inter_node_num, _leaf_num):
        if _leaf_num > _inter_node_num:
            raise InitError('leaf num must be less or equal then inter node num')
        else:
            self.__inter_node_num = _inter_node_num
            self.__leaf_num = _leaf_num
            self.__root = BtreeLeaf(_leaf_num)
            self.__leaf = self.__root

    @property
    def get_inter_node_num(self):
        return self.__inter_node_num

    @property
    def get_leaf_num(self):
        return self.__leaf_num

    def insert_node(self, _new_node, key_value):
        if not _new_node.is_leaf():
            if _new_node.is_full():
                self.insert_node(self.split_node(_new_node), key_value)
            else:
                p = bisect_right(_new_node.tree_leaf_mid_key, key_value.key)
                self.insert_node(_new_node.tree_leaf_list[p], key_value)
        else:
            p = bisect_right_map(_new_node.v_list, key_value)
            _new_node.v_list.insert(p, key_value)
            if _new_node.is_full():
                self.split_leaf(_new_node)
            else:
                return

    """
    索引节点分裂
    """
    def split_node(self, _inter_node):
        mid = (self.__inter_node_num + 1) // 2
        _new_inter_node = BtreeInterNode(self.__inter_node_num)
        if _inter_node.par is None:
            _new_root = BtreeInterNode(self.__inter_node_num)
            _new_root.tree_leaf_mid_key = [_inter_node.tree_leaf_mid_key.pop(mid)]
            _new_root.tree_leaf_list = [_inter_node, _new_inter_node]
            _inter_node.par = _new_inter_node.par = _new_root
            self.__root = _new_root
        else:
            index = _inter_node.par.tree_leaf_list.index(_inter_node)
            _inter_node.par.tree_leaf_mid_key.insert(index, _inter_node.tree_leaf_mid_key.pop(mid))
            _inter_node.par.tree_leaf_list.insert(index + 1, _new_inter_node)
        _new_inter_node.tree_leaf_list.append(_inter_node.tree_leaf_list.pop(mid + 1))
        while len(_inter_node.tree_leaf_mid_key) > mid:
            _new_inter_node.tree_leaf_mid_key.append(_inter_node.tree_leaf_mid_key.pop(mid))
            _new_inter_node.tree_leaf_list.append(_inter_node.tree_leaf_list.pop(mid + 1))
        _new_inter_node.par = _inter_node.par
        for _tree_leaf in _new_inter_node.tree_leaf_list:
            _tree_leaf.par = _new_inter_node
        return _inter_node.par

    """
    叶子节点分裂
    """
    def split_leaf(self, _new_node):
        mid = (self.__leaf_num + 1) // 2
        _new_leaf = BtreeLeaf(self.__leaf_num)
        while len(_new_node.v_list) > mid:
            _new_leaf.v_list.append(_new_node.v_list.pop(mid))
        if _new_node.par is None:
            _new_root = BtreeInterNode(self.__inter_node_num)
            _new_root.tree_leaf_mid_key.append(_new_leaf.v_list[0].key)
            _new_root.tree_leaf_list = [_new_node, _new_leaf]
            _new_node.par = _new_leaf.par = _new_root
            self.__root = _new_root
        else:
            index = _new_node.par.tree_leaf_list.index(_new_node)
            _new_node.par.tree_leaf_mid_key.insert(index, _new_leaf.v_list[0].key)
            _new_node.par.tree_leaf_list.insert(index + 1, _new_leaf)
            _new_leaf.par = _new_node.par
        _new_node.bro = _new_leaf
        return _new_node.par

    def insert(self, key_value):
        node = self.__root
        self.insert_node(node, key_value)

    """
    搜索key_value所在节点和index
    """
    def search_key(self, _node, key_value):
        if _node.is_leaf():
            _index = bisect_left_map(_node.v_list, key_value)
            return _index, _node
        else:
            _index = bisect_right(_node.tree_leaf_mid_key, key_value.key)
            return self.search_key(_node.tree_leaf_list[_index], key_value)

    def search(self, mi=None, ma=None):
        result = []
        node = self.__root
        leaf = self.__leaf
        if mi is None and ma is None:
            raise ParaError('you need to setup searching range')
        elif mi is not None and ma is not None and mi.key > ma.key:
            raise ParaError('upper bound must be greater or equal than lower bound')
        if mi is None:
            return self.between_value(leaf, ma)
        elif ma is None:
            index, leaf = self.search_key(node, mi)
            result.extend(leaf.v_list[index:])
            while True:
                if leaf.bro is None:
                    return result
                else:
                    leaf = leaf.bro
                    result.extend(leaf.v_list)
        else:
            if mi == ma:
                index, leaf = self.search_key(node, mi)
                try:
                    if leaf.v_list[index] == mi:
                        result.append(leaf.v_list[index])
                        return result
                    else:
                        return result
                except IndexError:
                    return result
            else:
                return self.search_mi_and_ma(ma, mi, node)

    @staticmethod
    def between_value(leaf, ma):
        result = []
        while True:
            for kv in leaf.v_list:
                if kv.key <= ma.key:
                    result.append(kv)
                else:
                    return result
            if leaf.bro is None:
                return result
            else:
                leaf = leaf.bro

    def search_mi_and_ma(self, ma, mi, node):
        result = []
        index1, leaf1 = self.search_key(node, mi)
        index2, leaf2 = self.search_key(node, ma)
        if leaf1 is leaf2:
            if index1 == index2:
                return result
            else:
                result.extend(leaf1.v_list[index1:index2])
                return result
        else:
            result.extend(leaf1.v_list[index1:])
            leaf = leaf1
            while True:
                if leaf.bro == leaf2:
                    result.extend(leaf2.v_list[:index2 + 1])
                    return result
                else:
                    result.extend(leaf.bro.v_list)
                    leaf = leaf.bro

    def traversal(self):
        result = []
        leaf = self.__leaf
        while True:
            result.extend(leaf.v_list)
            if leaf.bro is None:
                return result
            else:
                leaf = leaf.bro

    def show(self):
        print('this b+tree is:\n')
        q = deque()
        h = 0
        q.append([self.__root, h])
        while True:
            try:
                w, hei = q.popleft()
            except IndexError:
                return
            else:
                if not w.is_leaf():
                    print(w.tree_leaf_mid_key, 'the height is', hei)
                    if hei == h:
                        h += 1
                    q.extend([[i, h] for i in w.tree_leaf_list])
                else:
                    print([v.key for v in w.v_list], 'the leaf is,', hei)

    def del_node(self, node, kv):
        if not node.is_leaf():
            index = bisect_right(node.tree_leaf_mid_key, kv.key)
            self.del_node(node.tree_leaf_list[index], kv)
        else:
            p = bisect_left_map(node.v_list, kv)
            try:
                pp = node.v_list[p]
            except IndexError:
                return -1
            if pp != kv:
                return -1
            else:
                node.v_list.remove(kv)
                if node.is_rich():
                    return 0
                else:
                    self.arrange_node(node, kv)

    """
    删除后整理节点
    """

    def arrange_node(self, node, kv):
        if node.par is None:
            self.__root = node.par
            return self.__root
        else:
            index = bisect_right(node.par.tree_leaf_mid_key, kv.key)
            if node.par.tree_leaf_list[index - 1].is_rich():
                print("兄弟节点富裕，借一个给自己")
                self.tran_left_to_right(node.par, index - 1)
            else:
                print("兄弟节点不富裕，合并成一家")
                self.tran_right_to_left(node.par, index - 1, kv)

    """
    向兄弟借节点
    """

    @staticmethod
    def tran_left_to_right(node, index):
        if not node.tree_leaf_list[index].is_leaf():
            _inter_node = node.tree_leaf_list[index].tree_leaf_list.pop()
            node.tree_leaf_list[index + 1].tree_leaf_list.insert(0, _inter_node)
            _inter_node.par = node.tree_leaf_list[index + 1]
            node.tree_leaf_list[index + 1].tree_leaf_mid_key.insert(0, node.tree_leaf_mid_key[index])
            node.tree_leaf_mid_key[index] = node.tree_leaf_list[index].tree_leaf_mid_key.pop()
        else:
            node.tree_leaf_list[index + 1].v_list.insert(0, node.tree_leaf_list[index].v_list.pop())
            node.tree_leaf_mid_key[index] = node.tree_leaf_list[index + 1].v_list[0].key

    """
    和兄弟合家
    """

    def tran_right_to_left(self, node, index, kv):
        if not node.tree_leaf_list[index].is_leaf():
            node.tree_leaf_list[index].tree_leaf_list.append(node.tree_leaf_list[index + 1].tree_leaf_list[:])
            for tree_node in node.tree_leaf_list[index + 1].tree_leaf_list:
                tree_node.par = node.tree_leaf_list[index]
            node.tree_leaf_list[index].tree_leaf_mid_key.append(node.tree_leaf_mid_key[index])
            node.tree_leaf_mid_key[index] = node.tree_leaf_list[index + 1].tree_leaf_mid_key[0]
            node.tree_leaf_list[index + 1].tree_leaf_list.remove(node.tree_leaf_list[index + 1].tree_leaf_list[:])
            node.tree_leaf_list[index + 1].tree_leaf_mid_key.remove(node.tree_leaf_list[index + 1].tree_leaf_mid_key[:])
        else:
            node.tree_leaf_list[index].bro = node.tree_leaf_list[index + 1].bro
            for _leaf_node in node.tree_leaf_list[index + 1].v_list:
                node.tree_leaf_list[index].v_list.append(_leaf_node)
            node.tree_leaf_list.remove(node.tree_leaf_list[index + 1])
            del node.tree_leaf_list[index + 1]
            node.tree_leaf_mid_key.remove(node.tree_leaf_mid_key[index])
        if node.par is None:
            self.__root = node.par
            return self.__root
        elif node.par.is_rich():
            return 0
        else:
            self.arrange_node(node.par, kv)

    def delete(self, key_value):
        self.del_node(self.__root, key_value)


if __name__ == '__main__':
    bp_tree = Btree(4, 4)
