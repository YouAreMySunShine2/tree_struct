=========
B+Tree
=========
^^^^^^^^^^^^^^^^^^
B+Tree定义
^^^^^^^^^^^^^^^^^^
- 1.叶子节点小于或等于内部节点（索引节点）
- 2.叶子节点中的数据是key-value
- 3.内部节点包含两个数据结构，1.叶子节点2.叶子节点中数据的中位key
- 4.元素自底向上插入(当存在索引节点时，root记录的每次都是最新生成的节点（索引节点）)
- 5.叶子节点本身的关键字自小而大顺序连接

^^^^^^^^^^^^^^^^^^
数据结构
^^^^^^^^^^^^^^^^^^
- 叶子节点

::

  {
     leaf_num  叶子节点数量
     v_list 数据
     bro  下一个叶子节点路径
     par  直接内部节点
  }

- 内部节点

::

 {
     inter_node_num 内部节点的数量
     tree_leaf_list 叶子节点
     tree_leaf_mid_key 叶子节点的中间key
     self.par  直接内部节点
 }

^^^^^^^^^^^^^^^^^^
关键算法
^^^^^^^^^^^^^^^^^^

---------
1.插入
---------
1.1伪代码

::

    insert_node(node, kv){
        if (!is_leaf()){
          if(is_full()){
            node.insertIndexNode(kv)
            moveHalfNode(node, nodeA)
            insert_node(node.par)
           }else{
            insert_node(node.par)
           }
        }else{
          index = findInsertIndex(node, kv)
          node.insert(kv)
          if(is_full()){
             moveHalfNode(node, nodeB)
             insertIndexNode()
          }
        }
    }

1.2时间复杂度

::

   (n-1)(n+1)=k  k:层级，n:记录数
    n = (k+1)^(1/2)
   T(n) = (k)*(k-1)
   T(n) = O(k^2) = O(n)

---------
2.删除
---------
2.1伪代码

::

   del_node(node, kv){
       if(is_leaf()){
         index = findValueIndex(node, kv)
         node.remove(index)
         if(!is_rich()){
           arrange_node(node, kv)
         }
        }else{
         index = findNodeIndex(n)
         del_node(node.child, kv)
        }
   }
   arrange_node(node, kv){
      index = node.par.findValueIndex(kv)
      if(node.beforeNode.is_rich()){
              moveNode(node.par, nodeB)
        }else{
            moveNode(node.par, nodeB)
            arrange_node(node.par, kv)
         }
   }

2.2时间复杂度

::

  T(n) = k*(k-1)
  T(n) = O(k^2) = O(n)

---------
3.查询
---------
3.1伪代码

::

   search_mi_and_ma(node, ma, mi){
      index1, leaf1 = search_key(node, mi)
      index2, leaf2 = search_key(node, ma)
      result.append(leaf1[index1:])
      while(leaf1.bro == leaf2.bro){
         result.append(leaf1[index1:])
         leaf1=leaf1.bro
      }
    }
   search_key(node, key_value){
         if(is_leaf()){
            index = node.par.findValueIndex(key_value)
            return node,index
          }else{
            index = node.par.findValueIndex(key_value)
            return search_key(node.child, key_value)
          }
    }

3.2时间复杂度

::

  T(n) = k*(k-1)
  T(n) = O(k^2) = O(n)
