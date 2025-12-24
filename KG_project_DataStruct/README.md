# 学科知识图谱构建系统 (Subject Knowledge Graph Construction)

本项目是一个基于 **Neo4j** 图数据库和 **Vue 3** 前端框架的学科知识图谱构建与可视化系统。它旨在帮助用户直观地理解数据结构（Data Structures）与算法（Algorithms）之间的复杂关系。

## 1. 项目简介 (Introduction)

本系统通过交互式图谱展示知识点之间的关联，支持路径查询、模糊搜索以及数据的导入导出。

**核心功能**：
*   **知识图谱可视化**：使用 D3.js 和 ECharts 展示实体（如数组、链表、排序算法）及其关系（如 IS_A, USES）。
*   **路径查询**：支持查询两个知识点之间的最短路径。
*   **数据管理**：提供csv数据导入、导出及数据库初始化/重置功能。
*   **增删改查**：支持在界面上直接添加、编辑、删除节点和关系，以及管理其属性。
*   **交互式搜索**：支持模糊搜索节点并定位。

## 2. 项目结构 (Project Structure)

```text
KG_project_DataStruct/
├── backend/                # 后端代码 (Flask)
│   ├── app.py              # 应用入口
│   ├── config.py           # 配置文件
│   ├── db.py               # Neo4j 数据库连接管理
│   ├── routes/             # API 路由模块
│   │   ├── graph.py        # 图查询相关接口
│   │   └── data.py         # 数据导入导出接口
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端代码 (Vue 3 + Vite)
│   ├── src/
│   │   ├── api/            # API 请求封装
│   │   ├── components/     # Vue 组件 (Sidebar, KnowledgeGraph, etc.)
│   │   └── App.vue         # 主应用组件
│   ├── package.json        # Node.js 依赖
│   └── vite.config.js      # Vite 配置
├── data/                   # 数据文件存储
│   ├── entity.csv          # 当前使用的实体数据
│   ├── relation.csv        # 当前使用的关系数据
│   └── *_template.csv      # 导入模板
├── scripts/
│   └── generate_data.py    # 初始数据生成脚本
└── README.md               # 项目文档
```

## 3. 环境要求 (Prerequisites)

在开始部署之前，请确保您的开发环境满足以下要求：

*   **操作系统**：Windows / macOS / Linux
*   **数据库**：[Neo4j Database](https://neo4j.com/download/) (推荐版本 5.x)
    *   需开启 Bolt 协议端口 (默认 7687)
*   **后端环境**：Python 3.10+
*   **前端环境**：Node.js 16+ & npm

## 4. 安装与配置 (Installation)

### 4.1 获取代码
```bash 
git clone <repository_url>
cd KG_project_DataStruct
```

### 4.2 后端设置 (Backend)
1.  进入后端目录并安装依赖：
    ```bash
    cd backend
    pip install -r requirements.txt
    ```
2.  **配置数据库连接**：
    项目默认连接本地 Neo4j (`bolt://localhost:7687`)，用户 `neo4j`，密码 `neo4jDatabase`。
    
    如需修改，请设置以下环境变量（推荐）或直接修改 `backend/config.py`：
    *   `NEO4J_URI`: 数据库地址
    *   `NEO4J_USER`: 用户名
    *   `NEO4J_PASSWORD`: 密码

    **Windows PowerShell 设置示例**：
    ```powershell
    $env:NEO4J_PASSWORD="your_new_password"
    ```

### 4.3 前端设置 (Frontend)
1.  进入前端目录并安装依赖：
    ```bash
    cd ../frontend
    npm install
    ```

## 5. 快速启动 (Getting Started)

### 步骤 1：生成初始数据
在项目根目录下运行脚本，生成基础 CSV 数据：
```bash
python scripts/generate_data.py
```

### 步骤 2：启动后端服务
```bash
cd backend
python app.py
# 服务将运行在 http://127.0.0.1:5000
```

### 步骤 3：启动前端服务
新建终端窗口：
```bash
cd frontend
npm run dev -- --host
# 访问 http://localhost:5173
```

## 6. API 接口文档 (API Reference)

后端提供了一系列 RESTful API 供前端调用：

| 方法 | 路径 | 描述 | 参数 |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/test` | 测试后端连通性 | 无 |
| **GET** | `/api/graph` | 获取全图数据 | 无 |
| **GET** | `/api/search` | 搜索节点 | `q`: 搜索关键词 |
| **GET** | `/api/path` | 查询最短路径 | `start`: 起点ID/名, `end`: 终点ID/名 |
| **POST** | `/api/init` | 重置数据库 | 无 (恢复至上次保存或初始状态) |
| **POST** | `/api/save` | 保存当前快照 | 无 (保存至 `saved_*.csv`) |
| **POST** | `/api/import` | 导入 CSV 数据 | `entity_file`, `relation_file` (文件流) |
| **GET** | `/api/template/entity` | 下载实体模板 | 无 |
| **GET** | `/api/template/relation` | 下载关系模板 | 无 |
| **POST** | `/api/node` | 创建节点 | `{name, label, properties}` |
| **PUT** | `/api/node/<id>/property` | 更新节点属性 | `{key, value}` |
| **DELETE** | `/api/node/<id>` | 删除节点 | 无 |
| **POST** | `/api/relationship` | 创建关系 | `{source_id, target_id, type, properties}` |
| **DELETE** | `/api/relationship` | 删除关系 | `source_id, target_id` |

## 7. 功能操作指南 (Usage)

### 7.1 界面概览
*   **Sidebar (左侧)**：控制面板，包含搜索、路径查询、数据管理等功能。
*   **Canvas (中间)**：交互式图谱，支持缩放、拖拽。
*   **Info Panel (右侧)**：选中节点/边后显示详情，支持编辑属性。

### 7.2 数据管理详解
*   **Reset Database**: 清空当前数据库，并重新加载 `data/` 目录下的 CSV 文件。如果存在 `saved_entity.csv` (快照)，则优先加载快照，否则加载 `entity.csv` (原始数据)。
*   **Save Database**: 将当前图谱的所有节点和关系保存为 `saved_entity.csv` 和 `saved_relation.csv`。这相当于创建一个"存档点"。
*   **Import Data**: 上传自定义 CSV 文件覆盖当前数据。**注意**：导入操作会先清空数据库，然后写入新数据并自动保存为新的原始数据文件。

### 7.3 编辑与维护 (Editing & Maintenance)
*   **添加节点**：在侧边栏 "Add Node" 区域输入名称和标签，点击 "Create Node"。
*   **添加关系**：在 "Add Edge" 区域输入源节点和目标节点的名称，选择关系类型，点击 "Create Edge"。
*   **编辑属性**：点击任意节点或边，在右侧面板中点击 "➕" 添加属性，或点击属性旁的 "×" 删除属性。
*   **删除对象**：在右侧面板底部点击 "Delete" 按钮删除当前选中的节点或边。

## 8. 常见问题排查 (Troubleshooting)

### Q1: 后端启动报错 `ServiceUnavailable`
*   **现象**：`neo4j.exceptions.ServiceUnavailable: Cannot open connection to ...`
*   **原因**：无法连接到 Neo4j 数据库。
*   **解决**：
    1.  检查 Neo4j 服务是否已启动。
    2.  确认 `backend/config.py` 中的端口 (默认 7687) 和密码是否正确。

### Q2: 前端显示 "Network Error"
*   **原因**：前端无法连接到后端 API。
*   **解决**：确保后端服务正在运行，且端口为 5000。

### Q3: 中文乱码问题
*   **原因**：CSV 文件编码非 UTF-8。
*   **解决**：导入数据时，请确保 CSV 文件使用 **UTF-8** 编码保存。Excel 用户请使用 "另存为 -> CSV UTF-8"。
