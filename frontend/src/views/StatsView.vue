<template>
  <div>
    <el-page-header content="我的战绩" @back="$router.push('/map')" class="header" />
    <el-row :gutter="16">
      <el-col :span="6" v-for="card in cards" :key="card.label">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-num" :style="{ color: card.color }">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="map-progress" shadow="never">
      <template #header>关卡进度</template>
      <el-table :data="rows">
        <el-table-column label="章节" prop="chapter" width="160" />
        <el-table-column label="关卡" prop="level" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag v-if="row.cleared" type="success">已通关</el-tag>
            <el-tag v-else-if="row.unlocked" type="warning">未通关</el-tag>
            <el-tag v-else type="info">未解锁</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="星星" width="120">
          <template #default="{ row }">
            <span v-if="row.stars">⭐ x{{ row.stars }}</span>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="最佳正确率" width="120">
          <template #default="{ row }">
            {{ row.best_accuracy ? Math.round(row.best_accuracy * 100) + '%' : '—' }}
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button v-if="row.unlocked" size="small" link type="primary"
                       @click="$router.push(`/level/${row.id}`)">去挑战</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import http from '../api/http'

const stats = ref({})
const map = ref([])

const cards = computed(() => [
  { label: '总关卡', value: stats.value.total_levels ?? 0, color: '#909399' },
  { label: '已通关', value: stats.value.cleared_levels ?? 0, color: '#67c23a' },
  { label: '累计星星', value: stats.value.total_stars ?? 0, color: '#e6a23c' },
  { label: '错题数', value: stats.value.wrong_count ?? 0, color: '#f56c6c' }
])

const rows = computed(() =>
  map.value.flatMap((ch) =>
    ch.levels.map((lv) => ({
      ...lv,
      chapter: `第 ${ch.order + 1} 章 ${ch.title}`,
      level: `关卡 ${lv.order + 1} ${lv.title}`
    }))
  )
)

async function load() {
  ;[stats.value, map.value] = await Promise.all([http.get('/stats'), http.get('/map')])
}
onMounted(load)
</script>

<style scoped>
.header { margin-bottom: 16px; }
.stat-card { text-align: center; margin-bottom: 16px; }
.stat-num { font-size: 32px; font-weight: 800; }
.stat-label { color: #909399; margin-top: 4px; font-size: 13px; }
.map-progress { margin-top: 8px; }
</style>
