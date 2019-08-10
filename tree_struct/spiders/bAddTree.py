#!/usr/bin/env python
from bisect import bisect_right, bisect_left
from collections import deque


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
            """BtreeLeaf"""
            self.tree_leaf_list = []
            """key"""
            self.tree_leaf_mid_key = []
            """下个内部节点指向"""
            self.par = None

    @classmethod
    def is_leaf(cls):
        return False

    def is_full(self):
        return len(self.tree_leaf_list) >= self.__inter_node_num - 1

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

    """索引节点分裂"""

    def split_node(self, _inter_node):
        mid = int((self.__inter_node_num + 1) / 2)
        _new_inter_node = BtreeInterNode(self.__inter_node_num)
        while len(_inter_node.tree_leaf_mid_key) > mid:
            _new_inter_node.tree_leaf_mid_key.append(_inter_node.tree_leaf_mid_key.pop(mid))
            _new_inter_node.tree_leaf_list.append(_inter_node.tree_leaf_list.pop(mid))
        _new_inter_node.par = _inter_node.par
        for _tree_leaf in _new_inter_node.tree_leaf_list:
            _tree_leaf.par = _new_inter_node
        if _inter_node.par is None:
            _new_root = BtreeInterNode(self.__inter_node_num)
            _new_root.tree_leaf_mid_key = [_new_inter_node.tree_leaf_mid_key[0]]
            _new_root.tree_leaf_list = [_inter_node, _new_inter_node]
            _inter_node.par = _new_inter_node.par = _new_root
            self.__root = _new_root
        else:
            index = _inter_node.par.tree_leaf_list.index(_inter_node)
            _inter_node.par.tree_leaf_mid_key.insert(index, _new_inter_node.tree_leaf_mid_key[0])
            _inter_node.par.tree_leaf_list.insert(index + 1, _new_inter_node)
        return _inter_node.par

    """叶子节点分裂"""

    def split_leaf(self, _new_node):
        mid = int((self.__leaf_num + 1) / 2)
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

    def search(self, mi=None, ma=None):
        result = []
        node = self.__root
        leaf = self.__leaf
        if mi is None and ma is None:
            raise ParaError('you need to setup searching range')
        elif mi is not None and ma is not None and mi > ma:
            raise ParaError('upper bound must be greater or equal than lower bound')

        def search_key(n, k):
            if n.is_leaf():
                p = bisect_left(n.vlist, k)
                return (p, n)
            else:
                p = bisect_right(n.ilist, k)
                return search_key(n.clist[p], k)

        if mi is None:
            while True:
                for kv in leaf.v_list:
                    if kv <= ma:
                        result.append(kv)
                    else:
                        return result
                if leaf.bro == None:
                    return result
                else:
                    leaf = leaf.bro
        elif ma is None:
            index, leaf = search_key(node, mi)
            result.extend(leaf.vlist[index:])
            while True:
                if leaf.bro == None:
                    return result
                else:
                    leaf = leaf.bro
                    result.extend(leaf.vlist)
        else:
            if mi == ma:
                i, l = search_key(node, mi)
                try:
                    if l.vlist[i] == mi:
                        result.append(l.vlist[i])
                        return result
                    else:
                        return result
                except IndexError:
                    return result
            else:
                i1, l1 = search_key(node, mi)
                i2, l2 = search_key(node, ma)
                if l1 is l2:
                    if i1 == i2:
                        return result
                    else:
                        result.extend(l1.vlist[i1:i2])
                        return result
                else:
                    result.extend(l1.vlist[i1:])
                    l = l1
                    while True:
                        if l.bro == l2:
                            result.extend(l2.vlist[:i2 + 1])
                            return result
                        else:
                            result.extend(l.bro.vlist)
                            l = l.bro

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
                    print(w.ilist, 'the height is', hei)
                    if hei == h:
                        h += 1
                    q.extend([[i, h] for i in w.clist])
                else:
                    print([v.key for v in w.vlist], 'the leaf is,', hei)

    def delete(self, key_value):
        def merge(n, i):
            if n.clist[i].is_leaf():
                n.clist[i].vlist = n.clist[i].vlist + n.clist[i + 1].vlist
                n.clist[i].bro = n.clist[i + 1].bro
            else:
                n.clist[i].ilist = n.clist[i].ilist + [n.ilist[i]] + n.clist[i + 1].ilist
                n.clist[i].clist = n.clist[i].clist + n.clist[i + 1].clist
            n.clist.remove(n.clist[i + 1])
            n.ilist.remove(n.ilist[i])
            if n.ilist == []:
                n.clist[0].par = None
                self.__root = n.clist[0]
                del n
                return self.__root
            else:
                return n

        def tran_l2r(n, i):
            if not n.clist[i].is_leaf():
                n.clist[i + 1].clist.insert(0, n.clist[i].clist[-1])
                n.clist[i].clist[-1].par = n.clist[i + 1]
                n.clist[i + 1].ilist.insert(0, n.ilist[i])
                n.ilist[i] = n.clist[i].ilist[-1]
                n.clist[i].clist.pop()
                n.clist[i].ilist.pop()
            else:
                n.clist[i + 1].vlist.insert(0, n.clist[i].vlist[-1])
                n.clist[i].vlist.pop()
                n.ilist[i] = n.clist[i + 1].vlist[0].key

        def tran_r2l(n, i):
            if not n.clist[i].is_leaf():
                n.clist[i].clist.append(n.clist[i + 1].clist[0])
                n.clist[i + 1].clist[0].par = n.clist[i]
                n.clist[i].ilist.append(n.ilist[i])
                n.ilist[i] = n.clist[i + 1].ilist[0]
                n.clist[i + 1].clist.remove(n.clist[i + 1].clist[0])
                n.clist[i + 1].ilist.remove(n.clist[i + 1].ilist[0])
            else:
                n.clist[i].vlist.append(n.clist[i + 1].vlist[0])
                n.clist[i + 1].vlist.remove(n.clist[i + 1].vlist[0])
                n.ilist[i] = n.clist[i + 1].vlist[0].key

        def del_node(n, kv):
            if not n.is_leaf():
                p = bisect_right(n.ilist, kv)
                if p == len(n.ilist):
                    if not n.clist[p].isempty():
                        return del_node(n.clist[p], kv)
                    elif not n.clist[p - 1].isempty():
                        tran_l2r(n, p - 1)
                        return del_node(n.clist[p], kv)
                    else:
                        return del_node(merge(n, p), kv)
                else:
                    if not n.clist[p].isempty():
                        return del_node(n.clist[p], kv)
                    elif not n.clist[p + 1].isempty():
                        tran_r2l(n, p)
                        return del_node(n.clist[p], kv)
                    else:
                        return del_node(merge(n, p), kv)
            else:
                p = bisect_left(n.vlist, kv)
                try:
                    pp = n.vlist[p]
                except IndexError:
                    return -1
                else:
                    if pp != kv:
                        return -1
                    else:
                        n.vlist.remove(kv)
                        return 0

        del_node(self.__root, key_value)


def test():
    mini = 2
    maxi = 60
    testlist = []
    for i in range(1, 10):
        key = i
        value = i
        testlist.append(KeyValue(key, value))
    mybptree = Btree(4, 4)
    for kv in testlist:
        mybptree.insert(kv)
    mybptree.delete(testlist[0])
    mybptree.show()
    print('\nkey of this b+tree is \n')
    print([kv.key for kv in mybptree.traversal()])


if __name__ == '__main__':
    test()
