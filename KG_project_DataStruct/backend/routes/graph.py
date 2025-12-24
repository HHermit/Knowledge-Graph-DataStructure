"""
图查询路由模块
包含获取图数据、搜索节点、路径查询等接口
"""
from flask import jsonify, request
from routes import api_bp
from db import db


@api_bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return jsonify({"message": "Backend is running!"})


@api_bp.route('/graph', methods=['GET'])
def get_graph():
    """
    获取全图数据
    返回所有节点和关系，包括所有属性
    """
    session = db.get_session()
    try:
        nodes = {}
        links = []
        
        # 1. 获取所有节点及其属性
        # MATCH (n) 匹配所有节点
        # labels(n) 获取节点的标签列表
        all_nodes_result = session.run("""
            MATCH (n)
            RETURN n, labels(n) as labels
        """)
        
        for record in all_nodes_result:
            n = record['n']
            n_id = n.get('id')
            if n_id not in nodes:
                labels = list(record['labels'])
                # 将节点对象转换为字典，包含所有属性
                props = dict(n)
                
                nodes[n_id] = {
                    "id": n_id,
                    "name": n.get('name'),
                    "category": labels[0] if labels else None,
                    "labels": labels,
                    "properties": props # 包含所有属性
                }
        
        # 2. 获取所有关系及其属性
        # MATCH (n)-[r]->(m) 匹配所有有向关系
        # LIMIT 500 限制返回数量，防止数据量过大导致前端卡顿
        rels_result = session.run("""
            MATCH (n)-[r]->(m)
            RETURN n.id as source_id, m.id as target_id, type(r) as rel_type, properties(r) as props
            LIMIT 500
        """)
        
        for record in rels_result:
            links.append({
                "source": record['source_id'],
                "target": record['target_id'],
                "name": record['rel_type'],
                "properties": record['props'] # 包含关系属性
            })
            
        return jsonify({"nodes": list(nodes.values()), "links": links})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@api_bp.route('/search', methods=['GET'])
def search_node():
    """
    搜索节点
    """
    query = request.args.get('q', '')
    session = db.get_session()
    try:
        # 使用 CONTAINS 进行模糊搜索 (不区分大小写)
        # toLower() 将名称和查询词都转换为小写
        result = session.run("""
            MATCH (n)
            WHERE toLower(n.name) CONTAINS toLower($term)
            RETURN n, labels(n) as labels
            LIMIT 10
        """, term=query)
        
        nodes = []
        for record in result:
            n = record['n']
            labels = list(record['labels'])
            nodes.append({
                "id": n.get('id'),
                "name": n.get('name'),
                "category": labels[0] if labels else None,
                "labels": labels,
                "properties": dict(n)
            })
            
        return jsonify(nodes)
    finally:
        session.close()


@api_bp.route('/path', methods=['GET'])
def shortest_path():
    """
    最短路径查询
    """
    start = request.args.get('start')
    end = request.args.get('end')
    
    if not start or not end:
        return jsonify({"error": "Missing start or end parameters"}), 400
        
    session = db.get_session()
    try:
        # 解析 ID 或名称
        try:
            start_id = int(start)
            start_condition = "start.id = $start_val"
        except ValueError:
            start_id = None
            start_condition = "toLower(start.name) = toLower($start_val)"
        
        try:
            end_id = int(end)
            end_condition = "end.id = $end_val"
        except ValueError:
            end_id = None
            end_condition = "toLower(end.name) = toLower($end_val)"
        
        # 构建查询语句
        # shortestPath((start)-[*]-(end)) 查找任意方向的最短路径
        # [*] 表示任意长度的路径
        query = f"""
            MATCH (start), (end)
            WHERE {start_condition} AND {end_condition}
            MATCH p = shortestPath((start)-[*]-(end))
            RETURN p
        """
        
        result = session.run(query, 
            start_val=start_id if start_id is not None else start,
            end_val=end_id if end_id is not None else end
        )
        
        record = result.single()
        if record:
            path = record['p']
            nodes = []
            for n in path.nodes:
                nodes.append({
                    "id": n.get('id'),
                    "name": n.get('name'),
                    "category": list(n.labels)[0] if n.labels else None,
                    "labels": list(n.labels),
                    "properties": dict(n)
                })
            return jsonify({"path": nodes})
        else:
            return jsonify({"message": "No path found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
