"""
Flask 应用入口
"""
# 导入 Flask 框架
from flask import Flask
# 导入 CORS 扩展，用于解决跨域问题
from flask_cors import CORS
# 导入 API 路由蓝图
from routes import api_bp
# 导入配置类
from config import Config

# 创建 Flask 应用实例
app = Flask(__name__)

# 启用 CORS，允许所有来源访问 API (生产环境应限制来源)
CORS(app)

# 注册 API Blueprint
# url_prefix='/api' 表示所有路由都以 /api 开头，例如 /api/graph
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    # 启动 Flask 开发服务器
    # debug=True: 代码修改后自动重启
    # port: 指定运行端口
    app.run(debug=Config.DEBUG, port=Config.PORT)
