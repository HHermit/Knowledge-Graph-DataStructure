<template>
  <div class="knowledge-graph">
    <!-- Sidebar (侧边栏) -->
    <Sidebar 
      :nodeCount="nodes.length"
      :linkCount="links.length"
      :categories="categories"
      :relationTypes="relationTypes"
      :colors="colors"
      :lang="currentLang"
      @search="handleSearch"
      @findPath="handleFindPath"
      @createNode="handleCreateNode"
      @createEdge="handleCreateEdge"
      @initDb="handleInitDb"
      @saveDb="handleSaveDb"
      @resetView="handleResetView"
      @toggleLang="toggleLang"
      @filterByCategory="handleFilterByCategory" 
      @filterByRelation="handleFilterByRelation"
      @showAllRelations="handleShowAllRelations"
      @showAllNodes="handleResetView"
      @importFiles="handleImportFiles"
    />

    <!-- Main Content (主内容区) -->
    <div class="main-content">
      <!-- D3.js SVG 容器 -->
      <svg ref="svgRef" class="graph-svg">
        <defs>
          <!-- 箭头标记定义 -->
          <marker id="arrow" viewBox="0 -5 10 10" refX="22" refY="0" markerWidth="10" markerHeight="10" orient="auto">
            <path d="M0,-4L10,0L0,4" fill="#e0e0e0"/>
          </marker>
        </defs>
        <g ref="zoomContainerRef" class="zoom-container">
          <g class="links"></g>
          <g class="link-labels"></g> <!-- 新增：边标签组 -->
          <g class="nodes"></g>
        </g>
      </svg>
      
      <!-- Info Panel (信息面板) -->
      <NodeInfoPanel 
        :nodeHistory="nodeHistory"
        :colors="colors"
        :categories="categories"
        :lang="currentLang"
        @promote="promoteNode"
        @remove="removeFromHistory"
        @save="handleSaveNode"
        @delete="handleDeleteNode"
        @addLabel="handleAddLabel"
        @removeLabel="handleRemoveLabel"
        @refresh="fetchGraph"
        class="info-panel-container"
      />

      <!-- Minimap (小地图) -->
      <div class="minimap-container">
        <svg ref="minimapSvgRef" class="minimap-svg">
          <g class="minimap-content"></g>
          <rect class="viewport-rect"></rect>
        </svg>
      </div>

      <!-- Floating Controls (悬浮控制按钮) -->
      <div class="floating-controls">
        <button 
          class="control-btn" 
          @click="releaseFixedNodes" 
          title="释放所有固定节点，恢复自动布局">
          <span class="icon">🔓</span> 释放固定
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import * as d3 from 'd3'; // D3.js 用于图谱可视化
import api from '../api'; // 导入 API 模块
import Sidebar from './Sidebar.vue';
import NodeInfoPanel from './NodeInfoPanel.vue';

// Graph data (图数据)
const nodes = ref([]);
const links = ref([]);
const categories = ref([]);
const nodeHistory = ref([]); // 节点点击历史记录

// D3.js refs
const svgRef = ref(null);
const zoomContainerRef = ref(null);
const minimapSvgRef = ref(null); // 小地图 SVG ref

let simulation = null;  // D3 力导向模拟
let resizeObserver = null; // 监听容器大小变化
const zoomBehavior = ref(null); // 存储缩放行为

// Color palette - Pastel/Macaron colors (low saturation)
// 颜色调色板（低饱和度马卡龙色系）
const colors = [
  '#E0BBE4',  // Light Purple/Lavender
  '#D2E7D6',  // Light Beige/Olive  
  '#FFDAC1',  // Light Peach/Orange
  '#FFE5D9',  // Light Pink
  '#E2F0CB',  // Light Green
  '#B5EAD7',  // Mint
  '#C7CEEA',  // Periwinkle
  '#FFDFD3',  // Peach
  '#E8E8E8',  // Light Gray
  '#D4A5A5'   // Dusty Rose
];

// Language (语言设置)
const currentLang = ref('zh');
const toggleLang = () => {
  currentLang.value = currentLang.value === 'en' ? 'zh' : 'en';
};

// 保存当前筛选状态和焦点状态
const currentFilterState = ref({ 
  highlightIds: [],    // 用于过滤（hideNonMatching=true 时决定哪些节点可见）
  highlightEdges: [],  // 用于过滤（hideNonMatching=true 时决定哪些边可见）
  hideNonMatching: false,
  focusIds: [],        // 用于视觉高亮（点击节点时高亮它和邻居）
  focusEdges: []       // 用于视觉高亮（点击节点时高亮相关边）
});
// 当前缩放比例
const currentZoom = ref(1);

// Computed (计算属性)
const relationTypes = computed(() => {
  const types = new Set(links.value.map(l => l.name));
  return Array.from(types);
});

// 初始化 D3.js 图表
const initChart = () => {
  if (!svgRef.value) return;
  
  const svg = d3.select(svgRef.value);
  let width = svgRef.value.clientWidth || window.innerWidth;
  let height = svgRef.value.clientHeight || window.innerHeight;
  
  svg.attr('width', width).attr('height', height);
  
  // 配置缩放行为
  zoomBehavior.value = d3.zoom()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
      d3.select(zoomContainerRef.value).attr('transform', event.transform);
      currentZoom.value = event.transform.k;
      updateMinimapViewport(event.transform);
    });
  
  svg.call(zoomBehavior.value);
  
  // 初始缩放位置
  const initialTransform = d3.zoomIdentity.translate(width / 2, height / 2).scale(1).translate(-width / 2, -height / 2);
  svg.call(zoomBehavior.value.transform, initialTransform);

  // 配置力导向模拟
  simulation = d3.forceSimulation()
    .velocityDecay(0.6)
    .alphaDecay(0.05)
    .force('link', d3.forceLink().id(d => d.id).distance(60)) // 缩短连线距离 (100 -> 60)
    .force('charge', d3.forceManyBody().strength(-150)) // 减小排斥力 (-400 -> -150)
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(25)); // 增大碰撞半径 (15 -> 25) 以保护标签不重叠
  
  // 点击空白处清除选中状态
  svg.on('click', (event) => {
    if (event.target === svgRef.value) {
      nodeHistory.value = [];
      currentFilterState.value.focusIds = [];
      currentFilterState.value.focusEdges = [];
    }
  });
  
  // 监听窗口大小变化
  resizeObserver = new ResizeObserver(entries => {
    for (const entry of entries) {
      const { width: newWidth, height: newHeight } = entry.contentRect;
      if (newWidth === 0 || newHeight === 0) return;
      
      svg.attr('width', newWidth).attr('height', newHeight);
      
      if (simulation) {
        simulation.force('center', d3.forceCenter(newWidth / 2, newHeight / 2));
        simulation.alpha(1).restart();
      }
    }
  });
  
  resizeObserver.observe(svgRef.value);
  initMinimap();
};

// 小地图相关逻辑
let minimapScale = 0.1;
const minimapSize = { width: 240, height: 160 };

const initMinimap = () => {
  if (!minimapSvgRef.value) return;
  const svg = d3.select(minimapSvgRef.value);
  svg.attr('viewBox', `0 0 ${minimapSize.width} ${minimapSize.height}`);
};

const updateMinimap = () => {
  if (!minimapSvgRef.value || !simulation) return;
  const currentNodes = simulation.nodes();
  if (!currentNodes.length) {
    const svg = d3.select(minimapSvgRef.value);
    svg.select('.minimap-content').selectAll('circle').remove();
    return;
  }
  
  const svg = d3.select(minimapSvgRef.value);
  const content = svg.select('.minimap-content');
  const xExtent = d3.extent(currentNodes, d => d.x);
  const yExtent = d3.extent(currentNodes, d => d.y);
  
  if (xExtent[0] === undefined || yExtent[0] === undefined) return;
  
  const padding = 50;
  const graphWidth = xExtent[1] - xExtent[0] + padding * 2;
  const graphHeight = yExtent[1] - yExtent[0] + padding * 2;
  
  const scaleX = minimapSize.width / graphWidth;
  const scaleY = minimapSize.height / graphHeight;
  minimapScale = Math.min(scaleX, scaleY) * 0.8;
  
  const graphCenterX = (xExtent[0] + xExtent[1]) / 2;
  const graphCenterY = (yExtent[0] + yExtent[1]) / 2;
  
  const miniNodes = content.selectAll('circle')
    .data(currentNodes, d => d.id);
    
  miniNodes.exit().remove();
  
  miniNodes.enter().append('circle')
    .attr('r', 2)
    .attr('fill', d => getColor(d.category))
    .merge(miniNodes)
    .attr('cx', d => (d.x - graphCenterX) * minimapScale + minimapSize.width / 2)
    .attr('cy', d => (d.y - graphCenterY) * minimapScale + minimapSize.height / 2);
};

const updateMinimapViewport = (transform) => {
  if (!minimapSvgRef.value || !svgRef.value) return;
  const svg = d3.select(minimapSvgRef.value);
  const rect = svg.select('.viewport-rect');
  const mainWidth = svgRef.value.clientWidth || window.innerWidth;
  const mainHeight = svgRef.value.clientHeight || window.innerHeight;
  const xExtent = d3.extent(nodes.value, d => d.x);
  const yExtent = d3.extent(nodes.value, d => d.y);
  
  if (xExtent[0] === undefined) return;
  const graphCenterX = (xExtent[0] + xExtent[1]) / 2;
  const graphCenterY = (yExtent[0] + yExtent[1]) / 2;
  
  const visibleX = (-transform.x) / transform.k;
  const visibleY = (-transform.y) / transform.k;
  const visibleW = mainWidth / transform.k;
  const visibleH = mainHeight / transform.k;
  
  const miniX = (visibleX - graphCenterX) * minimapScale + minimapSize.width / 2;
  const miniY = (visibleY - graphCenterY) * minimapScale + minimapSize.height / 2;
  const miniW = visibleW * minimapScale;
  const miniH = visibleH * minimapScale;
  
  rect.attr('x', miniX).attr('y', miniY).attr('width', miniW).attr('height', miniH);
};

const getColor = (category) => {
  const catIndex = categories.value.findIndex(c => c.name === category);
  return colors[catIndex % colors.length] || '#ccc';
};

// Fetch graph data (获取图数据)
const fetchGraph = async () => {
  try {
    const response = await api.getGraph();
    const newNodes = response.data.nodes.map(n => {
      const existing = nodes.value.find(en => String(en.id) === String(n.id));
      if (existing) {
        return { ...n, x: existing.x, y: existing.y, vx: existing.vx, vy: existing.vy };
      }
      return n;
    });
    
    nodes.value = newNodes;
    links.value = response.data.links;
    updateCategories();
    
    if (nodeHistory.value.length > 0) {
      nodeHistory.value = nodeHistory.value.map(historyItem => {
        if (historyItem.type === 'node') {
          const latestNode = nodes.value.find(n => String(n.id) === String(historyItem.id));
          if (latestNode) {
            return { ...historyItem, ...latestNode, isEditing: historyItem.isEditing, editName: historyItem.editName };
          }
        }
        return historyItem;
      });
    }
    renderGraph();
  } catch (error) {
    console.error('Error fetching graph:', error);
  }
};

// 更新分类列表
const updateCategories = () => {
  const uniqueCats = [...new Set(nodes.value.map(n => n.category))];
  const relationNames = new Set(links.value.map(l => l.name));
  // 过滤掉也是关系名称的分类
  const filteredCats = uniqueCats.filter(cat => !relationNames.has(cat));
  
  categories.value = filteredCats.map(name => {
    // 如果分类为空（无标签节点），赋予特殊名称
    if (name === null || name === undefined || name === '') {
      return { name: '未分配标签', isUnassigned: true };
    }
    return { name };
  });
};

// D3 渲染图谱
const renderGraph = (highlightIds = [], highlightEdges = [], hideNonMatching = false, focusIds = [], focusEdges = [], specificLinks = null) => {
  if (!svgRef.value || !simulation) return;
  
  const filteredNodes = nodes.value.filter(node => {
    if (hideNonMatching && highlightIds.length > 0) {
      return highlightIds.includes(String(node.id));
    }
    return true;
  });
  
  let filteredLinks;
  if (specificLinks) {
    filteredLinks = specificLinks;
  } else {
    filteredLinks = links.value.filter(link => {
      if (hideNonMatching && highlightIds.length > 0) {
        const sourceId = String(typeof link.source === 'object' ? link.source.id : link.source);
        const targetId = String(typeof link.target === 'object' ? link.target.id : link.target);
        return highlightIds.includes(sourceId) && highlightIds.includes(targetId);
      }
      return true;
    });
  }

  // 3. 聚簇布局逻辑：识别核心节点并建立引力关联
  const degrees = {};
  filteredLinks.forEach(l => {
    const s = String(typeof l.source === 'object' ? l.source.id : l.source);
    const t = String(typeof l.target === 'object' ? l.target.id : l.target);
    degrees[s] = (degrees[s] || 0) + 1;
    degrees[t] = (degrees[t] || 0) + 1;
  });

  // 定义核心节点（连接数 > 3）
  const hubs = filteredNodes.filter(n => (degrees[String(n.id)] || 0) > 3);
  const hubMap = new Map(hubs.map(h => [String(h.id), h]));

  filteredNodes.forEach(n => {
    const nid = String(n.id);
    n.isHub = hubMap.has(nid);
    n.degree = degrees[nid] || 0;
    
    if (!n.isHub) {
      // 寻找该节点连接的最强核心节点作为聚簇中心
      let bestHub = null;
      let maxHubDegree = -1;
      filteredLinks.forEach(l => {
        const s = String(typeof l.source === 'object' ? l.source.id : l.source);
        const t = String(typeof l.target === 'object' ? l.target.id : l.target);
        if (s === nid && hubMap.has(t)) {
          const h = hubMap.get(t);
          if (h.degree > maxHubDegree) { maxHubDegree = h.degree; bestHub = h; }
        } else if (t === nid && hubMap.has(s)) {
          const h = hubMap.get(s);
          if (h.degree > maxHubDegree) { maxHubDegree = h.degree; bestHub = h; }
        }
      });
      n.clusterHub = bestHub;
    } else {
      n.clusterHub = null; // 核心节点本身不被其他核心吸引
    }
  });

  currentFilterState.value = { highlightIds, highlightEdges, hideNonMatching, focusIds, focusEdges };
  simulation.nodes(filteredNodes);
  
  // 4. 优化力导向参数，防止聚簇交叠
  simulation.force('link')
    .links(filteredLinks)
    .distance(d => {
      const s = d.source;
      const t = d.target;
      // 如果是跨簇连接（两个都是 Hub，或者属于不同 Hub 的节点），拉长距离
      if (s.isHub && t.isHub) return 180; 
      if (s.clusterHub && t.clusterHub && s.clusterHub !== t.clusterHub) return 150;
      // 簇内连接保持紧凑
      return 60;
    });

  // 显著增强核心节点之间的排斥力
  simulation.force('charge', d3.forceManyBody().strength(d => {
    if (d.isHub) return -800; // 核心节点强力排斥
    return -100;
  }));

  // 添加碰撞力，核心节点拥有更大的保护半径
  simulation.force('collision', d3.forceCollide().radius(d => {
    return d.isHub ? 60 : 25;
  }));

  const linkGroup = d3.select(zoomContainerRef.value).select('.links');
  const link = linkGroup.selectAll('line')
    .data(filteredLinks, d => d.id || `${d.source.id || d.source}-${d.target.id || d.target}`);

  link.exit().remove();
  const linkEnter = link.enter().append('line')
    .attr('stroke', '#e0e0e0')
    .attr('stroke-opacity', 0.6)
    .attr('marker-end', 'url(#arrow)')
    .attr('cursor', 'pointer')
    .on('click', (event, d) => {
      event.stopPropagation();
      const sourceId = typeof d.source === 'object' ? d.source.id : d.source;
      const targetId = typeof d.target === 'object' ? d.target.id : d.target;
      addToHistory({
        id: `${sourceId}->${targetId}`,
        name: d.value || d.name || 'Relationship',
        category: d.value || d.name,
        source: sourceId,
        target: targetId,
        properties: d.properties,
        type: 'edge'
      });
      renderGraph(currentFilterState.value.highlightIds, currentFilterState.value.highlightEdges, currentFilterState.value.hideNonMatching, [], [{source: String(sourceId), target: String(targetId)}]);
    });

  const linkMerge = linkEnter.merge(link);
  linkMerge
    .attr('stroke-width', d => {
      const sourceId = String(d.source.id || d.source);
      const targetId = String(d.target.id || d.target);
      const isFocused = focusEdges.some(e => (e.source === sourceId && e.target === targetId) || (e.source === targetId && e.target === sourceId));
      return isFocused ? 2.5 : 1.5;
    })
    .attr('stroke', d => {
      const sourceId = String(d.source.id || d.source);
      const targetId = String(d.target.id || d.target);
      const isFocused = focusEdges.some(e => (e.source === sourceId && e.target === targetId) || (e.source === targetId && e.target === sourceId));
      return isFocused ? '#00ffff' : '#e0e0e0';
    });

  const labelGroup = d3.select(zoomContainerRef.value).select('.link-labels');
  const linkLabel = labelGroup.selectAll('text')
    .data(filteredLinks, d => d.id || `${d.source.id || d.source}-${d.target.id || d.target}`);

  linkLabel.exit().remove();
  const linkLabelEnter = linkLabel.enter().append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', -4)
    .text(d => d.value || d.name)
    .style('font-size', '10px')
    .style('fill', '#ccc')
    .style('pointer-events', 'none')
    .style('opacity', 0.9);

  const linkLabelMerge = linkLabelEnter.merge(linkLabel);
  linkLabelMerge.text(d => d.value || d.name);

  const nodeGroup = d3.select(zoomContainerRef.value).select('.nodes');
  const node = nodeGroup.selectAll('g')
    .data(filteredNodes, d => d.id);

  node.exit().remove();
  const nodeEnter = node.enter().append('g')
    .call(d3.drag().on('start', dragstarted).on('drag', dragged).on('end', dragended))
    .on('click', (event, d) => {
      event.stopPropagation();
      addToHistory({ 
        id: d.id, 
        name: d.name, 
        category: d.categoryName || d.category, 
        labels: d.labels || (d.category ? [d.category] : []), 
        properties: d.properties, 
        type: 'node' 
      });
      renderGraph(currentFilterState.value.highlightIds, currentFilterState.value.highlightEdges, currentFilterState.value.hideNonMatching, [String(d.id)], []);
    });

  nodeEnter.append('circle').attr('r', 10).attr('stroke', '#fff').attr('stroke-width', 1.5);
  nodeEnter.append('text').attr('dy', 18).attr('text-anchor', 'middle').text(d => d.name).style('font-size', '10px').style('pointer-events', 'none').style('fill', '#fff').style('text-shadow', '1px 1px 2px #000').style('font-weight', 'bold');

  const nodeMerge = nodeEnter.merge(node);
  nodeMerge.select('circle')
    .attr('fill', d => getColor(d.category))
    .attr('r', d => {
      if (focusIds.includes(String(d.id))) return 15;
      return d.isHub ? 14 : 10; // 核心节点稍大
    })
    .attr('stroke', d => {
      if (focusIds.includes(String(d.id))) return '#00ffff';
      return d.isHub ? '#ffd700' : '#fff'; // 核心节点金边
    })
    .attr('stroke-width', d => {
      if (focusIds.includes(String(d.id))) return 3;
      return d.isHub ? 2.5 : 1.5;
    });
    
  nodeMerge.select('text')
    .style('font-size', d => focusIds.includes(String(d.id)) ? '14px' : (d.isHub ? '12px' : '10px'))
    .style('fill', d => d.isHub ? '#fff' : '#eee');

  simulation.on('tick', () => {
    // 应用聚簇引力
    const alpha = simulation.alpha();
    filteredNodes.forEach(d => {
      if (d.clusterHub) {
        d.vx += (d.clusterHub.x - d.x) * alpha * 0.05;
        d.vy += (d.clusterHub.y - d.y) * alpha * 0.05;
      }
    });

    linkMerge.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    linkLabelMerge.attr('x', d => (d.source.x + d.target.x) / 2).attr('y', d => (d.source.y + d.target.y) / 2);
    nodeMerge.attr('transform', d => `translate(${d.x},${d.y})`);
    updateMinimap();
  });

  simulation.alpha(0.3).restart();
};

// 拖拽事件处理
const dragstarted = (event, d) => {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x; d.fy = d.y;
};
const dragged = (event, d) => { d.fx = event.x; d.fy = event.y; };
const dragended = (event, d) => {
  if (!event.active) simulation.alphaTarget(0);
  // 拖拽结束时不清除 fx/fy，使节点保持在当前位置（静止）
  d.fx = event.x;
  d.fy = event.y;
};

// 释放所有固定位置的节点，恢复力导向自动布局
const releaseFixedNodes = () => {
  nodes.value.forEach(n => {
    n.fx = null;
    n.fy = null;
  });
  if (simulation) simulation.alpha(0.3).restart();
};

// 添加到历史记录
const addToHistory = (node) => {
  const idx = nodeHistory.value.findIndex(n => n.id === node.id);
  if (idx !== -1) nodeHistory.value.splice(idx, 1);
  nodeHistory.value.unshift({ ...node, isEditing: false, editName: node.name });
};

const promoteNode = (index) => {
  const node = nodeHistory.value.splice(index, 1)[0];
  nodeHistory.value.unshift(node);
};

const removeFromHistory = (id) => {
  const idx = nodeHistory.value.findIndex(n => n.id === id);
  if (idx !== -1) nodeHistory.value.splice(idx, 1);
};

// 处理搜索
const handleSearch = async (query) => {
  if (!query) return;
  const queryLower = query.toLowerCase();
  
  // 1. 查找节点 - 优先精确匹配，再进行模糊匹配
  let foundNode = nodes.value.find(n => 
    String(n.id) === query || n.name.toLowerCase() === queryLower
  );
  
  if (!foundNode) {
    foundNode = nodes.value.find(n => n.name.toLowerCase().includes(queryLower));
  }
  
  if (foundNode) {
    // 2. 添加到历史记录
    addToHistory({ 
      id: foundNode.id, 
      name: foundNode.name, 
      category: foundNode.categoryName || foundNode.category, 
      labels: foundNode.labels || (foundNode.category ? [foundNode.category] : []), 
      properties: foundNode.properties, 
      type: 'node', 
      isEditing: false, 
      editName: foundNode.name 
    });

    // 3. 找出与该节点相关的所有路径和节点
    const relatedNodeIds = new Set();
    const relatedLinks = new Set();
    const targetId = String(foundNode.id);
    relatedNodeIds.add(targetId);

    // A. 查找所有从该节点出发可达的节点（无论路径多长）- 向下遍历
    const downstreamQueue = [targetId];
    let head = 0;
    while (head < downstreamQueue.length) {
      const nodeId = downstreamQueue[head++];
      links.value.forEach(link => {
        const s = String(typeof link.source === 'object' ? link.source.id : link.source);
        const t = String(typeof link.target === 'object' ? link.target.id : link.target);
        
        if (s === nodeId) {
          relatedLinks.add(link);
          if (!relatedNodeIds.has(t)) {
            relatedNodeIds.add(t);
            downstreamQueue.push(t);
          }
        }
      });
    }

    // B. 查找直接指向该节点的节点（路径距离为1）- 向上一步
    links.value.forEach(link => {
      const s = String(typeof link.source === 'object' ? link.source.id : link.source);
      const t = String(typeof link.target === 'object' ? link.target.id : link.target);
      
      if (t === targetId) {
        relatedLinks.add(link);
        relatedNodeIds.add(s);
      }
    });

    // 4. 仅显示该特定子图，并高亮搜索到的中心节点
    renderGraph(
      Array.from(relatedNodeIds), 
      [], 
      true, 
      [targetId], 
      [], 
      Array.from(relatedLinks)
    );
    
    // 5. 视图自动平滑移动到该节点
    const maxAttempts = 50;
    let attempts = 0;
    const tryZoom = () => {
      if (foundNode.x !== undefined && foundNode.y !== undefined && !isNaN(foundNode.x) && !isNaN(foundNode.y)) {
        if (!svgRef.value || !zoomBehavior.value) return;
        const svg = d3.select(svgRef.value);
        const width = svgRef.value.clientWidth || window.innerWidth;
        const height = svgRef.value.clientHeight || window.innerHeight;
        const scale = 1.5;
        const x = -foundNode.x * scale + width / 2;
        const y = -foundNode.y * scale + height / 2;
        const zoomIdentity = d3.zoomIdentity.translate(x, y).scale(scale);
        svg.transition().duration(750).call(zoomBehavior.value.transform, zoomIdentity);
      } else {
        attempts++;
        if (attempts < maxAttempts) setTimeout(tryZoom, 50);
      }
    };
    tryZoom();
  } else {
    alert('未找到匹配的节点');
  }
};

// 处理路径查找
const handleFindPath = async ({ start, end }) => {
  if (!start || !end) return;
  try {
    const res = await api.findPath(start, end);
    const pathNodes = res.data.path;
    const pathIds = pathNodes.map(n => String(n.id));
    
    // 找出路径中实际存在的边对象
    const pathLinks = [];
    for (let i = 0; i < pathIds.length - 1; i++) {
      const s = pathIds[i];
      const t = pathIds[i+1];
      const link = links.value.find(l => {
        const sourceId = String(typeof l.source === 'object' ? l.source.id : l.source);
        const targetId = String(typeof l.target === 'object' ? l.target.id : l.target);
        // 路径通常是有向的，但也考虑无向匹配的情况
        return (sourceId === s && targetId === t) || (sourceId === t && targetId === s);
      });
      if (link) pathLinks.push(link);
    }
    
    // 严格过滤：只显示路径节点和路径边
    renderGraph(pathIds, [], true, pathIds, [], pathLinks);
  } catch (e) { 
    alert('未找到路径'); 
  }
};

const handleCreateNode = async ({ name, label, properties }) => {
  try { await api.createNode({ name, label, properties }); fetchGraph(); } catch (e) { alert('Failed to create node'); }
};

const handleCreateEdge = async ({ sourceName, targetName, type, properties }) => {
  try {
    const sourceNode = nodes.value.find(n => String(n.id) === sourceName || n.name.toLowerCase() === sourceName.toLowerCase());
    const targetNode = nodes.value.find(n => String(n.id) === targetName || n.name.toLowerCase() === targetName.toLowerCase());
    if (!sourceNode || !targetNode) { alert('Node not found'); return; }
    await api.createRelation({ source_id: sourceNode.id, target_id: targetNode.id, type, properties });
    fetchGraph();
  } catch (e) { alert('Failed to create edge'); }
};

const handleSaveNode = async (node) => {
  try { await api.updateNode(node.id, { name: node.editName }); node.name = node.editName; node.isEditing = false; fetchGraph(); } catch (e) { alert('Failed to save'); }
};

const handleDeleteNode = async (node) => {
  if (!confirm(`Delete node #${node.id}?`)) return;
  try { await api.deleteNode(node.id); removeFromHistory(node.id); fetchGraph(); } catch (e) { alert('Failed to delete'); }
};

const handleInitDb = async () => {
  try { const response = await api.initDb(); nodeHistory.value = []; fetchGraph(); alert(response.data.message || 'Database restored'); } catch (e) { alert('Failed to init DB'); }
};

const handleSaveDb = async () => {
  try { await api.saveDb(); alert('Checkpoint saved!'); } catch (e) { alert('Failed to save'); }
};

const handleAddLabel = async ({ nodeId, label }) => {
  try { await api.addNodeLabel(nodeId, label); fetchGraph(); } catch (e) { alert('Failed to add label'); }
};

const handleRemoveLabel = async ({ nodeId, label }) => {
  try { await api.removeNodeLabel(nodeId, label); fetchGraph(); } catch (e) { alert('Failed to remove label'); }
};

const handleFilterByCategory = (category) => {
  let filteredNodes;
  if (category === '未分配标签') {
    // 过滤出没有任何标签的节点
    filteredNodes = nodes.value.filter(node => !node.labels || node.labels.length === 0);
  } else {
    filteredNodes = nodes.value.filter(node => node.labels && node.labels.includes(category));
  }
  // 传入空数组 [] 作为 specificLinks，确保只显示节点而不显示任何关系连接
  renderGraph(filteredNodes.map(n => String(n.id)), [], true, [], [], []);
};

const handleFilterByRelation = (relationType) => {
  const filteredLinks = links.value.filter(link => link.name === relationType);
  const nodeIds = new Set();
  filteredLinks.forEach(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    nodeIds.add(String(sourceId)); nodeIds.add(String(targetId));
  });
  renderGraph(Array.from(nodeIds), [], true, [], [], filteredLinks);
};

const handleShowAllRelations = () => {
  const connectedNodeIds = new Set();
  const allEdges = [];
  links.value.forEach(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    connectedNodeIds.add(String(sourceId)); connectedNodeIds.add(String(targetId));
    allEdges.push({ source: String(sourceId), target: String(targetId) });
  });
  renderGraph(Array.from(connectedNodeIds), allEdges, true);
};

const handleResetView = () => { nodeHistory.value = []; renderGraph(); };

const handleImportFiles = async ({ entityFile, relationFile }) => {
  try {
    const formData = new FormData();
    formData.append('entity_file', entityFile);
    formData.append('relation_file', relationFile);
    await api.importFiles(formData);
    nodeHistory.value = [];
    fetchGraph();
    alert('Data imported successfully!');
  } catch (e) { alert('Import failed'); }
};

onMounted(() => { initChart(); fetchGraph(); });
onUnmounted(() => {
  if (simulation) simulation.stop();
  if (resizeObserver) resizeObserver.disconnect();
});
</script>

<style scoped>
.knowledge-graph {
  width: 100%;
  height: 100%;
  display: flex;
  background-color: #1a1a2e;
  overflow: hidden;
  position: relative;
}

.main-content {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.graph-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.minimap-container {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 240px;
  height: 160px;
  background: rgba(20, 20, 30, 0.9);
  border: 1px solid #444;
  border-radius: 8px;
  overflow: hidden;
  pointer-events: none;
  z-index: 10;
}

.minimap-svg {
  width: 100%;
  height: 100%;
}

.viewport-rect {
  fill: rgba(255, 255, 255, 0.1);
  stroke: #00ffff;
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
}

.info-panel-container {
  transform: scale(0.7);
  transform-origin: top right;
  position: absolute;
  top: 20px;
  right: 20px;
}

.floating-controls {
  position: absolute;
  bottom: 20px;
  left: 20px;
  z-index: 100;
}

.control-btn {
  background: rgba(30, 30, 50, 0.9);
  color: #fff;
  border: 1px solid #00ffff;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.control-btn:hover {
  background: #00ffff;
  color: #1a1a2e;
  transform: translateY(-2px);
}

.control-btn .icon {
  font-size: 16px;
}
</style>
