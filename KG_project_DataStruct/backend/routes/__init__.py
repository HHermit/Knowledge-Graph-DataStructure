"""
路由模块包
将所有 API 路由组织在子模块中
"""
from flask import Blueprint

# 创建主 API Blueprint
api_bp = Blueprint('api', __name__)

# 导入各子模块的路由 (必须在 Blueprint 创建之后)
from routes import graph, nodes, relationships, data
