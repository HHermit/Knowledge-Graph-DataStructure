import os
import spacy
from spacy.matcher import PhraseMatcher
from src.nlp_core import load_spacy_model

class FeatureExtractor:
    """
    特征提取器：将 (实体1, 实体2, 句子) 转换为特征向量。
    """
    def __init__(self, nlp=None):
        # 如果未传入 nlp 对象，则加载默认模型
        self.nlp = nlp if nlp else load_spacy_model()
        # 初始化一个临时的匹配器用于实体合并
        self.matcher = PhraseMatcher(self.nlp.vocab)

    def extract_features(self, e1, e2, sentence):
        """提取两个实体之间的关系特征"""
        doc = self.nlp(sentence)
        
        # [关键修复] 动态合并实体，确保 e1 和 e2 成为单个 Token
        # 否则依存分析和位置特征会出错
        if "TEMP_ENT" in self.matcher:
            self.matcher.remove("TEMP_ENT")
        self.matcher.add("TEMP_ENT", [self.nlp.make_doc(e1), self.nlp.make_doc(e2)])
        matches = self.matcher(doc)
        spans = spacy.util.filter_spans([doc[start:end] for _, start, end in matches])
        
        with doc.retokenize() as retokenizer:
            for span in spans:
                retokenizer.merge(span)
        
        # 重新定位实体在句子中的 Token 对象
        t1, t2 = None, None
        for token in doc:
            if token.text == e1: t1 = token
            if token.text == e2: t2 = token
        
        if not t1 or not t2:
            return {}

        features = {}
        features["e1_text"] = e1
        features["e2_text"] = e2
        features["e1_pos"] = t1.pos_
        features["e2_pos"] = t2.pos_
        features["token_distance"] = abs(t1.i - t2.i)
        features["is_adjacent"] = (features["token_distance"] == 1)
        
        lca = self._get_lca(t1, t2)
        if lca:
            features["lca_pos"] = lca.pos_
            features["lca_text"] = lca.text
            features["dist_to_lca_1"] = self._get_dep_dist(t1, lca)
            features["dist_to_lca_2"] = self._get_dep_dist(t2, lca)
        
        start, end = sorted([t1.i, t2.i])
        between_tokens = doc[start+1:end]
        
        features["has_include"] = any(w.text in ["包括", "包含", "分为"] for w in between_tokens)
        features["has_is"] = any(w.text in ["是", "属于", "是一种"] for w in between_tokens)
        features["has_implement"] = any(w.text in ["实现", "采用"] for w in between_tokens)
        
        return features

    def _get_lca(self, t1, t2):
        """计算最近公共祖先"""
        ancestors1 = set([t1] + list(t1.ancestors))
        for anc in [t2] + list(t2.ancestors):
            if anc in ancestors1:
                return anc
        return None

    def _get_dep_dist(self, t, ancestor):
        """计算依存路径距离"""
        dist = 0
        current = t
        while current != ancestor and current != current.head:
            current = current.head
            dist += 1
        return dist
