<template>
  <div class="stats-page">
    <!-- 页头 -->
    <div class="page-head">
      <div class="head-left">
        <h1 class="head-title">🏆 我的战绩</h1>
        <p class="head-sub">每一次通关，都算数。</p>
      </div>
      <el-button text class="to-map" @click="$router.push('/map')">← 返回地图</el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-grid">
      <div v-for="card in cards" :key="card.label" class="stat-card">
        <span class="stat-ico" :style="{ background: card.bg }">{{ card.emoji }}</span>
        <div class="stat-body">
          <div class="stat-num" :style="{ color: card.color }">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </div>
      </div>
    </div>

    <!-- 冒险进度 -->
    <div class="progress-hero">
      <div class="hero-text">
        <span class="hero-title">🗺️ 冒险进度</span>
        <span class="hero-sub">已通关 {{ stats.cleared_levels ?? 0 }} / {{ stats.total_levels ?? 0 }} 关</span>
      </div>
      <div class="hero-bar">
        <i :style="{ width: percent + '%' }"></i>
      </div>
      <div class="hero-num">{{ percent }}%</div>
    </div>

    <!-- 关卡进度明细 -->
    <div class="table-card">
      <div class="table-title">📋 关卡明细</div>
      <el-table :data="rows" class="lq-table" :header-cell-style="{ background: '#f6f7ff', color: '#5a5f86' }">
        <el-table-column label="科目" width="150">
          <template #default="{ row }">
            <el-tag effect="plain" size="small">{{ row.subject }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="章节" prop="chapter" min-width="150" show-overflow-tooltip />
        <el-table-column label="关卡" prop="level" min-width="150" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.cleared" type="success" effect="light" round>已通关</el-tag>
            <el-tag v-else-if="row.unlocked" type="warning" effect="light" round>未通关</el-tag>
            <el-tag v-else type="info" effect="light" round>未解锁</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="星星" width="110">
          <template #default="{ row }">
            <span v-if="row.stars" class="star-cells">
              <span v-for="i in 3" :key="i" class="sc" :class="{ on: i <= row.stars }">★</span>
            </span>
            <span v-else class="dim">—</span>
          </template>
        </el-table-column>
        <el-table-column label="最佳正确率" width="110">
          <template #default="{ row }">
            <span class="acc" v-if="row.best_accuracy">{{ Math.round(row.best_accuracy * 100) }}%</span>
            <span v-else class="dim">—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90">
          <template #default="{ row }">
            <el-button v-if="row.unlocked" link type="primary" size="small"
                       @click="$router.push(`/level/${row.id}`)">去挑战</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import http from '../api/http'

const stats = ref({})
const map = ref([])

const cards = computed(() => [
  { label: '总关卡', value: stats.value.total_levels ?? 0, color: '#6366f1', emoji: '🗺️', bg: 'linear-gradient(135deg,#c7d2fe,#818cf8)' },
  { label: '已通关', value: stats.value.cleared_levels ?? 0, color: '#10b981', emoji: '🏅', bg: 'linear-gradient(135deg,#a7f3d0,#34d399)' },
  { label: '累计星星', value: stats.value.total_stars ?? 0, color: '#f59e0b', emoji: '⭐', bg: 'linear-gradient(135deg,#fde68a,#fbbf24)' },
  { label: '错题数', value: stats.value.wrong_count ?? 0, color: '#f43f5e', emoji: '📕', bg: 'linear-gradient(135deg,#fecdd3,#fb7185)' }
])

const percent = computed(() => {
  const t = stats.value.total_levels ?? 0
  if (!t) return 0
  return Math.round(((stats.value.cleared_levels ?? 0) / t) * 100)
})

const rows = computed(() =>
  map.value.flatMap((s) =>
    s.chapters.flatMap((ch) =>
      ch.levels.map((lv) => ({
        ...lv,
        subject: `${s.icon} ${s.name}`,
        chapter: `第 ${ch.order + 1} 章 ${ch.title}`,
        level: `关卡 ${lv.order + 1} ${lv.title}`
      }))
    )
  )
)

async function load() {
  ;[stats.value, map.value] = await Promise.all([http.get('/stats'), http.get('/map')])
}
onMounted(load)
</script>

<style scoped>
.stats-page {
  max-width: 1100px;
  margin: 0 auto;
  animation: fadeUp 0.4s ease both;
}
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}
.head-title {
  margin: 0;
  font-size: 26px;
  font-weight: 800;
  color: #23253f;
}
.head-sub {
  margin: 6px 0 0;
  font-size: 13.5px;
  color: #9aa0c4;
}
.to-map {
  color: #6366f1;
  font-weight: 600;
}

/* 统计卡片 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(99, 102, 241, 0.09);
  box-shadow: 0 8px 22px -16px rgba(35, 37, 63, 0.35);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 30px -18px rgba(99, 102, 241, 0.5);
}
.stat-ico {
  width: 52px;
  height: 52px;
  flex: none;
  display: grid;
  place-items: center;
  font-size: 24px;
  border-radius: 15px;
  box-shadow: inset 0 -6px 12px -8px rgba(0, 0, 0, 0.18);
}
.stat-num {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.1;
}
.stat-label {
  margin-top: 3px;
  font-size: 12.5px;
  color: #9aa0c4;
}

/* 冒险进度 */
.progress-hero {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
  background: #fff;
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 18px;
  border: 1px solid rgba(99, 102, 241, 0.09);
  box-shadow: 0 8px 22px -16px rgba(35, 37, 63, 0.35);
}
.hero-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: none;
}
.hero-title {
  font-weight: 800;
  font-size: 15px;
  color: #34385c;
}
.hero-sub {
  font-size: 12px;
  color: #9aa0c4;
}
.hero-bar {
  flex: 1;
  min-width: 160px;
  height: 12px;
  border-radius: 8px;
  background: #e9ecf8;
  overflow: hidden;
}
.hero-bar i {
  display: block;
  height: 100%;
  border-radius: 8px;
  background: var(--lq-grad);
  transition: width 0.6s ease;
}
.hero-num {
  flex: none;
  font-size: 20px;
  font-weight: 800;
  color: #6366f1;
}

/* 明细表 */
.table-card {
  background: #fff;
  border-radius: 16px;
  padding: 18px 18px 8px;
  border: 1px solid rgba(99, 102, 241, 0.09);
  box-shadow: 0 8px 22px -16px rgba(35, 37, 63, 0.35);
  overflow: hidden;
}
.table-title {
  font-weight: 800;
  font-size: 15px;
  color: #34385c;
  margin-bottom: 12px;
}
.star-cells {
  display: inline-flex;
  gap: 2px;
}
.sc {
  font-size: 15px;
  color: #e5e4f2;
}
.sc.on {
  color: #f5b301;
  text-shadow: 0 1px 4px rgba(245, 179, 1, 0.5);
}
.acc {
  color: #10b981;
  font-weight: 700;
  background: #ecfdf5;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
}
.dim {
  color: #c3c8e0;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
