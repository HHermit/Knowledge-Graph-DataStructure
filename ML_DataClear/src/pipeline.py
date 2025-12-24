import os
import json
import re
import pandas as pd
import spacy
from src.nlp_core import load_spacy_model, TextPreprocessor
from src.entity_extraction import EntityExtractor
from src.relation_extraction import RelationExtractor

class KnowledgeExtractorPipeline:
    """
    知识抽取主管道：串联预处理、实体抽取、关系抽取和导出
    """
    def __init__(self, model_name="zh_core_web_sm", vocab_path=None):
        if vocab_path is None:
            CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
            PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
            vocab_path = os.path.join(PROJECT_ROOT, "data", "config", "domain_vocab.txt")
            
        # 加载配置好的 NLP 模型
        self.nlp = load_spacy_model(model_name, vocab_path)

        # 初始化各个组件
        self.preprocessor = TextPreprocessor()
        self.entity_extractor = EntityExtractor(self.nlp, vocab_path)
        self.relation_extractor = RelationExtractor(nlp=self.nlp)
        
        # 用于存储最终结果的数据结构
        self.entities_db = {} 
        self.relations_list = [] 

    def run(self, input_path: str, output_dir: str):
        """运行完整的抽取流程"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print(f"开始处理，共 {len(lines)} 行文本...")

        entity_id_counter = 1 
        all_found_entities = set()
        sentence_docs = [] 
        current_chapter = None 

        for line in lines:
            line = line.strip()
            if not line: continue
            
            if line.startswith("#") or (line.startswith("第") and "章" in line):
                topic = re.sub(r'[#\s]', '', line)
                topic = re.sub(r'第[一二三四五六七八九十0-9]+章', '', topic)
                if topic:
                    current_chapter = topic
                    print(f"检测到章节主题: {current_chapter}")
                continue

            clean_line = self.preprocessor.clean(line)
            sentences = self.preprocessor.split_sentences(clean_line)
            
            for sent in sentences:
                doc = self.nlp(sent)
                found_entities = self.entity_extractor.extract(doc)
                for ent_name in found_entities:
                    all_found_entities.add(ent_name)
                    if ent_name not in self.entities_db:
                        self.entities_db[ent_name] = {
                            "id": entity_id_counter,
                            "name": ent_name,
                            "labels": "知识点",
                            "properties": json.dumps({"source": "auto_extraction"})
                        }
                        entity_id_counter += 1

                with doc.retokenize() as retokenizer:
                    matches = self.entity_extractor.matcher(doc)
                    spans = spacy.util.filter_spans([doc[start:end] for _, start, end in matches])
                    for span in spans:
                        retokenizer.merge(span)
                
                sentence_docs.append((doc, current_chapter, found_entities))
            
        print(f"共识别到 {len(all_found_entities)} 个唯一实体。")

        for doc, chapter_topic, doc_entities in sentence_docs:
            found_relations = self.relation_extractor.extract(doc, list(all_found_entities))
            
            if chapter_topic:
                for ent in doc_entities:
                    if chapter_topic in ent and ent != chapter_topic:
                        is_exist = False
                        for s, o, r in found_relations:
                            if s == ent and o == chapter_topic:
                                is_exist = True
                                break
                        
                        if not is_exist:
                            if chapter_topic not in self.entities_db:
                                self.entities_db[chapter_topic] = {
                                    "id": entity_id_counter,
                                    "name": chapter_topic,
                                    "labels": "知识点",
                                    "properties": json.dumps({"source": "chapter_title"})
                                }
                                entity_id_counter += 1
                                all_found_entities.add(chapter_topic)
                            
                            found_relations.append((ent, chapter_topic, "属于"))

            for s, o, r in found_relations:
                if s in self.entities_db and o in self.entities_db:
                    self.relations_list.append({
                        "source_id": self.entities_db[s]["id"],
                        "target_id": self.entities_db[o]["id"],
                        "type": r,
                        "properties": json.dumps({})
                    })

        self._export(output_dir)
        print(f"抽取完成！结果已保存至 {output_dir}")

    def _export(self, output_dir: str):
        """将结果导出为 CSV 文件"""
        df_entities = pd.DataFrame(list(self.entities_db.values()))
        df_entities.to_csv(os.path.join(output_dir, "entity.csv"), index=False, encoding='utf-8-sig')
        
        df_relations = pd.DataFrame(self.relations_list)
        df_relations = df_relations.drop_duplicates()
        df_relations.to_csv(os.path.join(output_dir, "relation.csv"), index=False, encoding='utf-8-sig')
