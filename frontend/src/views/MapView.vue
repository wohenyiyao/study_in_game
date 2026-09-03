<template>
  <div>
    <el-page-header content="学习地图" class="header" @back="$router.push('/stats')" />
    <el-empty v-if="!chapters.length" description="暂无内容，等管理员添加章节吧" />
    <el-collapse v-for="ch in chapters" :key="ch.id" v-model="open" class="chapter">
      <el-collapse-item :name="ch.id">
        <template #title>
          <div class="ch-title">
            <span class="ch-order">第 {{ ch.order + 1 }} 章</span>
            <b>{{ ch.title }}</b>
            <span class="ch-desc">{{ ch.description }}</span>
          </div>
        </template>
        <el-row :gutter="12">
          <el-col :span="6" v-for="lv in ch.levels" :key="lv.id">
            <el-card class="level-card" :class="{ locked: !lv.unlocked }" shadow="hover"
                     :body-style="{ padding: '14px' }">
              <template #header>
                <div class="lv-head">
                  <span>关卡 {{ lv.order + 1 }}</span>
                  <el-icon v-if="lv.cleared" color="#e6a23c" size="16"><StarFilled /></el-icon>
                  <el-icon v-else-if="lv.unlocked" color="#67c23a" size="16"><VideoPlay /></el-icon>
                  <el-icon v-else color="#c0c4cc" size="16"><Lock /></el-icon>
                </div>
              </template>
              <div class="lv-title">{{ lv.title }}</div>
              <div class="lv-meta">
                <span>{{ lv.question_count }} 题</span>
                <span v-if="lv.cleared" class="stars">★★★★☆</span>
                <span v-else-if="lv.unlocked" class="unpassed">未通关</span>
                <span v-else class="locked-tip">通关前置关卡解锁</span>
              </div>
              <el-button type="primary" size="small" style="width:100%;margin-top:10px"
                         :disabled="!lv.unlocked"
                         @click="$router.push(`/level/${lv.id}`)">
                {{ lv.cleared ? '再战一次' : (lv.unlocked ? '开始闯关' : '未解锁') }}
              </el-button>
            </el-card>
          </el-col>
        </el-row>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../api/http'

const chapters = ref([])
const open = ref([])
const starsOf = (acc) => (acc >= 0.9 ? 3 : acc >= 0.75 ? 2 : acc >= 0.6 ? 1 : 0)

async function load() {
  chapters.value = await http.get('/map')
  // 默认展开第一/二章（有可玩关卡的）
  open.value = chapters.value.map((c) => c.id)
}
onMounted(load)
</script>

<style scoped>
.header { margin-bottom: 16px; }
.chapter { margin-bottom: 14px; background: #fff; border-radius: 8px; }
.ch-title { display: flex; align-items: baseline; gap: 10px; }
.ch-order { color: #1f6feb; font-weight: 700; font-size: 13px; }
.ch-desc { color: #909399; font-size: 12px; margin-left: 8px; }
.level-card.locked { opacity: 0.55; }
.lv-head { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #666; }
.lv-title { font-weight: 600; margin-bottom: 6px; }
.lv-meta { font-size: 12px; color: #909399; }
.stars { color: #e6a23c; letter-spacing: 2px; }
.unpassed { color: #e6a23c; }
.locked-tip { font-size: 11px; }
</style>
