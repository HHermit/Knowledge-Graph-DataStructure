import os
import re
import joblib
from typing import List, Tuple
from src.features import FeatureExtractor

class RelationExtractor:
    """
    关系抽取类：利用机器学习模型进行预测，规则作为辅助。
    """
    def __init__(self, model_path=None, nlp=None):
        self.feature_extractor = FeatureExtractor(nlp=nlp)
        self.model = None
        self.vectorizer = None
        
        if model_path is None:
            CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
            PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
            model_path = os.path.join(PROJECT_ROOT, "models", "relation_classifier.pkl")
        
        if os.path.exists(model_path):
            print(f"正在加载机器学习模型: {model_path}")
            self.model, self.vectorizer = joblib.load(model_path)
        else:
            print(f"未找到模型文件 ({model_path})，将仅使用规则提取。")

        self.relation_keywords = {
            "包含": ["包括", "包含", "分为", "组成", "构成", "由", "涵盖"],
            "属于": ["是", "属于", "是一种", "遵循", "归为"],
            "实现方式": ["实现", "采用", "使用", "基于"],
            "应用场景": ["应用", "用于", "场景"]
        }
        
    def extract(self, doc, known_entities: List[str] = None) -> List[Tuple[str, str, str]]:
        """结合 ML 模型预测和规则匹配进行关系抽取"""
        triples = []
        
        if self.model and known_entities:
            for e1 in known_entities:
                for e2 in known_entities:
                    if e1 == e2: continue
                    if e1 not in doc.text or e2 not in doc.text: continue
                    
                    feats = self.feature_extractor.extract_features(e1, e2, doc.text)
                    if not feats: continue
                    
                    X = self.vectorizer.transform([feats])
                    pred_label = self.model.predict(X)[0]
                    
                    if pred_label != "None":
                        triples.append((e1, e2, pred_label))
                        
        if not self.model:
            triples.extend(self._extract_by_rules(doc, known_entities))

        return list(set(triples))

    def _extract_by_rules(self, doc, known_entities):
        """基于规则的抽取逻辑"""
        triples = []
        for token in doc:
            if token.pos_ == "VERB" or self._get_relation_type(token.text):
                rel_type = self._get_relation_type(token.text)
                if not rel_type: continue
                
                subjects = [child for child in token.children if child.dep_ in ["nsubj", "top", "nsubj:pass"]]
                objects = [child for child in token.children if child.dep_ in ["obj", "attr", "range", "dobj"]]
                
                extended_subjects = []
                for s in subjects:
                    extended_subjects.append(s)
                    self._get_conjunctions(s, extended_subjects)
                    
                extended_objects = []
                for o in objects:
                    extended_objects.append(o)
                    self._get_conjunctions(o, extended_objects)
                    modifiers = self._get_modifiers(o)
                    for mod in modifiers:
                        extended_objects.append(mod)
                
                for s in extended_subjects:
                    for o in extended_objects:
                        if s == o: continue
                        if known_entities and (s.text not in known_entities or o.text not in known_entities):
                            continue
                        triples.append((s.text, o.text, rel_type))

        if known_entities:
            text = doc.text
            for rel, keywords in self.relation_keywords.items():
                for kw in keywords:
                    for s_ent in known_entities:
                        if s_ent not in text: continue
                        for o_ent in known_entities:
                            if s_ent == o_ent or o_ent not in text: continue
                            pattern = rf"{re.escape(s_ent)}.*?{re.escape(kw)}.*?{re.escape(o_ent)}"
                            if re.search(pattern, text):
                                triples.append((s_ent, o_ent, rel))
                                
        return triples

    def _get_conjunctions(self, token, result_list):
        for child in token.children:
            if child.dep_ == "conj":
                result_list.append(child)
                self._get_conjunctions(child, result_list)

    def _get_modifiers(self, token):
        modifiers = []
        for child in token.children:
            if child.dep_ in ["nmod:assmod", "nmod", "amod", "compound"]:
                modifiers.append(child)
                modifiers.extend(self._get_modifiers(child))
        return modifiers

    def _get_relation_type(self, word: str) -> str:
        for rel, keywords in self.relation_keywords.items():
            if any(k in word for k in keywords):
                return rel
        return None
