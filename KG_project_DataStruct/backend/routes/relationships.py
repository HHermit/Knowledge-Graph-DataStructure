"""
关系 CRUD 路由模块
包含创建、删除关系及属性的接口
"""
from flask import jsonify, request
from routes import api_bp
from db import db


@api_bp.route('/relationship', methods=['POST'])
def create_relationship():
    """
    创建关系
    请求体: { source_id: int, target_id: int, type: string, properties: dict }
    """
    data = request.json
    source_id = data.get('source_id')
    target_id = data.get('target_id')
    rel_type = data.get('type')
    properties = data.get('properties', {})
    
    if not source_id or not target_id or not rel_type:
        return jsonify({"error": "Missing parameters"}), 400
        
    session = db.get_session()
    try:
        # 使用 MERGE 避免创建重复关系
        # MATCH 查找两个端点
        # MERGE (a)-[r]->(b) 如果关系不存在则创建，存在则匹配
        # SET r += $props 更新或设置属性
        cypher = f"""
            MATCH (a), (b)
            WHERE a.id = $source_id AND b.id = $target_id
            MERGE (a)-[r:`{rel_type}`]->(b)
            SET r += $props
            RETURN r
        """
        session.run(cypher, source_id=int(source_id), target_id=int(target_id), props=properties)
        
        return jsonify({"message": "Relationship created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@api_bp.route('/relationship', methods=['DELETE'])
def delete_relationship():
    """
    删除关系
    参数: source_id, target_id, type (可选)
    """
    source_id = request.args.get('source_id')
    target_id = request.args.get('target_id')
    rel_type = request.args.get('type')
    
    if not source_id or not target_id:
        return jsonify({"error": "Missing source or target id"}), 400
        
    session = db.get_session()
    try:
        if rel_type:
            # 如果指定了关系类型，只删除特定类型的关系
            cypher = f"""
                MATCH (a)-[r:`{rel_type}`]->(b)
                WHERE a.id = $source_id AND b.id = $target_id
                DELETE r
            """
        else:
            # 如果未指定类型，删除两个节点间的所有关系
            cypher = """
                MATCH (a)-[r]->(b)
                WHERE a.id = $source_id AND b.id = $target_id
                DELETE r
            """
            
        session.run(cypher, source_id=int(source_id), target_id=int(target_id))
        
        return jsonify({"message": "Relationship deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@api_bp.route('/relationship/property', methods=['PUT'])
def update_relationship_property():
    """
    更新关系属性
    请求体: { source_id, target_id, type, key, value }
    """
    data = request.json
    source_id = data.get('source_id')
    target_id = data.get('target_id')
    rel_type = data.get('type')
    key = data.get('key')
    value = data.get('value')
    
    if not all([source_id, target_id, rel_type, key]):
        return jsonify({"error": "Missing parameters"}), 400
        
    if not key.isidentifier():
        return jsonify({"error": "Invalid property key"}), 400
        
    session = db.get_session()
    try:
        # 更新关系属性
        # SET r.{key} = $value
        cypher = f"""
            MATCH (a)-[r:`{rel_type}`]->(b)
            WHERE a.id = $source_id AND b.id = $target_id
            SET r.{key} = $value
            RETURN r
        """
        result = session.run(cypher, source_id=int(source_id), target_id=int(target_id), value=value)
        
        if result.single():
            return jsonify({"message": f"Property '{key}' updated"}), 200
        else:
            return jsonify({"error": "Relationship not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@api_bp.route('/relationship/property', methods=['DELETE'])
def delete_relationship_property():
    """
    删除关系属性
    参数: source_id, target_id, type, key
    """
    source_id = request.args.get('source_id')
    target_id = request.args.get('target_id')
    rel_type = request.args.get('type')
    key = request.args.get('key')
    
    if not all([source_id, target_id, rel_type, key]):
        return jsonify({"error": "Missing parameters"}), 400
        
    if not key.isidentifier():
        return jsonify({"error": "Invalid property key"}), 400
        
    session = db.get_session()
    try:
        # 删除关系属性
        # REMOVE r.{key}
        cypher = f"""
            MATCH (a)-[r:`{rel_type}`]->(b)
            WHERE a.id = $source_id AND b.id = $target_id
            REMOVE r.{key}
            RETURN r
        """
        result = session.run(cypher, source_id=int(source_id), target_id=int(target_id))
        
        if result.single():
            return jsonify({"message": f"Property '{key}' deleted"}), 200
        else:
            return jsonify({"error": "Relationship not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
