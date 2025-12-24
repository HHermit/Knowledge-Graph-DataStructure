import os
import json
import spacy
from src.pipeline import KnowledgeExtractorPipeline

def build_dataset(input_path, output_path):
    """
    构建关系分类训练数据集
    """
    # 初始化管道（复用其分词和实体抽取能力）
    pipeline = KnowledgeExtractorPipeline()
    
    print(f"正在读取源文本: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    dataset = []
    
    print("正在生成训练样本...")
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"): continue
        
        clean_text = pipeline.preprocessor.clean(line)
        sentences = pipeline.preprocessor.split_sentences(clean_text)
        
        for sent in sentences:
            doc = pipeline.nlp(sent)
            entities = pipeline.entity_extractor.extract(doc)
            
            if len(entities) < 2: continue
            
            # 实体合并以便于规则匹配
            with doc.retokenize() as retokenizer:
                matches = pipeline.entity_extractor.matcher(doc)
                spans = spacy.util.filter_spans([doc[start:end] for _, start, end in matches])
                for span in spans:
                    retokenizer.merge(span)
            
            # 利用规则引擎生成正样本
            pos_triples = pipeline.relation_extractor._extract_by_rules(doc, entities)
            
            # 记录已有的实体对，用于负采样
            pos_pairs = set()
            for s, o, r in pos_triples:
                dataset.append({
                    "sentence": sent,
                    "entity1": s,
                    "entity2": o,
                    "label": r
                })
                pos_pairs.add((s, o))
            
            # 负采样：在同一句子中随机选取没有关系的实体对
            for e1 in entities:
                for e2 in entities:
                    if e1 == e2: continue
                    if (e1, e2) not in pos_pairs:
                        # 只有当 e1 和 e2 都在句子中时才添加
                        if e1 in sent and e2 in sent:
                            dataset.append({
                                "sentence": sent,
                                "entity1": e1,
                                "entity2": e2,
                                "label": "None"
                            })
                            
    # 标签优先级仲裁 (去重)
    final_dataset = []
    seen_pairs = {} # (sent, e1, e2) -> label
    
    label_priority = {"属于": 4, "实现方式": 3, "应用场景": 2, "包含": 1, "None": 0}
    
    for item in dataset:
        key = (item["sentence"], item["entity1"], item["entity2"])
        if key not in seen_pairs:
            seen_pairs[key] = item["label"]
        else:
            # 如果存在冲突，保留高优先级标签
            if label_priority.get(item["label"], 0) > label_priority.get(seen_pairs[key], 0):
                seen_pairs[key] = item["label"]
                
    for (s, e1, e2), l in seen_pairs.items():
        final_dataset.append({"sentence": s, "entity1": e1, "entity2": e2, "label": l})
        
    print(f"数据集构建完成，共 {len(final_dataset)} 条样本。")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)
    print(f"训练数据已保存至: {output_path}")

if __name__ == "__main__":
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
    
    INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "source_text.txt")
    OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "train_data.json")
    
    build_dataset(INPUT_FILE, OUTPUT_FILE)
