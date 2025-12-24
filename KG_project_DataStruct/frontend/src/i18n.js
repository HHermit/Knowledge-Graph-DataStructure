/**
 * 国际化语言包
 * 包含中英文翻译
 */
export const messages = {
    en: {
        // Sidebar
        databaseInfo: 'Database Info',
        nodes: 'Nodes',
        relationships: 'Relationships',
        search: 'Search',
        searchPlaceholder: 'Node name...',
        pathFinding: 'Path Finding',
        startId: 'Start ID',
        endId: 'End ID',
        findPath: 'Find Path',
        startNode: 'Start (ID or Name)',
        endNode: 'End (ID or Name)',
        addNode: 'Add Node',
        name: 'Name',
        label: 'Label',
        selectLabel: 'Select Label',
        customLabel: 'Custom Label',
        custom: 'Custom Text',
        createNode: 'Create Node',
        addEdge: 'Add Edge',
        sourceId: 'Source ID',
        targetId: 'Target ID',
        type: 'Type',
        sourceName: 'Source (ID or Name)',
        targetName: 'Target (ID or Name)',
        createEdge: 'Create Edge',
        selectType: 'Select Type',
        customType: 'Custom Type',
        resetDatabase: 'Reset Database',
        saveDatabase: 'Save Checkpoint',
        resetView: 'Reset View',
        language: 'Language',
        clickToHighlight: 'Click to highlight',
        importExport: 'Import / Export',
        entityTemplate: 'Entity Template',
        relationTemplate: 'Relation Template',
        uploadEntity: 'Upload Entity CSV',
        uploadRelation: 'Upload Relation CSV',
        importData: 'Import Data',

        // Node Info Panel
        nodeInfo: 'Node Info',
        labels: 'Labels',
        addLabelPlaceholder: 'Add label...',
        showAll: 'Show all nodes',
        showAllRelations: 'Show all relationships',
        edit: 'Edit',
        save: 'Save',
        delete: 'Delete',
        cancel: 'Cancel',

        // Alerts
        noNodesFound: 'No nodes found',
        pathNotFound: 'Path not found',
        nodeCreated: 'Node created!',
        edgeCreated: 'Edge created!',
        deleteFailed: 'Delete failed',
        saveFailed: 'Save failed',
        confirmDelete: 'Delete node #{id}? This will also delete connected edges.'
    },
    zh: {
        // 侧边栏
        databaseInfo: '数据库信息',
        nodes: '节点',
        relationships: '关系',
        search: '搜索',
        searchPlaceholder: '节点名称...',
        pathFinding: '路径查找',
        startId: '起始ID',
        endId: '结束ID',
        findPath: '查找路径',
        startNode: '起点 (ID或名称)',
        endNode: '终点 (ID或名称)',
        addNode: '添加节点',
        name: '名称',
        label: '标签',
        selectLabel: '选择标签',
        customLabel: '自定义标签',
        custom: '自定义标签文字',
        createNode: '创建节点',
        addEdge: '添加关系',
        sourceId: '源ID',
        targetId: '目标ID',
        type: '类型',
        sourceName: '源 (ID或名称)',
        targetName: '目标 (ID或名称)',
        createEdge: '创建关系',
        selectType: '选择类型',
        customType: '自定义类型',
        resetDatabase: '重置数据库',
        saveDatabase: '保存检查点',
        resetView: '重置视图',
        language: '语言',
        clickToHighlight: '点击高亮显示',
        importExport: '导入 / 导出',
        entityTemplate: '实体模板',
        relationTemplate: '关系模板',
        uploadEntity: '上传实体 CSV',
        uploadRelation: '上传关系 CSV',
        importData: '导入数据',

        // 节点信息面板
        nodeInfo: '节点信息',
        labels: '标签',
        addLabelPlaceholder: '添加标签...',
        showAll: '显示所有节点',
        showAllRelations: '显示所有关系',
        edit: '编辑',
        save: '保存',
        delete: '删除',
        cancel: '取消',

        // 提示
        noNodesFound: '未找到节点',
        pathNotFound: '未找到路径',
        nodeCreated: '节点已创建！',
        edgeCreated: '关系已创建！',
        deleteFailed: '删除失败',
        saveFailed: '保存失败',
        confirmDelete: '删除节点 #{id}？这将同时删除与之相连的所有关系。'
    }
};

export const useI18n = (lang = 'en') => {
    return {
        t: (key) => messages[lang]?.[key] || key,
        messages
    };
};
