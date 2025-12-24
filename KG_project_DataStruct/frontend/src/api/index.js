import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const apiClient = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json'
    }
});

export default {
    // 获取全图数据
    getGraph() {
        return apiClient.get('/graph');
    },

    // 搜索节点
    searchNodes(query) {
        return apiClient.get('/search', { params: { q: query } });
    },

    // 查找最短路径
    findPath(start, end) {
        return apiClient.get('/path', { params: { start, end } });
    },

    // 创建节点
    createNode(data) {
        return apiClient.post('/node', data);
    },

    // 更新节点 (名称)
    updateNode(id, data) {
        return apiClient.put(`/node/${id}`, data);
    },

    // 删除节点
    deleteNode(id) {
        return apiClient.delete(`/node/${id}`);
    },

    // 节点属性操作
    updateNodeProperty(id, key, value) {
        return apiClient.put(`/node/${id}/property`, { key, value });
    },

    deleteNodeProperty(id, key) {
        return apiClient.delete(`/node/${id}/property/${key}`);
    },

    // 创建关系
    createRelation(data) {
        return apiClient.post('/relationship', data);
    },

    // 删除关系
    deleteRelation(sourceId, targetId, type) {
        return apiClient.delete('/relationship', {
            params: { source_id: sourceId, target_id: targetId, type }
        });
    },

    // 关系属性操作
    updateRelationProperty(sourceId, targetId, type, key, value) {
        return apiClient.put('/relationship/property', {
            source_id: sourceId, target_id: targetId, type, key, value
        });
    },

    deleteRelationProperty(sourceId, targetId, type, key) {
        return apiClient.delete('/relationship/property', {
            params: { source_id: sourceId, target_id: targetId, type, key }
        });
    },

    // 添加节点标签
    addNodeLabel(id, label) {
        return apiClient.post(`/node/${id}/label`, { label });
    },

    // 删除节点标签
    removeNodeLabel(id, label) {
        return apiClient.delete(`/node/${id}/label/${label}`);
    },

    // 初始化数据库
    initDb() {
        return apiClient.post('/init');
    },

    // 保存数据库快照
    saveDb() {
        return apiClient.post('/save');
    },

    // 导入文件
    importFiles(formData) {
        return apiClient.post('/import', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    }
};
