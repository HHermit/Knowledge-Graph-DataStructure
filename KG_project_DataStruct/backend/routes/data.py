"""
数据导入路由模块
包含数据库初始化和 CSV 数据导入功能
"""
import csv
import io
import os
import json
from flask import jsonify, request, send_file
from routes import api_bp
from db import db
from config import Config

# 数据文件目录
DATA_DIR = os.path.dirname(Config.ENTITY_FILE)

# 保存的检查点文件路径
SAVED_ENTITY_FILE = os.path.join(DATA_DIR, 'saved_entity.csv')
SAVED_RELATION_FILE = os.path.join(DATA_DIR, 'saved_relation.csv')

# 模板文件路径
ENTITY_TEMPLATE_FILE = os.path.join(DATA_DIR, 'entity_template.csv')
RELATION_TEMPLATE_FILE = os.path.join(DATA_DIR, 'relation_template.csv')


@api_bp.route('/template/entity', methods=['GET'])
def download_entity_template():
    """下载实体模板文件"""
    return send_file(ENTITY_TEMPLATE_FILE, as_attachment=True, download_name='entity_template.csv')


@api_bp.route('/template/relation', methods=['GET'])
def download_relation_template():
    """下载关系模板文件"""
    return send_file(RELATION_TEMPLATE_FILE, as_attachment=True, download_name='relation_template.csv')


@api_bp.route('/init', methods=['POST'])
def init_db():
    """
    初始化数据库（恢复到上次保存的状态）
    优先使用保存的检查点，否则使用原始文件
    """
    session = db.get_session()
    
    # 优先使用保存的文件
    entity_file = SAVED_ENTITY_FILE if os.path.exists(SAVED_ENTITY_FILE) else Config.ENTITY_FILE
    relation_file = SAVED_RELATION_FILE if os.path.exists(SAVED_RELATION_FILE) else Config.RELATION_FILE
    
    try:
        # 清空数据库
        # MATCH (n) DETACH DELETE n: 匹配所有节点 (n) 并删除它们，DETACH 会同时删除与节点相连的所有关系
        session.run("MATCH (n) DETACH DELETE n")
        
        # 导入实体
        with open(entity_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 解析标签 (支持 | 分隔)
                labels_str = row.get('labels', '')
                if not labels_str:
                     # 兼容旧格式
                    labels = []
                    for key in row.keys():
                        if key.lower().startswith('label'):
                            value = row.get(key, '')
                            if value and value.strip():
                                labels.append(value.strip().replace(' ', '_'))
                else:
                    labels = [l.strip().replace(' ', '_') for l in labels_str.split('|') if l.strip()]

                if not labels:
                    labels = ['Unknown']
                
                # 解析属性 (JSON 字符串)
                properties = {}
                props_str = row.get('properties', '{}')
                try:
                    properties = json.loads(props_str)
                except json.JSONDecodeError:
                    pass # 忽略解析错误
                
                # 确保 id 和 name 存在
                properties['id'] = int(row['id'])
                properties['name'] = row['name']

                # 构建 Cypher 查询语句
                # 动态构建标签部分，例如 :`Data_Structure`:`Linear`
                labels_cypher = ':'.join([f'`{label}`' for label in labels])
                
                # 动态设置属性
                # $props 是参数占位符，防止注入攻击
                cypher = f"CREATE (n:{labels_cypher}) SET n = $props"
                session.run(cypher, props=properties)
        
        # 导入关系
        with open(relation_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rel_type = row.get('type', row.get('relation', 'RELATED_TO')).replace(' ', '_')
                
                # 解析属性
                properties = {}
                props_str = row.get('properties', '{}')
                try:
                    properties = json.loads(props_str)
                except json.JSONDecodeError:
                    pass
                
                # 构建 Cypher 查询语句
                # MATCH 查找源节点 (a) 和目标节点 (b)
                # MERGE 创建或匹配关系 (r)
                cypher = f"""
                    MATCH (a), (b)
                    WHERE a.id = $source_id AND b.id = $target_id
                    MERGE (a)-[r:`{rel_type}`]->(b)
                    SET r += $props
                """
                session.run(
                    cypher,
                    source_id=int(row['source_id']),
                    target_id=int(row['target_id']),
                    props=properties
                )
        
        source_type = "saved checkpoint" if entity_file == SAVED_ENTITY_FILE else "original"
        return jsonify({"message": f"Database restored from {source_type}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@api_bp.route('/save', methods=['POST'])
def save_db():
    """
    保存当前数据库状态到 CSV 文件（创建检查点）
    """
    session = db.get_session()
    
    try:
        # 导出所有节点
        # MATCH (n) 匹配所有节点
        nodes_result = session.run("""
            MATCH (n)
            RETURN n, labels(n) as labels
            ORDER BY n.id
        """)
        
        # 写入实体文件
        with open(SAVED_ENTITY_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'labels', 'properties'])
            
            for record in nodes_result:
                node = record['n']
                labels = list(record['labels'])
                
                # 提取基本属性
                n_id = node.get('id')
                n_name = node.get('name')
                
                # 提取其他属性
                props = dict(node)
                if 'id' in props: del props['id']
                if 'name' in props: del props['name']
                
                writer.writerow([
                    n_id, 
                    n_name, 
                    "|".join(labels), 
                    json.dumps(props, ensure_ascii=False)
                ])
        
        # 导出所有关系
        # MATCH (a)-[r]->(b) 匹配所有关系
        rels_result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN a.id as source_id, b.id as target_id, type(r) as type, properties(r) as props
            ORDER BY a.id, b.id
        """)
        
        # 写入关系文件
        with open(SAVED_RELATION_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['source_id', 'target_id', 'type', 'properties'])
            
            for record in rels_result:
                writer.writerow([
                    record['source_id'], 
                    record['target_id'], 
                    record['type'], 
                    json.dumps(record['props'], ensure_ascii=False)
                ])
        
        return jsonify({"message": "Database saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@api_bp.route('/import', methods=['POST'])
def import_csv():
    """
    导入用户上传的 CSV 文件
    直接覆盖 data 目录下的文件，并更新数据库
    """
    if 'entity_file' not in request.files or 'relation_file' not in request.files:
        return jsonify({"error": "Both entity_file and relation_file are required"}), 400
    
    entity_file = request.files['entity_file']
    relation_file = request.files['relation_file']
    
    session = db.get_session()
    
    try:
        # 读取上传文件内容
        entity_content = entity_file.read().decode('utf-8')
        relation_content = relation_file.read().decode('utf-8')
        
        # 1. 保存到 data 文件夹 (直接覆盖，不备份)
        with open(Config.ENTITY_FILE, 'w', encoding='utf-8', newline='') as f:
            f.write(entity_content)
        
        with open(Config.RELATION_FILE, 'w', encoding='utf-8', newline='') as f:
            f.write(relation_content)
        
        # 2. 清空数据库
        session.run("MATCH (n) DETACH DELETE n")
        
        # 3. 导入实体
        entity_reader = csv.DictReader(io.StringIO(entity_content))
        for row in entity_reader:
            # 解析标签
            labels_str = row.get('labels', '')
            if not labels_str:
                 labels = []
                 for key in row.keys():
                    if key.lower().startswith('label'):
                        val = row.get(key, '')
                        if val: labels.append(val.strip().replace(' ', '_'))
            else:
                labels = [l.strip().replace(' ', '_') for l in labels_str.split('|') if l.strip()]
            
            if not labels: labels = ['Unknown']
            
            # 解析属性
            properties = {}
            try:
                properties = json.loads(row.get('properties', '{}'))
            except: pass
            
            properties['id'] = int(row['id'])
            properties['name'] = row['name']
            
            labels_cypher = ':'.join([f'`{label}`' for label in labels])
            session.run(f"CREATE (n:{labels_cypher}) SET n = $props", props=properties)
            
        # 4. 导入关系
        relation_reader = csv.DictReader(io.StringIO(relation_content))
        for row in relation_reader:
            rel_type = row.get('type', row.get('relation', 'RELATED_TO')).replace(' ', '_')
            
            properties = {}
            try:
                properties = json.loads(row.get('properties', '{}'))
            except: pass
            
            cypher = f"""
                MATCH (a), (b)
                WHERE a.id = $source_id AND b.id = $target_id
                MERGE (a)-[r:`{rel_type}`]->(b)
                SET r += $props
            """
            session.run(cypher, source_id=int(row['source_id']), target_id=int(row['target_id']), props=properties)

        # 5. 删除旧的检查点文件（确保下次 init 使用新数据）
        if os.path.exists(SAVED_ENTITY_FILE): os.remove(SAVED_ENTITY_FILE)
        if os.path.exists(SAVED_RELATION_FILE): os.remove(SAVED_RELATION_FILE)
        
        return jsonify({"message": "Data imported and saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
