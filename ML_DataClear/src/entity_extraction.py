import os
from spacy.matcher import PhraseMatcher
from typing import List

class EntityExtractor:
    """
    实体抽取类：识别专业术语。
    """
    def __init__(self, nlp, vocab_path: str):
        self.nlp = nlp
        self.matcher = PhraseMatcher(nlp.vocab)
        self.load_vocab(vocab_path)

    def load_vocab(self, path: str):
        """加载领域词典"""
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                terms = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                self.vocab_terms = set(terms)
                patterns = [self.nlp.make_doc(text) for text in terms]
                self.matcher.add("DOMAIN_TERM", patterns)

    def extract(self, doc) -> List[str]:
        """提取实体并进行长词优先过滤"""
        raw_entities = set()
        stop_fragments = ["性表", "表是", "列是", "之一", "方式", "实现", "节点", "元素", "操作", "应用", "场景", "内容", "策略", "解决", "冲突"]
        
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            raw_entities.add(doc[start:end].text)
            
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 1:
                if token.text not in stop_fragments:
                    raw_entities.add(token.text)
        
        sorted_entities = sorted(list(raw_entities), key=len, reverse=True)
        final_entities = []
        for i, entity in enumerate(sorted_entities):
            is_sub = False
            for other in sorted_entities[:i]:
                if entity in other:
                    if hasattr(self, 'vocab_terms') and entity in self.vocab_terms:
                        is_sub = False
                    else:
                        is_sub = True
                    break
            
            if not is_sub and hasattr(self, 'vocab_terms'):
                if entity not in self.vocab_terms:
                    for term in self.vocab_terms:
                        if entity in term and entity != term:
                            is_sub = True
                            break
            
            if not is_sub:
                final_entities.append(entity)
                
        return final_entities
