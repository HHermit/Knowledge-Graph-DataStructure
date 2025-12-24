import os
from src.pipeline import KnowledgeExtractorPipeline

if __name__ == "__main__":
    # 获取当前脚本所在目录 (src)
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录 (ML_DataClear)
    PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
    
    # 配置输入输出路径 (使用绝对路径)
    INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "source_text.txt")
    VOCAB_FILE = os.path.join(PROJECT_ROOT, "data", "config", "domain_vocab.txt")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "output")
    
    # 初始化并运行管道
    pipeline = KnowledgeExtractorPipeline(vocab_path=VOCAB_FILE)
    pipeline.run(INPUT_FILE, OUTPUT_DIR)
