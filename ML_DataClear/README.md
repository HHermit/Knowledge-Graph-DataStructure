# 学科知识图谱构建 - 自动化知识抽取管道 (ML_DataClear)

本项目是“学科知识图谱构建及应用”课程实验的核心数据处理模块。它实现了一个基于 **NLP** 和 **机器学习** 的自动化管道，能够从非结构化教材文本中提取专业术语（实体）及其关系，生成可直接导入 Neo4j 的结构化数据。

## 🚀 项目亮点

- **自动化抽取**：从原始文本到 CSV 数据的端到端处理。
- **混合架构**：结合了 **spaCy 依存句法分析**（规则）和 **Random Forest 分类器**（机器学习）。
- **可视化评估**：训练过程输出详细的 Pandas 表格报告，包含 Precision, Recall, F1 等多维度指标。
- **模块化设计**：代码经过深度重构，逻辑解耦，核心组件（分词、特征工程、抽取器）均可独立复用。
- **深度优化**：
  - ✅ **实体去重**：自动过滤“性表”、“表是”等碎片化噪声。
  - ✅ **关系预测**：利用监督学习模型预测隐含关系。
  - ✅ **标准输出**：生成符合 Neo4j `LOAD CSV` 标准的格式。

## ⚡ 运行顺序 (Quick Start)

本项目采用 **“先离线训练，后在线抽取”** 的流程。请严格按照以下顺序执行（推荐在项目根目录下运行）：

### 阶段 A：环境准备
```bash
pip install -r requirements.txt
python -m spacy download zh_core_web_sm
```

### 阶段 B：离线模型训练 (仅需执行一次)
利用规则自动生成数据并训练机器学习模型。
1. **构建训练数据**：
   ```bash
   python -m src.build_dataset
   ```
2. **训练关系分类模型**：
   ```bash
   python -m src.train_model
   ```

### 阶段 C：在线知识抽取 (生产运行)
加载训练好的模型，对目标文本进行全量抽取。
```bash
python -m src.knowledge_extractor
# 最终产出: data/output/entity.csv, data/output/relation.csv
```

## 📂 文件结构与作用

### 核心代码 (src/)
| 文件名 | 作用说明 |
|:---|:---|
| `src/knowledge_extractor.py` | **入口脚本**。配置路径并启动知识抽取主管道。 |
| `src/pipeline.py` | **主管道编排**。串联预处理、实体抽取、关系抽取和导出流程。 |
| `src/nlp_core.py` | **核心 NLP 组件**。包含自定义 Jieba 分词器、文本预处理器和模型加载逻辑。 |
| `src/features.py` | **特征工程**。定义 `FeatureExtractor` 类，供训练和预测阶段共用。 |
| `src/entity_extraction.py` | **实体抽取**。封装基于词典和 NER 的实体识别及智能过滤逻辑。 |
| `src/relation_extraction.py` | **关系抽取**。整合 ML 模型预测与基于依存句法的规则匹配。 |
| `src/build_dataset.py` | **数据生成器**。利用规则自动标注文本，生成训练集。 |
| `src/train_model.py` | **模型训练器**。训练随机森林模型并输出可视化评估报告。 |

### 数据与模型
| 路径 | 作用说明 |
|:---|:---|
| `data/raw/source_text.txt` | 教材原始文本输入。 |
| `data/config/domain_vocab.txt` | 领域专业词典。 |
| `data/processed/train_data.json` | 生成的“银标准”训练数据。 |
| `models/relation_classifier.pkl` | 训练好的随机森林模型文件。 |
| `data/output/` | 存放生成的 `entity.csv` 和 `relation.csv`。 |

## 🛠️ 核心模块与功能说明 (Core Modules)

本项目集成了多个强大的 Python 库，每个库都承担着特定的关键任务：

| 模块/库 | 核心功能 | 在本项目中的具体作用 |
| :--- | :--- | :--- |
| **[jieba](https://github.com/fxsjy/jieba)** | **中文分词** | **分词引擎**。替换 spaCy 的默认分词器，精准切分领域长词，防止术语被切碎。 |
| **[spaCy](https://spacy.io/)** | **NLP 框架** | **句法分析与 NER**。提供依存句法分析 (Dependency Parsing) 以识别主谓宾结构。 |
| **[scikit-learn](https://scikit-learn.org/)** | **机器学习** | **关系分类器**。使用 `RandomForestClassifier` 训练关系预测模型。 |
| **[pandas](https://pandas.pydata.org/)** | **数据处理** | **CSV 导出 & 报表**。负责导出 Neo4j 兼容 CSV，并生成评估表格。 |
| **[joblib](https://joblib.readthedocs.io/)** | **模型持久化** | **模型保存与加载**。负责将训练好的模型序列化保存为 `.pkl` 文件。 |

## 🔄 完整运作流程 (Pipeline Workflow)

```mermaid
graph TD
    subgraph "Phase 1: 离线学习 (Offline Learning)"
        A[原始文本 source_text.txt] --> B(预处理 & 分句)
        B --> C{构建训练集?}
        C -- Yes --> D[规则引擎标注 build_dataset.py]
        D --> E[银标准数据 train_data.json]
        E --> F[模型训练 train_model.py]
        F --> G[随机森林模型 relation_classifier.pkl]
    end

    subgraph "Phase 2: 在线抽取 (Online Extraction)"
        H[原始文本 source_text.txt] --> I(预处理 & 章节识别)
        I --> J[实体抽取 Entity Extraction]
        J --> K[特征提取 Feature Extraction]
        G -.-> L{加载模型?}
        K --> L
        L -- Yes (ML预测) --> M[模型分类]
        L -- No (规则兜底) --> N[规则匹配]
        M --> O[结果聚合]
        N --> O
        O --> P[输出 CSV (entity.csv, relation.csv)]
    end
```

### 流程详解

#### Phase 1: 离线学习 (Offline Learning)
目标：利用规则自动生成数据，训练一个泛化能力更强的分类器。

**Step 1.1: 银标准数据构建 (Silver Standard Construction)**
*   **脚本**: `src/build_dataset.py`
*   **核心逻辑**:
    1.  **预处理**: 调用 `nlp_core.TextPreprocessor` 清洗文本。
    2.  **实体抽取**: 调用 `entity_extraction.EntityExtractor` 提取实体。
    3.  **规则标注**: 调用 `relation_extraction.RelationExtractor` 的规则引擎自动识别高置信度关系。
    4.  **负采样**: 在同一句子中随机选取未被规则命中的实体对作为负样本。
*   **输出**: `data/processed/train_data.json`

**Step 1.2: 模型训练 (Model Training)**
*   **脚本**: `src/train_model.py`
*   **核心逻辑**:
    1.  **特征工程**: 调用 `features.FeatureExtractor` 提取词汇、句法和位置特征。
    2.  **向量化**: 使用 `DictVectorizer` 转换为数值向量。
    3.  **训练**: 训练 `RandomForestClassifier` 并进行分层采样评估。
*   **输出**: `models/relation_classifier.pkl`

#### Phase 2: 在线抽取 (Online Extraction)
目标：对新文本进行全量抽取，预测隐含关系。

**Step 2.1: 管道初始化与预处理**
*   **模块**: `src/pipeline.py`
*   **逻辑**: 加载配置好的 `nlp_core` 模型，识别章节标题（如 "# 第六章 排序"）作为全局上下文。

**Step 2.2: 实体抽取与优化**
*   **模块**: `src/entity_extraction.py`
*   **逻辑**: 结合词典匹配与 NER，执行长词优先过滤，解决实体碎片化问题。

**Step 2.3: 关系预测与导出**
*   **模块**: `src/relation_extraction.py`
*   **逻辑**: 
    1.  **上下文默认关系**: 自动建立实体与章节主题的“属于”关系。
    2.  **ML 预测**: 提取特征并输入随机森林模型。
    3.  **规则兜底**: 若模型缺失则回退至依存句法匹配。
*   **输出**: `data/output/` 下的 `entity.csv` 和 `relation.csv`。

## 🧠 机器学习实现细节

### 为什么使用“远程监督” (Distant Supervision)？
本项目采用了一种称为 **远程监督** 的策略：先用高置信度的规则（Teacher）自动生成训练数据，再用这些数据训练机器学习模型（Student）。

这样做有以下核心优势：

1.  **泛化能力 (Generalization)**：
    *   **规则是死板的**：规则通常基于严格的模式匹配（如正则表达式）。如果句子结构发生微小变化（如插入了修饰语），规则很容易失效。
    *   **模型是灵活的**：机器学习模型学习的是**特征**（如词性序列、依存距离、上下文关键词）。即使句子结构发生了规则未覆盖的变化，只要特征相似，模型依然能正确识别。

2.  **容错与概率 (Probability)**：
    *   规则只能给出“是”或“不是”的硬性判断。
    *   模型可以给出**概率分数 (Confidence Score)**，这对于处理模糊情况或解决冲突非常有价值。

3.  **系统演进 (Scalability)**：
    *   随着项目发展，维护复杂的规则集会变得越来越困难（“if-else 地狱”）。
    *   通过这种方式，我们只需不断优化数据生成逻辑或添加更多高质量样本，重新训练模型即可获得性能提升，而无需修改核心预测代码。

### 样本定义：正样本 vs 负样本 (Samples)

在构建训练集（`build_dataset.py`）时，系统会自动生成两类样本：

1.  **正样本 (Positive Samples)**：
    *   **定义**：确实存在预设关系（如“属于”、“包含”）的实体对。
    *   **来源**：由规则引擎根据句法结构和关键词自动判定。
    *   **作用**：教会模型识别关系的“正面特征”。
2.  **负样本 (Negative Samples)**：
    *   **定义**：出现在同一句中但**没有任何定义关系**的实体对。
    *   **来源**：通过“负采样”逻辑，选取未被规则命中的实体对，标记为 `"None"`。
    *   **作用**：防止模型“过度乐观”，教会模型识别“无关系”的情况，降低误报率。

> [!TIP]
> 为了保证模型的辨别能力，本项目在生成数据时通常会保持正负样本约 **1:3** 的比例。

### 模型选型：为什么选择随机森林？(Why Random Forest?)

在数据量较小（<1000）且依赖人工特征工程的场景下，**随机森林 (Random Forest)** 是性价比最高的选择，主要基于以下考量：

1.  **极佳的抗过拟合能力 (Robustness)**：
    *   我们的训练数据非常少（约 530 条）。深度学习模型（如 BERT）极易过拟合，而随机森林通过“集成学习”（投票机制）能有效降低方差，保证泛化能力。
2.  **擅长处理高维稀疏特征 (High Dimensionality)**：
    *   `DictVectorizer` 产生的特征空间高达数千维且稀疏。随机森林能自动选择对分类最有用的特征子集，忽略噪声。
3.  **天然支持多分类 (Multiclass Support)**：
    *   无需像 SVM 那样使用 One-vs-Rest 策略，直接支持 5 种关系类别的同时预测。
4.  **可解释性 (Interpretability)**：
    *   可以输出 **Feature Importance**，让我们直观看到哪些特征（如“依存距离”）对判断关系最重要，便于教学和调试。

### 技术流程优化 (Engineering)

| 优化措施         | 问题现象 (Why)              | 解决方案原理 (How)                                           |
| :--------------- | :-------------------------- | :----------------------------------------------------------- |
| **模块化重构**   | 代码耦合度高，存在重复逻辑。 | **解耦设计**：将功能拆分为 nlp_core, features 等 5 个独立模块，提高可维护性。 |
| **分词修复**     | 出现 "循环/队" 等碎片实体。 | **Jieba 集成**：替换 spaCy 默认分词器，并加载领域词典，确保术语不被切碎。 |
| **标签去重**     | 同一实体对有冲突关系。      | **优先级仲裁**：定义标签优先级（属于 > 包含），冲突时保留高优先级标签。 |
| **同义词归一化** | "enqueue" 和 "入队" 并在。  | **映射清洗**：预处理阶段统一转换为标准中文术语。             |
| **分层采样**     | 稀有类别 Recall 为 0。      | **Stratified Sampling**：强制训练集和测试集保持相同的类别分布比例。 |
| **上下文感知**   | 缺失跨句子层级关系。        | **Context-Awareness**：解析章节标题作为全局上下文，自动建立"属于"关系。 |

## 🔍 规则引擎实现原理 (Rule Engine)

规则引擎是本项目的“老师”，负责在离线阶段生成高置信度的训练数据。它主要基于以下两种机制：

### 1. 基于依存句法分析 (Dependency Parsing)
利用 spaCy 的句法分析能力，识别句子中实体间的结构化联系：
*   **主谓宾识别**：如果两个实体通过动词（如“包含”、“属于”、“实现”）连接，且符合主谓宾（nsubj/obj）结构，则提取关系。
*   **介词短语识别**：识别如“...应用于...”等复杂的介词结构。

### 2. 基于模式匹配 (Pattern Matching)
利用正则表达式和关键词库捕捉显式的描述性文字：
*   **关键词库**：内置了针对“属于”、“包含”、“实现方式”、“应用场景”等关系的专业关键词。
*   **正则匹配**：通过 `实体1 + 关键词 + 实体2` 的模式进行快速扫描。

> [!NOTE]
> 规则引擎的完整实现位于 `src/relation_extraction.py` 的 `_extract_by_rules` 方法中。

## 💡 关键技术释疑 (Technical Q&A)

**Q1: 既然使用了 Jieba 分词，为什么还要加载 spaCy 模型 (`zh_core_web_sm`)？**

> **A**: 我们需要区分 **分词器 (Tokenizer)** 和 **语言模型 (Language Model)**。
>
> *   **Jieba** 仅负责将句子切分为单词列表（如 `["数据结构", "是", "核心", "课程"]`），它擅长处理中文专业术语，但不懂语法。
> *   **spaCy 模型** 接收 Jieba 切分好的词，进行深层语法分析：
>     *   **词性标注 (POS)**：识别 "是" 为动词 (VERB)。
>     *   **依存句法 (Dependency)**：识别 "数据结构" 是 "是" 的主语 (nsubj)。
>     *   **实体识别 (NER)**：识别 "计算机科学" 为实体。
>
> 因此，**Jieba 是“刀”，spaCy 是“脑”**，两者结合才能实现精准抽取。

**Q2: 为什么构建数据时提示“正在禁用已加载的机器学习模型”？**

> **A**: 这是为了防止数据泄露和循环验证。
>
> *   在 `build_dataset.py` 中，我们的目标是利用**规则引擎（老师）**来生成训练数据。
> *   如果此时使用了**机器学习模型（学生）**来生成数据，就变成了“学生自己出题自己做”，失去了监督学习的意义。
> *   因此，我们在生成“银标准”数据时，强制禁用了 `relation_classifier.pkl`，确保训练集纯粹源自高置信度的规则。
