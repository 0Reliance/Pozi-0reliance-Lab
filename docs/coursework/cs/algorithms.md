---
title: Algorithms
description: Comprehensive guide to algorithm design, analysis, and implementation
---

# Algorithms

## Overview

Algorithms are step-by-step procedures for solving problems and performing tasks. They are the heart of computer science, enabling us to process data efficiently and solve complex computational problems.

## Learning Objectives

By the end of this guide, you will understand:
- Algorithm design techniques and paradigms
- Time and space complexity analysis
- Classic algorithms and their applications
- Algorithm optimization and trade-offs

## Fundamental Concepts

### Algorithm Properties
A good algorithm should be:
- **Correct**: Produces the right output for all valid inputs
- **Efficient**: Uses resources (time, space) optimally
- **Clear**: Easy to understand and implement
- **Scalable**: Performance degrades gracefully with input size

### Complexity Analysis
Big O notation describes how algorithm performance scales:

| Complexity | Description | Example |
|------------|-------------|---------|
| O(1) | Constant time | Array access |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Linear search |
| O(n log n) | Linearithmic | Merge sort |
| O(n²) | Quadratic | Bubble sort |
| O(2ⁿ) | Exponential | Recursive Fibonacci |

## Algorithm Design Paradigms

### 1. Divide and Conquer

Break problems into smaller subproblems, solve recursively, then combine results.

#### Merge Sort
```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

#### Quick Sort
```python
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)
```

### 2. Dynamic Programming

Break problems into overlapping subproblems, store solutions to avoid recomputation.

#### Fibonacci with Memoization
```python
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 2:
        return 1
    
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]
```

#### Longest Common Subsequence
```python
def lcs(X, Y):
    m, n = len(X), len(Y)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                dp[i][j] = 0
            elif X[i-1] == Y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]
```

#### Knapsack Problem
```python
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    for i in range(n + 1):
        for w in range(capacity + 1):
            if i == 0 or w == 0:
                dp[i][w] = 0
            elif weights[i-1] <= w:
                dp[i][w] = max(values[i-1] + dp[i-1][w-weights[i-1]], 
                              dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]
    
    return dp[n][capacity]
```

### 3. Greedy Algorithms

Make locally optimal choices at each step, hoping to find a global optimum.

#### Huffman Coding
```python
import heapq

class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq

def huffman_coding(char_freq):
    heap = []
    for char, freq in char_freq.items():
        heapq.heappush(heap, HuffmanNode(char, freq))
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)
    
    return heap[0]

def generate_codes(root, code="", codes={}):
    if root:
        if root.char is not None:
            codes[root.char] = code
        generate_codes(root.left, code + "0", codes)
        generate_codes(root.right, code + "1", codes)
    return codes
```

#### Dijkstra's Shortest Path
```python
import heapq

def dijkstra(graph, start):
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    previous = {}
    
    pq = [(0, start)]
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        if current_dist > distances[current]:
            continue
        
        for neighbor, weight in graph[current].items():
            distance = current_dist + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current
                heapq.heappush(pq, (distance, neighbor))
    
    return distances, previous
```

### 4. Backtracking

Explore all possible solutions by building candidates incrementally.

#### N-Queens Problem
```python
def solve_n_queens(n):
    board = [['.' for _ in range(n)] for _ in range(n)]
    solutions = []
    
    def is_safe(row, col):
        # Check this row on left side
        for i in range(col):
            if board[row][i] == 'Q':
                return False
        
        # Check upper diagonal on left side
        for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
            if board[i][j] == 'Q':
                return False
        
        # Check lower diagonal on left side
        for i, j in zip(range(row, n), range(col, -1, -1)):
            if board[i][j] == 'Q':
                return False
        
        return True
    
    def solve(col):
        if col >= n:
            solutions.append([''.join(row) for row in board])
            return
        
        for row in range(n):
            if is_safe(row, col):
                board[row][col] = 'Q'
                solve(col + 1)
                board[row][col] = '.'
    
    solve(0)
    return solutions
```

#### Sudoku Solver
```python
def solve_sudoku(board):
    def find_empty():
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return i, j
        return None
    
    def is_valid(num, pos):
        # Check row
        for j in range(9):
            if board[pos[0]][j] == num and pos[1] != j:
                return False
        
        # Check column
        for i in range(9):
            if board[i][pos[1]] == num and pos[0] != i:
                return False
        
        # Check 3x3 box
        box_x = pos[1] // 3
        box_y = pos[0] // 3
        
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if board[i][j] == num and (i, j) != pos:
                    return False
        
        return True
    
    find = find_empty()
    if not find:
        return True
    else:
        row, col = find
    
    for num in range(1, 10):
        if is_valid(num, (row, col)):
            board[row][col] = num
            
            if solve_sudoku(board):
                return True
            
            board[row][col] = 0
    
    return False
```

## Sorting Algorithms

### Comparison-Based Sorting

#### Bubble Sort
```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr
```

#### Insertion Sort
```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
```

#### Selection Sort
```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
```

### Non-Comparison Sorting

#### Counting Sort
```python
def counting_sort(arr):
    max_val = max(arr)
    count = [0] * (max_val + 1)
    
    for num in arr:
        count[num] += 1
    
    for i in range(1, len(count)):
        count[i] += count[i - 1]
    
    output = [0] * len(arr)
    for num in reversed(arr):
        count[num] -= 1
        output[count[num]] = num
    
    return output
```

#### Radix Sort
```python
def counting_sort_for_radix(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    
    for i in range(n):
        index = arr[i] // exp
        count[index % 10] += 1
    
    for i in range(1, 10):
        count[i] += count[i - 1]
    
    for i in range(n - 1, -1, -1):
        index = arr[i] // exp
        output[count[index % 10] - 1] = arr[i]
        count[index % 10] -= 1
    
    return output

def radix_sort(arr):
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        arr = counting_sort_for_radix(arr, exp)
        exp *= 10
    return arr
```

## Search Algorithms

### Linear Search
```python
def linear_search(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
```

### Binary Search
```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1
```

### Interpolation Search
```python
def interpolation_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right and target >= arr[left] and target <= arr[right]:
        if left == right:
            return left if arr[left] == target else -1
        
        pos = left + ((target - arr[left]) * (right - left)) // (arr[right] - arr[left])
        
        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            left = pos + 1
        else:
            right = pos - 1
    
    return -1
```

## Graph Algorithms

### Depth-First Search (DFS)
```python
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    
    visited.add(start)
    print(start, end=' ')
    
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
    
    return visited
```

### Breadth-First Search (BFS)
```python
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        vertex = queue.popleft()
        print(vertex, end=' ')
        
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return visited
```

### Topological Sort
```python
def topological_sort(graph):
    visited = set()
    stack = []
    
    def dfs(vertex):
        visited.add(vertex)
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                dfs(neighbor)
        stack.append(vertex)
    
    for vertex in graph:
        if vertex not in visited:
            dfs(vertex)
    
    return stack[::-1]
```

### Minimum Spanning Tree

#### Prim's Algorithm
```python
import heapq

def prim_mst(graph):
    start = list(graph.keys())[0]
    visited = set([start])
    edges = [(weight, start, neighbor) for neighbor, weight in graph[start].items()]
    heapq.heapify(edges)
    
    mst = []
    total_weight = 0
    
    while edges:
        weight, u, v = heapq.heappop(edges)
        
        if v not in visited:
            visited.add(v)
            mst.append((u, v, weight))
            total_weight += weight
            
            for neighbor, w in graph[v].items():
                if neighbor not in visited:
                    heapq.heappush(edges, (w, v, neighbor))
    
    return mst, total_weight
```

#### Kruskal's Algorithm
```python
def kruskal_mst(edges, vertices):
    parent = {v: v for v in vertices}
    rank = {v: 0 for v in vertices}
    
    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    
    def union(u, v):
        root_u = find(u)
        root_v = find(v)
        
        if rank[root_u] > rank[root_v]:
            parent[root_v] = root_u
        elif rank[root_u] < rank[root_v]:
            parent[root_u] = root_v
        else:
            parent[root_v] = root_u
            rank[root_u] += 1
    
    edges.sort(key=lambda x: x[2])
    mst = []
    
    for u, v, weight in edges:
        if find(u) != find(v):
            union(u, v)
            mst.append((u, v, weight))
    
    return mst
```

## String Algorithms

### Pattern Matching

#### KMP Algorithm
```python
def kmp_search(text, pattern):
    def compute_lps(pattern):
        lps = [0] * len(pattern)
        length = 0
        i = 1
        
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps
    
    lps = compute_lps(pattern)
    i = j = 0
    matches = []
    
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
        
        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    return matches
```

#### Rabin-Karp Algorithm
```python
def rabin_karp_search(text, pattern):
    n = len(text)
    m = len(pattern)
    d = 256  # Number of characters in alphabet
    q = 101  # Prime number
    
    h = 1
    for i in range(m - 1):
        h = (h * d) % q
    
    pattern_hash = 0
    text_hash = 0
    
    for i in range(m):
        pattern_hash = (d * pattern_hash + ord(pattern[i])) % q
        text_hash = (d * text_hash + ord(text[i])) % q
    
    matches = []
    
    for i in range(n - m + 1):
        if pattern_hash == text_hash:
            if text[i:i+m] == pattern:
                matches.append(i)
        
        if i < n - m:
            text_hash = (d * (text_hash - ord(text[i]) * h) + ord(text[i + m])) % q
            if text_hash < 0:
                text_hash += q
    
    return matches
```

## Advanced Topics

### Randomized Algorithms

#### Randomized Quick Sort
```python
import random

def randomized_quicksort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = random.choice(arr)
    less = [x for x in arr if x < pivot]
    equal = [x for x in arr if x == pivot]
    greater = [x for x in arr if x > pivot]
    
    return randomized_quicksort(less) + equal + randomized_quicksort(greater)
```

### Approximation Algorithms

#### Traveling Salesman Problem (Approximation)
```python
import itertools

def tsp_approximation(graph):
    start = list(graph.keys())[0]
    unvisited = set(graph.keys())
    unvisited.remove(start)
    
    path = [start]
    current = start
    total_distance = 0
    
    while unvisited:
        nearest = min(unvisited, key=lambda x: graph[current][x])
        path.append(nearest)
        total_distance += graph[current][nearest]
        unvisited.remove(nearest)
        current = nearest
    
    # Return to start
    total_distance += graph[current][start]
    path.append(start)
    
    return path, total_distance
```

## Algorithm Analysis

### Performance Testing
```python
import time
import random

def benchmark_algorithm(algorithm, input_sizes, iterations=10):
    results = {}
    
    for size in input_sizes:
        times = []
        
        for _ in range(iterations):
            # Generate random input
            data = [random.randint(0, 1000) for _ in range(size)]
            
            # Measure execution time
            start_time = time.time()
            algorithm(data.copy())
            end_time = time.time()
            
            times.append(end_time - start_time)
        
        results[size] = {
            'avg_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times)
        }
    
    return results
```

## Best Practices

### Algorithm Selection Guidelines

| Problem Type | Recommended Algorithms | When to Use |
|--------------|----------------------|-------------|
| Sorting | Quick Sort, Merge Sort | Large datasets, general purpose |
| Small Sorts | Insertion Sort | Small arrays (< 100 elements) |
| Stable Sort | Merge Sort | Maintaining relative order |
| Search | Binary Search | Sorted data |
| Pattern Matching | KMP, Rabin-Karp | String searching |
| Shortest Path | Dijkstra | Weighted graphs |
| MST | Prim, Kruskal | Connected graphs |
| Optimization | DP, Greedy | Optimal solutions needed |

### Optimization Tips
1. **Choose the right data structure**: Algorithms depend on underlying structures
2. **Consider input characteristics**: Sorted, nearly sorted, random distributions
3. **Profile your code**: Measure before optimizing
4. **Use built-in algorithms**: Standard library implementations are optimized
5. **Consider space-time tradeoffs**: Memory usage vs. speed

## Common Interview Problems

### Classic Algorithm Questions
1. **Two Sum Problem** - Find pairs that sum to target
2. **Maximum Subarray** - Kadane's algorithm
3. **Longest Increasing Subsequence** - Dynamic programming
4. **Edit Distance** - String similarity
5. **Coin Change** - Minimum coins to make amount
6. **Tree Traversals** - Inorder, preorder, postorder
7. **Graph Cycles** - Detect cycles in directed/undirected graphs
8. **Palindrome Checking** - String manipulation

### Problem-Solving Framework
1. **Understand the problem**: Clarify requirements and constraints
2. **Brute force first**: Simple, working solution
3. **Optimize**: Identify inefficiencies and improve
4. **Test**: Verify with edge cases and large inputs
5. **Analyze**: Time and space complexity

## Practical Applications

### Real-World Algorithm Uses
- **Navigation Systems**: Shortest path algorithms
- **Recommendation Engines**: Collaborative filtering algorithms
- **Search Engines**: PageRank, indexing algorithms
- **Financial Trading**: High-frequency trading algorithms
- **Bioinformatics**: Sequence alignment algorithms
- **Cryptography**: Encryption and hash algorithms

### Industry Applications
- **Google**: PageRank, search algorithms
- **Amazon**: Recommendation algorithms, logistics optimization
- **Netflix**: Content recommendation algorithms
- **Uber**: Route optimization, surge pricing algorithms
- **Airbnb**: Dynamic pricing algorithms

## Exercises

### Beginner
1. Implement binary search recursively
2. Write a function to check if a string is a palindrome
3. Find the maximum element in an array
4. Implement bubble sort
5. Write a function to reverse a string

### Intermediate
1. Implement merge sort and quick sort
2. Solve the knapsack problem
3. Find the shortest path in a weighted graph
4. Implement hash table collision resolution
5. Write a regex engine for simple patterns

### Advanced
1. Implement A* pathfinding algorithm
2. Solve the traveling salesman problem approximately
3. Design a load balancer algorithm
4. Implement a consistent hashing ring
5. Create a distributed consensus algorithm

## Resources

### Books
- "Introduction to Algorithms" by Cormen et al.
- "Algorithm Design Manual" by Steven Skiena
- "Algorithms" by Robert Sedgewick and Kevin Wayne
- "The Art of Computer Programming" by Donald Knuth

### Online Courses
- Coursera: Algorithms by Stanford University
- edX: Algorithmic Design and Techniques by UC San Diego
- MIT OpenCourseWare: Introduction to Algorithms

### Practice Platforms
- LeetCode: Algorithm challenges and interview preparation
- HackerRank: Algorithmic problem solving
- Codeforces: Competitive programming contests
- TopCoder: Algorithm competitions

## See Also

- [Data Structures](data-structures.md) - Foundation for algorithm implementation
- [Database Systems](databases.md) - Algorithm applications in data management
- [System Design](../sysadmin/system-design.md) - Algorithm design in large systems

---

*This guide is part of the Computer Science coursework series. For more information, see the [CS Coursework Index](index.md).*
