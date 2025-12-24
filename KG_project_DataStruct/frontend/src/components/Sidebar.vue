<template>
  <div class="sidebar">
    <!-- Top Toggles (顶部切换按钮) -->
    <div class="top-toggles">
      <!-- 语言切换按钮 -->
      <button @click="toggleLang" class="toggle-btn">
        {{ lang === 'en' ? '中文' : 'EN' }}
      </button>
    </div>

    <!-- Database Info Section (数据库信息区域) -->
    <div class="section">
      <h2><span class="icon">📊</span> {{ t('databaseInfo') }}</h2>
      <div class="info-item">
        <span class="label">{{ t('nodes') }}</span>
        <span class="badge">{{ nodeCount }}</span>
      </div>
      <div class="label-list">
        <span 
          class="label-tag clickable all-cat"
          @click="$emit('showAllNodes')"
          :title="t('showAll')">
          ALL
        </span>
        <span 
          v-for="cat in categories" 
          :key="cat.name" 
          class="label-tag clickable"
          :style="{ backgroundColor: getColor(cat.name) }"
          @click="$emit('filterByCategory', cat.name)"
          :title="t('clickToHighlight')">
          {{ cat.name }}
        </span>
      </div>

      
      <div class="info-item mt-4">
        <span class="label">{{ t('relationships') }}</span>
        <span class="badge">{{ linkCount }}</span>
      </div>
      <div class="label-list">
        <span 
          class="rel-tag clickable all-rel"
          @click="$emit('showAllRelations')"
          :title="t('showAllRelations')">
          ALL
        </span>
        <span 
          v-for="rel in relationTypes" 
          :key="rel" 
          class="rel-tag clickable"
          @click="$emit('filterByRelation', rel)"
          :title="t('clickToHighlight')">
          {{ rel }}
        </span>
      </div>
    </div>

    <!-- Search Section (搜索区域) -->
    <div class="section">
      <h2><span class="icon">🔍</span> {{ t('search') }}</h2>
      <div class="input-group">
        <input 
          v-model="searchQuery" 
          @keyup.enter="$emit('search', searchQuery)"
          :placeholder="t('searchPlaceholder')" 
        />
        <button @click="$emit('search', searchQuery)" class="btn icon-btn">Go</button>
      </div>
    </div>

    <!-- Path Finding Section (路径查找区域) -->
    <div class="section">
      <h2><span class="icon">🛣️</span> {{ t('pathFinding') }}</h2>
      <input v-model="startNode" :placeholder="t('startNode')" class="mb-8" />
      <input v-model="endNode" :placeholder="t('endNode')" class="mb-8" />
      <button @click="$emit('findPath', { start: startNode, end: endNode })" class="btn full-width">{{ t('findPath') }}</button>
    </div>

    <!-- Add Node Section (添加节点区域) -->
    <div class="section">
      <h2><span class="icon">➕</span> {{ t('addNode') }}</h2>
      <input v-model="newNodeName" :placeholder="t('name')" class="mb-8" />
      <select v-model="newNodeLabel" class="select-box">
        <option value="" disabled>{{ t('selectLabel') }}</option>
        <option v-for="cat in categories" :key="cat.name" :value="cat.name">{{ cat.name }}</option>
        <option value="__custom__">{{ t('custom') }}</option>
      </select>
      <input v-if="newNodeLabel === '__custom__'" v-model="customLabel" :placeholder="t('customLabel')" class="mb-8" />
      
      <!-- Initial Properties -->
      <div class="props-input">
        <input v-model="nodePropKey" placeholder="Prop Key" class="half-width" />
        <input v-model="nodePropValue" placeholder="Value" class="half-width" />
      </div>

      <button @click="addNode" class="btn full-width success">{{ t('createNode') }}</button>
    </div>

    <!-- Add Edge Section (添加边区域) -->
    <div class="section">
      <h2><span class="icon">🔗</span> {{ t('addEdge') }}</h2>
      <input v-model="edgeSourceName" :placeholder="t('sourceName')" class="mb-8" />
      <input v-model="edgeTargetName" :placeholder="t('targetName')" class="mb-8" />
      <select v-model="edgeType" class="select-box">
        <option value="" disabled>{{ t('selectType') }}</option>
        <option v-for="rel in relationTypes" :key="rel" :value="rel">{{ rel }}</option>
        <option value="__custom__">{{ t('custom') }}</option>
      </select>
      <input v-if="edgeType === '__custom__'" v-model="customType" :placeholder="t('customType')" class="mb-8" />
      
      <!-- Initial Properties -->
      <div class="props-input">
        <input v-model="edgePropKey" placeholder="Prop Key" class="half-width" />
        <input v-model="edgePropValue" placeholder="Value" class="half-width" />
      </div>

      <button @click="addEdge" class="btn full-width success">{{ t('createEdge') }}</button>
    </div>

    <!-- Import/Export Section (导入/导出区域) -->
    <div class="section">
      <h2><span class="icon">📁</span> {{ t('importExport') }}</h2>
      <div class="template-btns">
        <a href="http://localhost:5000/api/template/entity" target="_blank" class="link-btn" @click="showUtf8Tip">📄 Entity Tpl</a>
        <a href="http://localhost:5000/api/template/relation" target="_blank" class="link-btn" @click="showUtf8Tip">📄 Relation Tpl</a>
      </div>
      
      <div class="file-upload">
        <label class="file-label">
          <span>Nodes (CSV)</span>
          <input type="file" @change="handleEntityUpload" accept=".csv" />
        </label>
        <label class="file-label">
          <span>Edges (CSV)</span>
          <input type="file" @change="handleRelationUpload" accept=".csv" />
        </label>
      </div>
      
      <button 
        @click="importData" 
        class="btn full-width primary mt-8"
        :disabled="!entityFile || !relationFile">
        🚀 {{ t('importData') }}
      </button>
      <p v-if="entityFile || relationFile" class="file-info">
        {{ entityFile?.name || '—' }} / {{ relationFile?.name || '—' }}
      </p>
    </div>

    <!-- Actions Section (操作按钮区域) -->
    <div class="section actions">
      <button @click="$emit('saveDb')" class="btn full-width success">💾 {{ t('saveDatabase') }}</button>
      <button @click="$emit('initDb')" class="btn full-width warning">🔄 {{ t('resetDatabase') }}</button>
      <button @click="$emit('resetView')" class="btn full-width">👁️ {{ t('resetView') }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { messages } from '../i18n.js';

const props = defineProps({
  nodeCount: { type: Number, default: 0 }, // 节点总数
  linkCount: { type: Number, default: 0 }, // 关系总数
  categories: { type: Array, default: () => [] }, // 节点分类列表
  relationTypes: { type: Array, default: () => [] }, // 关系类型列表
  colors: { type: Array, default: () => [] }, // 颜色数组
  lang: { type: String, default: 'en' } // 当前语言
});

// 定义组件触发的事件
const emit = defineEmits(['search', 'findPath', 'createNode', 'createEdge', 'initDb', 'resetView', 'toggleLang', 'filterByCategory', 'filterByRelation', 'importFiles', 'saveDb', 'showAllRelations', 'showAllNodes']);

// 国际化翻译函数
const t = (key) => messages[props.lang][key] || key;

const toggleLang = () => emit('toggleLang');

// Search
const searchQuery = ref('');

// Path Finding (支持名称或ID)
const startNode = ref('');
const endNode = ref('');

// Add Node
const newNodeName = ref('');
const newNodeLabel = ref('');
const customLabel = ref('');
const nodePropKey = ref('');
const nodePropValue = ref('');

// Add Edge (支持名称或ID)
const edgeSourceName = ref('');
const edgeTargetName = ref('');
const edgeType = ref('');
const customType = ref('');
const edgePropKey = ref('');
const edgePropValue = ref('');

// File upload
const entityFile = ref(null);
const relationFile = ref(null);

// 获取分类对应的颜色
const getColor = (categoryName) => {
  const idx = props.categories.findIndex(c => c.name === categoryName);
  return idx !== -1 ? props.colors[idx % props.colors.length] : '#ccc';
};

// 添加节点逻辑
const addNode = () => {
  if (!newNodeName.value) return;
  const label = newNodeLabel.value === '__custom__' ? customLabel.value : newNodeLabel.value;
  // 移除对 label 的强制检查，后端现在会处理空标签的情况
  
  const properties = {};
  if (nodePropKey.value) {
    properties[nodePropKey.value] = nodePropValue.value;
  }

  emit('createNode', { name: newNodeName.value, label, properties });
  
  // 重置表单
  newNodeName.value = '';
  nodePropKey.value = '';
  nodePropValue.value = '';
};

// 添加边逻辑
const addEdge = () => {
  if (!edgeSourceName.value || !edgeTargetName.value) return;
  const type = edgeType.value === '__custom__' ? customType.value : edgeType.value;
  if (!type) return;

  const properties = {};
  if (edgePropKey.value) {
    properties[edgePropKey.value] = edgePropValue.value;
  }

  emit('createEdge', { 
    sourceName: edgeSourceName.value, 
    targetName: edgeTargetName.value, 
    type,
    properties
  });
  
  // 重置表单
  edgeSourceName.value = '';
  edgeTargetName.value = '';
  edgePropKey.value = '';
  edgePropValue.value = '';
};

// 处理文件上传
const handleEntityUpload = (e) => {
  showUtf8Tip();
  entityFile.value = e.target.files[0];
};

const handleRelationUpload = (e) => {
  showUtf8Tip();
  relationFile.value = e.target.files[0];
};

const showUtf8Tip = () => {
  alert('⚠️ 提示：CSV 文件请使用 UTF-8 编码保存，否则中文可能会乱码。');
};

// 触发导入事件
const importData = () => {
  if (entityFile.value && relationFile.value) {
    emit('importFiles', { entityFile: entityFile.value, relationFile: relationFile.value });
  }
};
</script>

<style scoped>
.sidebar {
  width: 280px;
  background: #1e1e2f;
  border-right: 1px solid #333;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 15px;
  color: #e0e0e0;
}

.top-toggles {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.toggle-btn {
  background: transparent;
  border: 1px solid #555;
  color: #aaa;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  cursor: pointer;
}

.toggle-btn:hover { color: #fff; border-color: #fff; }

.section {
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #333;
}

.section:last-child { border-bottom: none; }

h2 {
  font-size: 14px;
  text-transform: uppercase;
  color: #888;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon { font-size: 16px; }

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.badge {
  background: #333;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.label-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.label-tag {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 11px;
  color: #333;
  font-weight: bold;
}

.all-cat {
  background: #e0e0e0;
  color: #333;
}

.rel-tag {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  background: #333;
  color: #ccc;
  border: 1px solid #444;
}

.clickable { cursor: pointer; transition: transform 0.1s; }
.clickable:hover { transform: scale(1.05); filter: brightness(1.2); }

.all-rel { color: #fff; border-color: #666; }

.input-group {
  display: flex;
  gap: 5px;
}

input, .select-box {
  width: 100%;
  padding: 8px;
  background: #2b2b3c;
  border: 1px solid #444;
  border-radius: 4px;
  color: #fff;
  font-size: 13px;
  outline: none;
}

input:focus, .select-box:focus { border-color: #68bdf6; }

.mb-8 { margin-bottom: 8px; }
.mt-4 { margin-top: 4px; }
.mt-8 { margin-top: 8px; }

.btn {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: #333;
  color: #e0e0e0;
  font-size: 13px;
  transition: all 0.2s;
}

.btn:hover { background: #444; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.icon-btn { padding: 8px 12px; }
.full-width { width: 100%; }

.success { background: #2e7d32; color: white; }
.success:hover { background: #388e3c; }

.warning { background: #f57c00; color: white; }
.warning:hover { background: #fb8c00; }

.primary { background: #1976d2; color: white; }
.primary:hover { background: #2196f3; }

.template-btns {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.link-btn {
  font-size: 12px;
  color: #68bdf6;
  text-decoration: none;
}
.link-btn:hover { text-decoration: underline; }

.file-upload {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #aaa;
}

.file-info {
  font-size: 11px;
  color: #666;
  margin-top: 5px;
  text-align: center;
}

.props-input {
  display: flex;
  gap: 5px;
  margin-bottom: 8px;
}

.half-width { width: 50%; }
</style>
