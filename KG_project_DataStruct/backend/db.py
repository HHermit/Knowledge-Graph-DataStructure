"""
数据库连接模块
使用单例模式管理 Neo4j 数据库连接
"""
from neo4j import GraphDatabase
from config import Config


class Neo4jConnection:
    """Neo4j 数据库连接单例类"""
    _instance = None

    def __new__(cls):
        """
        实现单例模式，确保整个应用只创建一个数据库驱动实例
        """
        if cls._instance is None:
            cls._instance = super(Neo4jConnection, cls).__new__(cls)
            # 初始化 Neo4j 驱动
            cls._instance.driver = GraphDatabase.driver(
                Config.NEO4J_URI,
                auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
            )
        return cls._instance

    def close(self):
        """关闭数据库连接，释放资源"""
        if self.driver:
            self.driver.close()

    def get_session(self):
        """
        获取一个新的数据库会话 (Session)
        注意：使用完 session 后必须关闭 (session.close())
        """
        return self.driver.session()


# 全局数据库实例
db = Neo4jConnection()
