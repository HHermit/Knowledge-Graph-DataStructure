import os
import re
import spacy
import jieba
from typing import List

class JiebaTokenizer:
    """
    自定义 Jieba 分词器，适配 spaCy 接口。
    """
    def __init__(self, vocab):
        self.vocab = vocab

    def __call__(self, text):
        # 使用 jieba 进行分词
        words = list(jieba.cut(text))
        # 创建 spaCy Doc 对象
        return spacy.tokens.Doc(self.vocab, words=words, spaces=[False] * len(words))

class TextPreprocessor:
    """
    文本预处理类：负责清洗原始文本，分句处理。
    """
    def __init__(self):
        self.clean_patterns = [
            r'#.*',           # 匹配 Markdown 格式的标题
            r'第.*章.*',       # 匹配中文章节标题
            r'\[\d+\]',        # 匹配学术参考文献标注
            r'\s+',            # 匹配连续的多余空格
        ]

    def clean(self, text: str) -> str:
        """进行基本文本清洗和同义词归一化"""
        synonym_map = {
            "enqueue": "入队",
            "dequeue": "出队",
            "push": "入栈",
            "pop": "出栈",
            "LIFO": "后进先出",
            "FIFO": "先进先出"
        }
        for src, dst in synonym_map.items():
            text = re.sub(re.escape(src), dst, text, flags=re.IGNORECASE)

        for pattern in self.clean_patterns:
            text = re.sub(pattern, ' ', text)
        return text.strip()

    def split_sentences(self, text: str) -> List[str]:
        """将长文本切分为句子"""
        sentences = re.split(r'[。！？；]', text)
        return [s.strip() for s in sentences if len(s.strip()) > 1]

def load_spacy_model(model_name="zh_core_web_sm", vocab_path=None):
    """
    加载并配置 spaCy 模型（集成 Jieba 分词器）
    """
    if vocab_path is None:
        # 尝试定位默认词典路径
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
        default_vocab = os.path.join(PROJECT_ROOT, "data", "config", "domain_vocab.txt")
        if os.path.exists(default_vocab):
            vocab_path = default_vocab

    print(f"正在加载模型 {model_name}...")
    try:
        nlp = spacy.load(model_name)
        # 替换分词器
        nlp.tokenizer = JiebaTokenizer(nlp.vocab)
        print("已启用 Jieba 分词器。")
        
        # 加载领域词典到 jieba
        if vocab_path and os.path.exists(vocab_path):
            print(f"正在加载领域词典: {vocab_path}")
            with open(vocab_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word and not word.startswith('#'):
                        jieba.add_word(word)
            print("领域词典已加载。")
        return nlp
    except OSError:
        print(f"模型 {model_name} 未找到，请运行: python -m spacy download {model_name}")
        raise
