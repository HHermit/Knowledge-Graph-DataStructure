"""
应用配置模块
包含 Neo4j 数据库连接配置和其他应用设置
"""
import os

class Config:
    """应用配置类"""
    # Neo4j 连接配置
    # 优先从环境变量获取，如果没有则使用默认值
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")      # 数据库连接地址
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")                    # 数据库用户名
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4jDatabase")    # 数据库密码
    
    # Flask 配置
    DEBUG = True
    PORT = 5000
    
    # 数据文件路径配置
    # os.path.dirname(__file__) 获取当前文件所在目录
    # os.path.dirname(...) 获取上一级目录 (backend)
    # os.path.join(..., 'data') 拼接 data 目录路径
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    ENTITY_FILE = os.path.join(DATA_DIR, 'entity.csv')      # 实体数据文件
    RELATION_FILE = os.path.join(DATA_DIR, 'relation.csv')  # 关系数据文件
