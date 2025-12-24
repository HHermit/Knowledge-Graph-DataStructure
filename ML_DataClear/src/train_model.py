import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from src.features import FeatureExtractor

def train_model(data_path, model_path):
    """
    训练关系分类模型
    """
    print("正在加载训练数据...")
    with open(data_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # 初始化特征提取器 (内部已集成 Jieba 和领域词典)
    extractor = FeatureExtractor()
    
    X_dicts = [] 
    y = []       
    
    print("正在提取特征...")
    for item in raw_data:
        feats = extractor.extract_features(item["entity1"], item["entity2"], item["sentence"])
        if feats:
            X_dicts.append(feats)
            y.append(item["label"])
            
    vectorizer = DictVectorizer(sparse=False)
    X = vectorizer.fit_transform(X_dicts)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
    
    print("正在训练随机森林分类器...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # --- 模型评估 ---
    print("\n模型评估报告:")
    y_pred = clf.predict(X_test)
    
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    df_report = pd.DataFrame(report_dict).transpose()
    
    print("-" * 60)
    print("指标解释:")
    print("  Precision (查准率): 预测为该类别的样本中，真正属于该类别的比例。")
    print("  Recall    (查全率): 真实为该类别的样本中，被正确预测出来的比例。")
    print("  F1-score  (综合分): Precision 和 Recall 的调和平均数。")
    print("  Support   (样本数): 测试集中该类别的真实样本数量。")
    print("  Accuracy  (准确率): 所有样本中预测正确的比例。")
    print("  Macro avg (宏平均): 所有类别指标的算术平均值（不考虑样本量），反映对少数类的关注度。")
    print("  Weighted avg (加权平均): 按样本量加权的平均值，反映整体性能。")
    print("-" * 60)
    
    print(df_report)
    print("-" * 60)
    
    joblib.dump((clf, vectorizer), model_path)
    print(f"模型已保存至: {model_path}")

if __name__ == "__main__":
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
    
    DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "train_data.json")
    MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "relation_classifier.pkl")
    
    train_model(DATA_PATH, MODEL_PATH)
