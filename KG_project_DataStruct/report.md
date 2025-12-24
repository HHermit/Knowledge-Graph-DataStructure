# 数据结构知识图谱构建实验报告

## 一、 实验概述

本实验旨在构建一个基于 Web 的“数据结构”学科知识图谱应用。通过 Neo4j 图数据库存储知识点及其关系，利用 Python Flask 构建后端 API，并使用 Vue.js 结合 ECharts 实现前端的可视化展示与交互。

## 二、 系统设计

### 1. 技术栈

- **数据库**: Neo4j (图数据存储)
- **后端**: Python Flask (RESTful API)
- **前端**: Vue.js 3 + Vite (用户界面)
- **可视化**: Apache ECharts (图谱渲染)

### 2. 数据模型

- **节点 (Node)**:
  - Label: `Data Structure`, `Algorithm`, `Concept`, `Complexity`
  - Properties: `id`, `name`
- **关系 (Relationship)**:
  - Types: `IS_A` (属于), `USES` (使用), `OPERATES_ON` (操作于), `TIME_COMPLEXITY` (时间复杂度), `RELATED_TO` (相关)

### 3. 系统架构

前端 (Vue) <--> HTTP (Axios) <--> 后端 (Flask) <--> Bolt Protocol <--> 数据库 (Neo4j)

## 三、 核心代码实现

### 1. 数据生成 (Python)

使用 Python 脚本生成模拟数据 `entity.csv` 和 `relation.csv`。

```python
# scripts/generate_data.py 片段
entities = [
    (1, 'Array', 'Data Structure'),
    (21, 'Sorting', 'Algorithm'),
    ...
]
relations = [
    (23, 21, 'IS_A'), # Bubble Sort IS_A Sorting
    ...
]
```

### 2. 后端 API (Flask)

实现图数据查询接口。

```python
# backend/routes.py
@api_bp.route('/graph', methods=['GET'])
def get_graph():
    session = db.get_session()
    result = session.run("MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 300")
    # ... 解析结果为 nodes 和 links ...
    return jsonify({"nodes": nodes, "links": links})
```

### 3. 前端可视化 (Vue + ECharts)

使用 ECharts 渲染力导向图。

```javascript
// frontend/src/components/KnowledgeGraph.vue
const option = {
  series: [
    {
      type: "graph",
      layout: "force",
      data: formattedNodes,
      links: formattedLinks,
      roam: true,
      force: { repulsion: 300 },
    },
  ],
};
myChart.setOption(option);
```

## 四、 操作步骤

### 1. 环境准备

- 安装 Neo4j Desktop 并启动数据库。
- 修改 `backend/db.py` 中的数据库连接配置（用户名/密码）。

### 2. 后端启动

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev -- --host
```

### 4. 数据初始化

- 打开前端页面 (通常是 `http://localhost:5173`)。
- 点击页面顶部的 **"Reset/Init DB"** 按钮，系统将自动读取 CSV 文件并导入 Neo4j。

## 五、 实验总结与难点分析

### 1. 技术难点

- **大规模节点渲染**: 当节点数量增多时，前端渲染性能会下降。本实验通过 ECharts 的 WebGL 模式或限制返回节点数量 (`LIMIT 300`) 来优化。
- **Cypher 查询优化**: 复杂的路径查询（如最短路径）在数据量大时可能变慢。使用了 Neo4j 内置的 `shortestPath` 函数来提高效率。
- **数据一致性**: 导入 CSV 数据时，需要确保 ID 的唯一性和关系的正确对应。

### 2. 总结

通过本实验，完整实现了从数据建模、后端 API 开发到前端可视化的全栈流程。掌握了 Neo4j 在知识图谱构建中的核心应用，以及如何通过 Web 技术展示图数据。
