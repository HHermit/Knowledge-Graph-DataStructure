# 导入必要的库
import csv   # 用于读写 CSV 文件
import os    # 用于操作系统相关功能，如路径处理
import json  # 用于处理 JSON 数据格式
import random # 用于生成随机数（虽然本脚本暂未使用，但常用于数据生成）

# 定义文件路径
# __file__ 表示当前脚本文件的路径
# os.path.dirname 获取父目录
# 这样可以确保无论在哪里运行脚本，都能找到正确的 data 目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ENTITY_FILE = os.path.join(DATA_DIR, 'entity.csv')
RELATION_FILE = os.path.join(DATA_DIR, 'relation.csv')

# 确保 data 目录存在，如果不存在则创建
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def generate_data():
    print("Generating data...")
    
    # 1. 生成实体 (Nodes)
    # 实体代表知识图谱中的节点，例如具体的"数组"、"排序算法"等
    entities = [
        # Data Structures (数据结构类)
        # id: 唯一标识符
        # name: 显示名称
        # labels: 标签，用于分类（如 Data Structure, Linear）
        # properties: 属性，存储详细信息（如描述、时间复杂度）
        {"id": 1, "name": "Array", "labels": ["Data Structure", "Linear"], "properties": {"description": "连续内存分配", "access_time": "O(1)", "insert_time": "O(n)"}},
        {"id": 2, "name": "Linked List", "labels": ["Data Structure", "Linear"], "properties": {"description": "链式存储结构", "access_time": "O(n)", "insert_time": "O(1)"}},
        {"id": 3, "name": "Stack", "labels": ["Data Structure", "Linear"], "properties": {"description": "后进先出 (LIFO)", "operations": "push, pop"}},
        {"id": 4, "name": "Queue", "labels": ["Data Structure", "Linear"], "properties": {"description": "先进先出 (FIFO)", "operations": "enqueue, dequeue"}},
        {"id": 5, "name": "Tree", "labels": ["Data Structure", "Non-Linear"], "properties": {"description": "层级结构", "root": "Root Node"}},
        {"id": 6, "name": "Graph", "labels": ["Data Structure", "Non-Linear"], "properties": {"description": "节点和边的集合", "types": "Directed, Undirected"}},
        {"id": 7, "name": "Hash Table", "labels": ["Data Structure"], "properties": {"description": "键值对映射", "collision_resolution": "Chaining, Open Addressing"}},
        {"id": 8, "name": "Heap", "labels": ["Data Structure", "Tree-based"], "properties": {"description": "优先队列实现", "types": "Min-Heap, Max-Heap"}},
        
        # Algorithms (算法类)
        {"id": 21, "name": "Sorting", "labels": ["Algorithm"], "properties": {"description": "将元素按顺序排列"}},
        {"id": 22, "name": "Searching", "labels": ["Algorithm"], "properties": {"description": "在数据集中查找特定元素"}},
        {"id": 23, "name": "Bubble Sort", "labels": ["Algorithm", "Sorting"], "properties": {"complexity": "O(n^2)", "stable": "Yes"}},
        {"id": 24, "name": "Quick Sort", "labels": ["Algorithm", "Sorting"], "properties": {"complexity": "O(n log n)", "stable": "No"}},
        {"id": 25, "name": "Binary Search", "labels": ["Algorithm", "Searching"], "properties": {"complexity": "O(log n)", "precondition": "Sorted Array"}},
        {"id": 26, "name": "Dijkstra", "labels": ["Algorithm", "Graph Algorithm"], "properties": {"description": "最短路径算法", "weight": "Non-negative"}},
        
        # Concepts (概念类)
        {"id": 41, "name": "Recursion", "labels": ["Concept"], "properties": {"description": "函数调用自身"}},
        {"id": 42, "name": "Time Complexity", "labels": ["Concept"], "properties": {"notation": "Big O"}},
        {"id": 43, "name": "Space Complexity", "labels": ["Concept"], "properties": {"notation": "Big O"}},
        
        # Complexity Classes (复杂度类别)
        {"id": 51, "name": "O(1)", "labels": ["Complexity"], "properties": {"name": "Constant Time"}},
        {"id": 52, "name": "O(n)", "labels": ["Complexity"], "properties": {"name": "Linear Time"}},
        {"id": 53, "name": "O(log n)", "labels": ["Complexity"], "properties": {"name": "Logarithmic Time"}},
        {"id": 54, "name": "O(n^2)", "labels": ["Complexity"], "properties": {"name": "Quadratic Time"}}
    ]

    # 将实体写入 CSV 文件
    # encoding='utf-8' 确保中文不乱码
    # newline='' 防止产生多余的空行
    with open(ENTITY_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # 写入表头：id, name, labels (用 | 分隔), properties (JSON 字符串)
        writer.writerow(['id', 'name', 'labels', 'properties'])
        
        for e in entities:
            labels_str = "|".join(e['labels']) # 将列表转换为字符串，如 "Data Structure|Linear"
            props_str = json.dumps(e['properties'], ensure_ascii=False) # 将字典转换为 JSON 字符串
            writer.writerow([e['id'], e['name'], labels_str, props_str])
            
    print(f"Entities generated: {len(entities)}")

    # 2. 生成关系 (Relationships)
    # 关系代表节点之间的连接，例如 "Bubble Sort" (IS_A) "Sorting"
    relationships = [
        # IS_A (属于关系)
        {"source": 23, "target": 21, "type": "IS_A", "properties": {"description": "属于排序算法"}},
        {"source": 24, "target": 21, "type": "IS_A", "properties": {"description": "属于排序算法"}},
        {"source": 25, "target": 22, "type": "IS_A", "properties": {"description": "属于搜索算法"}},
        
        # USES (使用关系)
        {"source": 3, "target": 1, "type": "USES", "properties": {"context": "Implementation"}},
        {"source": 3, "target": 2, "type": "USES", "properties": {"context": "Implementation"}},
        {"source": 25, "target": 1, "type": "USES", "properties": {"requirement": "Sorted"}},
        
        # OPERATES_ON (操作对象)
        {"source": 26, "target": 6, "type": "OPERATES_ON", "properties": {"target": "Weighted Graph"}},
        
        # TIME_COMPLEXITY (时间复杂度)
        {"source": 1, "target": 51, "type": "TIME_COMPLEXITY", "properties": {"operation": "Access"}},
        {"source": 2, "target": 52, "type": "TIME_COMPLEXITY", "properties": {"operation": "Access"}},
        {"source": 23, "target": 54, "type": "TIME_COMPLEXITY", "properties": {"case": "Average"}},
        {"source": 25, "target": 53, "type": "TIME_COMPLEXITY", "properties": {"case": "Worst"}},
        
        # RELATED_TO (相关关系)
        {"source": 5, "target": 41, "type": "RELATED_TO", "properties": {"concept": "Traversal"}},
        {"source": 24, "target": 41, "type": "RELATED_TO", "properties": {"concept": "Divide and Conquer"}}
    ]

    # 将关系写入 CSV 文件
    with open(RELATION_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # 写入表头：source_id (源节点ID), target_id (目标节点ID), type (关系类型), properties (属性)
        writer.writerow(['source_id', 'target_id', 'type', 'properties'])
        
        for r in relationships:
            props_str = json.dumps(r['properties'], ensure_ascii=False)
            writer.writerow([r['source'], r['target'], r['type'], props_str])

    print(f"Relationships generated: {len(relationships)}")
    print("Done.")

if __name__ == '__main__':
    generate_data()
