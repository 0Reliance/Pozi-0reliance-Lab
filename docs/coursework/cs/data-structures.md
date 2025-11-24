---
title: Data Structures
description: Comprehensive guide to fundamental data structures in computer science
---

# Data Structures

## Overview

Data structures are the fundamental building blocks of computer science. They provide efficient ways to store, organize, and access data. Understanding data structures is essential for writing efficient and scalable software.

## Learning Objectives

By the end of this guide, you will understand:
- Basic and advanced data structures
- Time and space complexity analysis
- When to use specific data structures
- Implementation details and best practices

## Fundamental Concepts

### Time Complexity
Understanding how operations scale with input size is crucial:

| Operation | Array | Linked List | Hash Table |
|-----------|-------|-------------|------------|
| Access | O(1) | O(n) | O(1) average |
| Search | O(n) | O(n) | O(1) average |
| Insertion | O(n) | O(1) | O(1) average |
| Deletion | O(n) | O(1) | O(1) average |

### Space Complexity
Memory usage analysis for different data structures:
- **Static arrays**: Fixed size, predictable memory
- **Dynamic arrays**: Amortized O(1) insertion, O(n) worst case
- **Linked structures**: Extra overhead for pointers
- **Hash tables**: Load factor impacts space usage

## Linear Data Structures

### Arrays

#### Definition
Contiguous memory locations storing elements of the same type.

#### Implementation
```python
class DynamicArray:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.size = 0
        self.array = [None] * capacity
    
    def append(self, element):
        if self.size >= self.capacity:
            self._resize()
        self.array[self.size] = element
        self.size += 1
    
    def _resize(self):
        new_capacity = self.capacity * 2
        new_array = [None] * new_capacity
        for i in range(self.size):
            new_array[i] = self.array[i]
        self.array = new_array
        self.capacity = new_capacity
    
    def get(self, index):
        if index >= self.size:
            raise IndexError("Index out of bounds")
        return self.array[index]
```

#### Use Cases
- Random access patterns
- Fixed-size collections
- Memory-efficient storage for homogeneous data

### Linked Lists

#### Singly Linked List
```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class SinglyLinkedList:
    def __init__(self):
        self.head = None
    
    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def delete(self, data):
        if not self.head:
            return
        
        if self.head.data == data:
            self.head = self.head.next
            return
        
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                return
            current = current.next
```

#### Doubly Linked List
```python
class DoublyNode:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
    
    def append(self, data):
        new_node = DoublyNode(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
```

#### Use Cases
- Frequent insertions/deletions
- Implementing stacks and queues
- Navigation systems

### Stacks

#### Implementation
```python
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        raise IndexError("Stack is empty")
    
    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        raise IndexError("Stack is empty")
    
    def is_empty(self):
        return len(self.items) == 0
```

#### Applications
- Function call management
- Expression evaluation
- Undo/redo functionality
- Browser history

### Queues

#### Implementation
```python
from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, item):
        self.items.append(item)
    
    def dequeue(self):
        if not self.is_empty():
            return self.items.popleft()
        raise IndexError("Queue is empty")
    
    def is_empty(self):
        return len(self.items) == 0
```

#### Applications
- Task scheduling
- Message processing
- Breadth-first search
- Print job management

## Non-Linear Data Structures

### Trees

#### Binary Trees
```python
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None
    
    def insert(self, value):
        if not self.root:
            self.root = TreeNode(value)
        else:
            self._insert_recursive(self.root, value)
    
    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = TreeNode(value)
            else:
                self._insert_recursive(node.right, value)
```

#### Binary Search Trees (BST)
- Search: O(log n) average, O(n) worst case
- Insert: O(log n) average, O(n) worst case
- Delete: O(log n) average, O(n) worst case

#### Balanced Trees
- **AVL Trees**: Self-balancing with height differences ≤ 1
- **Red-Black Trees**: Balanced with color properties
- **B-Trees**: Optimized for disk storage

### Heaps

#### Max Heap Implementation
```python
import heapq

class MaxHeap:
    def __init__(self):
        self.heap = []
    
    def insert(self, value):
        heapq.heappush(self.heap, -value)
    
    def extract_max(self):
        if self.heap:
            return -heapq.heappop(self.heap)
        raise IndexError("Heap is empty")
    
    def peek(self):
        if self.heap:
            return -self.heap[0]
        raise IndexError("Heap is empty")
```

#### Applications
- Priority queues
- Heap sort algorithm
- Dijkstra's algorithm
- Task scheduling

### Graphs

#### Representation
```python
class Graph:
    def __init__(self):
        self.adjacency_list = {}
    
    def add_vertex(self, vertex):
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []
    
    def add_edge(self, vertex1, vertex2, weight=1):
        if vertex1 in self.adjacency_list and vertex2 in self.adjacency_list:
            self.adjacency_list[vertex1].append((vertex2, weight))
            self.adjacency_list[vertex2].append((vertex1, weight))
    
    def bfs(self, start):
        visited = set()
        queue = [start]
        result = []
        
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                result.append(vertex)
                queue.extend([neighbor for neighbor, _ in self.adjacency_list[vertex] 
                             if neighbor not in visited])
        return result
```

#### Applications
- Social networks
- Navigation systems
- Network routing
- Dependency resolution

## Hash-Based Structures

### Hash Tables

#### Implementation
```python
class HashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [[] for _ in range(size)]
    
    def _hash_function(self, key):
        return hash(key) % self.size
    
    def set(self, key, value):
        index = self._hash_function(key)
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                self.table[index][i] = (key, value)
                return
        self.table[index].append((key, value))
    
    def get(self, key):
        index = self._hash_function(key)
        for k, v in self.table[index]:
            if k == key:
                return v
        raise KeyError(f"Key {key} not found")
```

#### Collision Resolution
- **Chaining**: Store colliding elements in linked lists
- **Open Addressing**: Find alternative slots using probing
- **Robin Hood Hashing**: Optimize for reduced variance

## Advanced Data Structures

### Tries (Prefix Trees)

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        current = self.root
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.is_end_of_word = True
    
    def search(self, word):
        current = self.root
        for char in word:
            if char not in current.children:
                return False
            current = current.children[char]
        return current.is_end_of_word
```

### Segment Trees

```python
class SegmentTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.build(arr, 0, 0, self.n - 1)
    
    def build(self, arr, index, start, end):
        if start == end:
            self.tree[index] = arr[start]
        else:
            mid = (start + end) // 2
            self.build(arr, 2 * index + 1, start, mid)
            self.build(arr, 2 * index + 2, mid + 1, end)
            self.tree[index] = self.tree[2 * index + 1] + self.tree[2 * index + 2]
    
    def query(self, index, start, end, l, r):
        if r < start or end < l:
            return 0
        if l <= start and end <= r:
            return self.tree[index]
        mid = (start + end) // 2
        return (self.query(2 * index + 1, start, mid, l, r) +
                self.query(2 * index + 2, mid + 1, end, l, r))
```

## Performance Analysis

### Big O Notation
- **O(1)**: Constant time
- **O(log n)**: Logarithmic time
- **O(n)**: Linear time
- **O(n log n)**: Linearithmic time
- **O(n²)**: Quadratic time
- **O(2ⁿ)**: Exponential time

### Space Complexity
- **O(1)**: Constant space
- **O(n)**: Linear space
- **O(n²)**: Quadratic space
- **O(log n)**: Logarithmic space

## Best Practices

### Choosing the Right Data Structure

| Scenario | Recommended Data Structure | Reason |
|----------|---------------------------|---------|
| Fast lookups | Hash Table | O(1) average time complexity |
| Ordered data | Balanced BST | Maintains sorted order |
| Range queries | Segment Tree | Efficient range operations |
| String matching | Trie | Prefix-based operations |
| Priority operations | Heap | Efficient priority queue |

### Optimization Tips
1. **Profile first**: Measure before optimizing
2. **Consider cache locality**: Arrays vs linked structures
3. **Balance memory and speed**: Trade-offs in implementation
4. **Use built-in structures**: Leverage optimized standard library
5. **Consider amortized analysis**: Long-term performance matters

## Common Interview Questions

### Array Problems
- Two-sum problem
- Maximum subarray
- Rotate array
- Merge intervals

### Linked List Problems
- Detect cycle
- Reverse linked list
- Merge two sorted lists
- LRU cache implementation

### Tree Problems
- Validate BST
- Lowest common ancestor
- Tree traversal (inorder, preorder, postorder)
- Serialize/deserialize tree

### Graph Problems
- Graph traversal (DFS, BFS)
- Shortest path algorithms
- Topological sorting
- Connected components

## Practical Applications

### Real-World Examples
- **Databases**: B-trees for indexing
- **Compilers**: Symbol tables (hash tables)
- **Operating Systems**: Process scheduling (queues)
- **Web Browsers**: History management (stacks)
- **GPS Navigation**: Graph algorithms

### Industry Use Cases
- **Social Media**: Graphs for friend networks
- **E-commerce**: Tries for autocomplete
- **Finance**: Heaps for priority trading
- **Gaming**: Spatial data structures for collision detection

## Exercises

### Beginner
1. Implement a stack using queues
2. Reverse a linked list
3. Check if a string is a palindrome using a stack
4. Implement queue using two stacks

### Intermediate
1. Design a hash table with separate chaining
2. Implement binary search tree with all operations
3. Create a priority queue using a heap
4. Implement graph traversal algorithms

### Advanced
1. Build a balanced BST (AVL or Red-Black)
2. Implement segment tree with range updates
3. Create a trie with autocorrect functionality
4. Design an LRU cache with O(1) operations

## Resources

### Books
- "Introduction to Algorithms" by Cormen et al.
- "Data Structures and Algorithm Analysis" by Mark Allen Weiss
- "Algorithm Design Manual" by Steven Skiena

### Online Courses
- Coursera: Data Structures by University of California San Diego
- edX: Data Structures for Everyone by Microsoft
- MIT OpenCourseWare: Introduction to Algorithms

### Practice Platforms
- LeetCode: Algorithm and data structure problems
- HackerRank: Coding challenges and interviews
- Codeforces: Competitive programming problems

## See Also

- [Algorithms](algorithms.md) - Algorithm design and analysis
- [Database Systems](databases.md) - Database concepts and implementations
- [System Design](../sysadmin/system-design.md) - Large-scale system design

---

*This guide is part of the Computer Science coursework series. For more information, see the [CS Coursework Index](index.md).*
