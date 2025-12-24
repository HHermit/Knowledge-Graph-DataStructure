<template>
  <div class="info-panel-container">
    <transition-group name="list">
      <div 
        v-for="(item, index) in nodeHistory" 
        :key="item.id" 
        class="info-panel"
        :class="{ 'collapsed': index > 0, 'edge-panel': item.type === 'edge' }"
        @click="index > 0 ? $emit('promote', index) : null">
        
        <div class="panel-header">
          <div class="header-content">
            <span class="icon">{{ item.type === 'edge' ? '🔗' : '🔵' }}</span>
            <span v-if="item.type === 'edge'" class="title">{{ item.name }}</span>
            <span v-else class="title">{{ item.name }}</span>
            <span v-if="item.type !== 'edge'" class="node-id">#{{ item.id }}</span>
          </div>
          <button class="close-btn" @click.stop="$emit('remove', item.id)">×</button>
        </div>

        <div v-show="index === 0" class="panel-body">
          <!-- Node Info (节点信息) -->
          <template v-if="item.type !== 'edge'">
            <!-- Basic Info -->
            <div class="section-title">{{ t('basicInfo') }}</div>
            <div class="row">
              <span class="label">ID</span>
              <span class="value">{{ item.id }}</span>
            </div>
            <div class="row">
              <span class="label">{{ t('name') }}</span>
              <div class="value-group">
                <input v-if="item.isEditing" v-model="item.editName" class="edit-input" />
                <span v-else class="value">{{ item.name }}</span>
                <button v-if="!item.isEditing" @click="startEdit(item)" class="btn icon-btn">✏️</button>
                <button v-if="item.isEditing" @click="$emit('save', item)" class="btn icon-btn save">💾</button>
                <button v-if="item.isEditing" @click="cancelEdit(item)" class="btn icon-btn cancel">❌</button>
              </div>
            </div>

            <div class="tags-container">
              <span 
                v-for="lbl in (item.labels && item.labels.length > 0 ? item.labels : (item.category ? [item.category] : []))" 
                :key="lbl" 
                class="label-tag"
                :style="{ backgroundColor: getColor(lbl) }">
                {{ lbl }}
                <span class="remove-tag" @click="$emit('removeLabel', { nodeId: item.id, label: lbl })">×</span>
              </span>
            </div>
            <div class="add-label-row">
              <input v-model="newLabel" :placeholder="t('newLabel')" class="edit-input small" @keyup.enter="handleAddLabel(item)" />
              <button @click="handleAddLabel(item)" class="btn add-btn">+</button>
            </div>

            <!-- Properties (属性列表) -->
            <div class="section-title">
              {{ t('properties') }}
              <button @click="showAddProp = !showAddProp" class="btn icon-btn small" title="Add Property">➕</button>
            </div>
            
            <!-- Add Property Form -->
            <div v-if="showAddProp" class="add-prop-form">
              <input v-model="newPropKey" placeholder="Key" class="edit-input" />
              <input v-model="newPropValue" placeholder="Value" class="edit-input" />
              <button @click="handleAddProperty(item)" class="btn save">OK</button>
            </div>

            <div class="properties-list">
              <div v-for="(val, key) in item.properties" :key="key" class="prop-row">
                <div v-if="key !== 'id' && key !== 'name'" class="prop-content">
                  <span class="prop-key">{{ key }}:</span>
                  <span class="prop-value">{{ val }}</span>
                  <button @click="handleDeleteProperty(item, key)" class="btn icon-btn delete-prop">×</button>
                </div>
              </div>
            </div>

            <div class="actions-row">
              <button @click="$emit('delete', item)" class="btn delete full-width">🗑️ {{ t('deleteNode') }}</button>
            </div>
          </template>
          
          <!-- Edge Info (边信息) -->
          <template v-else>
            <div class="section-title">{{ t('relationship') }}</div>
            <div class="row">
              <span class="label">{{ t('type') }}</span>
              <span class="value">{{ item.name }}</span>
            </div>
            <div class="row">
              <span class="label">{{ t('source') }}</span>
              <span class="value">#{{ item.source }}</span>
            </div>
            <div class="row">
              <span class="label">{{ t('target') }}</span>
              <span class="value">#{{ item.target }}</span>
            </div>

            <!-- Properties -->
            <div class="section-title">
              {{ t('properties') }}
              <button @click="showAddProp = !showAddProp" class="btn icon-btn small">➕</button>
            </div>

            <div v-if="showAddProp" class="add-prop-form">
              <input v-model="newPropKey" placeholder="Key" class="edit-input" />
              <input v-model="newPropValue" placeholder="Value" class="edit-input" />
              <button @click="handleAddEdgeProperty(item)" class="btn save">OK</button>
            </div>

            <div class="properties-list">
              <div v-for="(val, key) in item.properties" :key="key" class="prop-row">
                <div class="prop-content">
                  <span class="prop-key">{{ key }}:</span>
                  <span class="prop-value">{{ val }}</span>
                  <button @click="handleDeleteEdgeProperty(item, key)" class="btn icon-btn delete-prop">×</button>
                </div>
              </div>
            </div>
            
            <div class="actions-row">
              <button @click="handleDeleteEdge(item)" class="btn delete full-width">🗑️ {{ t('deleteEdge') }}</button>
            </div>
          </template>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { messages } from '../i18n.js';
import api from '../api';

const props = defineProps({
  nodeHistory: { type: Array, default: () => [] }, // 选中节点/边的历史记录
  colors: { type: Array, default: () => [] }, // 颜色数组
  categories: { type: Array, default: () => [] }, // 分类列表
  lang: { type: String, default: 'en' } // 当前语言
});

// 定义事件
const emit = defineEmits(['promote', 'remove', 'save', 'delete', 'addLabel', 'removeLabel', 'refresh']);

const t = (key) => messages[props.lang][key] || key;

const newLabel = ref('');
const showAddProp = ref(false);
const newPropKey = ref('');
const newPropValue = ref('');

const getColor = (categoryName) => {
  const idx = props.categories.findIndex(c => c.name === categoryName);
  return idx !== -1 ? props.colors[idx % props.colors.length] : '#ccc';
};

// 开始编辑节点名称
const startEdit = (node) => {
  node.isEditing = true;
  node.editName = node.name;
};

const cancelEdit = (node) => {
  node.isEditing = false;
};

// 处理添加标签
const handleAddLabel = (item) => {
  if (newLabel.value) {
    emit('addLabel', { nodeId: item.id, label: newLabel.value });
    newLabel.value = '';
  }
};

// 处理添加节点属性
const handleAddProperty = async (item) => {
  if (!newPropKey.value) return;
  try {
    await api.updateNodeProperty(item.id, newPropKey.value, newPropValue.value);
    // 更新本地状态，避免重新刷新整个图谱
    if (!item.properties) item.properties = {};
    item.properties[newPropKey.value] = newPropValue.value;
    newPropKey.value = '';
    newPropValue.value = '';
    showAddProp.value = false;
  } catch (e) {
    alert('Failed to add property');
  }
};

// 处理删除节点属性
const handleDeleteProperty = async (item, key) => {
  if (!confirm(`Delete property '${key}'?`)) return;
  try {
    await api.deleteNodeProperty(item.id, key);
    delete item.properties[key];
  } catch (e) {
    alert('Failed to delete property');
  }
};

// 处理添加边属性
const handleAddEdgeProperty = async (item) => {
  if (!newPropKey.value) return;
  try {
    await api.updateRelationProperty(item.source, item.target, item.name, newPropKey.value, newPropValue.value);
    if (!item.properties) item.properties = {};
    item.properties[newPropKey.value] = newPropValue.value;
    newPropKey.value = '';
    newPropValue.value = '';
    showAddProp.value = false;
  } catch (e) {
    alert('Failed to add property');
  }
};

const handleDeleteEdgeProperty = async (item, key) => {
  if (!confirm(`Delete property '${key}'?`)) return;
  try {
    await api.deleteRelationProperty(item.source, item.target, item.name, key);
    delete item.properties[key];
  } catch (e) {
    alert('Failed to delete property');
  }
};

// 处理删除边
const handleDeleteEdge = async (item) => {
  if (!confirm('Delete this relationship?')) return;
  try {
    await api.deleteRelation(item.source, item.target, item.name);
    emit('remove', item.id); // 从历史记录中移除
    emit('refresh'); // 刷新图谱
  } catch (e) {
    alert('Failed to delete relationship');
  }
};
</script>

<style scoped>
.info-panel-container {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 320px;
  max-height: 85vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 100;
}

.info-panel {
  background: rgba(30, 30, 40, 0.95);
  border: 1px solid #444;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.5);
  overflow: hidden;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.info-panel.collapsed {
  height: 40px;
  opacity: 0.7;
  cursor: pointer;
}

.info-panel.collapsed:hover {
  opacity: 1;
  transform: translateX(-5px);
}

.edge-panel {
  border-color: #68bdf6;
}

.panel-header {
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #444;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.title {
  font-weight: bold;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}

.node-id {
  font-size: 11px;
  color: #888;
  background: #222;
  padding: 2px 4px;
  border-radius: 3px;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 18px;
  cursor: pointer;
  padding: 0 5px;
}

.close-btn:hover { color: #fff; }

.panel-body {
  padding: 15px;
  color: #e0e0e0;
}

.section-title {
  font-size: 12px;
  text-transform: uppercase;
  color: #888;
  margin: 15px 0 8px 0;
  border-bottom: 1px solid #444;
  padding-bottom: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title:first-child { margin-top: 0; }

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 13px;
}

.label { color: #aaa; }
.value { color: #fff; font-weight: 500; }

.value-group {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 1;
  justify-content: flex-end;
}

.edit-input {
  background: #333;
  border: 1px solid #555;
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
  width: 100%;
}

.edit-input.small {
  padding: 2px 6px;
  font-size: 12px;
}

.btn {
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn {
  background: transparent;
  padding: 2px;
  font-size: 14px;
}

.icon-btn:hover { transform: scale(1.1); }

.add-btn {
  background: #4caf50;
  color: white;
  padding: 2px 8px;
  font-size: 16px;
  line-height: 1;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.label-tag {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  color: #333;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 4px;
}

.remove-tag {
  cursor: pointer;
  opacity: 0.6;
  font-size: 14px;
}

.remove-tag:hover { opacity: 1; }

.add-label-row {
  display: flex;
  gap: 5px;
}

.add-prop-form {
  display: flex;
  gap: 5px;
  margin-bottom: 10px;
  background: #252530;
  padding: 8px;
  border-radius: 4px;
}

.properties-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.prop-row {
  background: #252530;
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.prop-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.prop-key { color: #aaa; margin-right: 8px; }
.prop-value { color: #fff; flex: 1; word-break: break-all; }

.delete-prop {
  color: #ff6b6b;
  opacity: 0;
  transition: opacity 0.2s;
}

.prop-row:hover .delete-prop { opacity: 1; }

.actions-row {
  margin-top: 20px;
}

.btn.delete {
  background: rgba(255, 80, 80, 0.2);
  color: #ff6b6b;
  padding: 8px;
}

.btn.delete:hover {
  background: rgba(255, 80, 80, 0.3);
}

.full-width { width: 100%; }
</style>
