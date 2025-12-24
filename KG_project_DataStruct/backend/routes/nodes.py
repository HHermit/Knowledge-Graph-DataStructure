"""
节点 CRUD 路由模块
包含创建、更新、删除节点及属性的接口
"""
from flask import jsonify, request
from routes import api_bp
from db import db


@api_bp.route('/node', methods=['POST'])
def create_node():
    """
    创建节点
    请求体: { name: string, label: string, properties: dict }
    """
    data = request.json
    name = data.get('name')
    label = data.get('label')
    properties = data.get('properties', {})
    
    if not name:
        return jsonify({"error": "Missing name"}), 400
        
    session = db.get_session()
    try:
        # 获取最大 ID 以自增
        result = session.run("MATCH (n) RETURN max(n.id) as max_id")
        max_id = result.single()['max_id']
        new_id = (max_id or 0) + 1
        
        # 确保 id 和 name 在属性中
        properties['id'] = new_id
        properties['name'] = name
        
        # 根据是否有标签构建不同的 Cypher 语句
        # 根据是否有标签构建不同的 Cypher 语句
        # 动态插入标签 (注意: 标签不能作为参数传递，只能拼接到 Cypher 字符串中)
        if label:
            cypher = f"CREATE (n:`{label}`) SET n = $props RETURN n"
        else:
            cypher = "CREATE (n) SET n = $props RETURN n"
            
        session.run(cypher, props=properties)
        
        return jsonify({"message": "Node created", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@api_bp.route('/node/<int:node_id>', methods=['PUT'])
def update_node(node_id):
    """
    更新节点名称 (保留此接口以兼容旧前端，实际建议使用属性更新接口)
    请求体: { name: string }
    """
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({"error": "Missing name"}), 400
        
    session = db.get_session()
    try:
        # 更新节点名称
        session.run("""
            MATCH (n) WHERE n.id = $id
            SET n.name = $name
            RETURN n
        """, id=node_id, name=name)
        
        return jsonify({"message": "Node updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@api_bp.route('/node/<int:node_id>', methods=['DELETE'])
def delete_node(node_id):
    """
    删除节点
    """
    session = db.get_session()
    try:
        # 删除节点及其所有关系 (DETACH DELETE)
        session.run("""
            MATCH (n) WHERE n.id = $id
            DETACH DELETE n
        """, id=node_id)
        
        return jsonify({"message": "Node deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@api_bp.route('/node/<int:node_id>/label', methods=['POST'])
def add_label(node_id):
    """
    给节点添加标签
    """
    data = request.json
    label = data.get('label')
    
    if not label:
        return jsonify({"error": "Missing label"}), 400
    
    label = label.strip().replace(' ', '_')
    
    session = db.get_session()
    try:
        # 给节点添加标签
        # SET n:`{label}`
        cypher = f"""
            MATCH (n) WHERE n.id = $id
            SET n:`{label}`
            RETURN n
        """
        result = session.run(cypher, id=node_id)
        
        if result.single():
            return jsonify({"message": f"Label '{label}' added"}), 200
        else:
            return jsonify({"error": "Node not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@api_bp.route('/node/<int:node_id>/label/<label_name>', methods=['DELETE'])
def remove_label(node_id, label_name):
    """
    移除节点的标签
    """
    session = db.get_session()
    try:
        # 移除节点标签
        # REMOVE n:`{label_name}`
        cypher = f"""
            MATCH (n) WHERE n.id = $id
            REMOVE n:`{label_name}`
            RETURN n
        """
        result = session.run(cypher, id=node_id)
        
        if result.single():
            return jsonify({"message": f"Label '{label_name}' removed"}), 200
        else:
            return jsonify({"error": "Node not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@api_bp.route('/node/<int:node_id>/property', methods=['PUT'])
def update_node_property(node_id):
    """
    更新或添加节点属性
    请求体: { key: string, value: any }
    """
    data = request.json
    key = data.get('key')
    value = data.get('value')
    
    if not key:
        return jsonify({"error": "Missing key"}), 400
        
    if key == 'id':
        return jsonify({"error": "Cannot modify ID"}), 400
        
    session = db.get_session()
    try:
        # 使用 += 动态设置属性
        # 注意：这里我们只设置一个属性，但为了安全使用参数化
        # 由于 Cypher 不能动态设置属性名（作为参数），我们需要构建查询字符串
        # 但要确保 key 是安全的。这里简单假设 key 是合法的标识符
        # 更安全的方法是使用 map projection 或 APOC
        
        # 简单防注入检查
        if not key.isidentifier():
             return jsonify({"error": "Invalid property key"}), 400

        # 动态设置属性
        # SET n.{key} = $value
        cypher = f"""
            MATCH (n) WHERE n.id = $id
            SET n.{key} = $value
            RETURN n
        """
        result = session.run(cypher, id=node_id, value=value)
        
        if result.single():
            return jsonify({"message": f"Property '{key}' updated"}), 200
        else:
            return jsonify({"error": "Node not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@api_bp.route('/node/<int:node_id>/property/<key>', methods=['DELETE'])
def delete_node_property(node_id, key):
    """
    删除节点属性
    """
    if key in ['id', 'name']:
        return jsonify({"error": "Cannot delete required property"}), 400
        
    if not key.isidentifier():
         return jsonify({"error": "Invalid property key"}), 400

    session = db.get_session()
    try:
        # 删除节点属性
        # REMOVE n.{key}
        cypher = f"""
            MATCH (n) WHERE n.id = $id
            REMOVE n.{key}
            RETURN n
        """
        result = session.run(cypher, id=node_id)
        
        if result.single():
            return jsonify({"message": f"Property '{key}' deleted"}), 200
        else:
            return jsonify({"error": "Node not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
