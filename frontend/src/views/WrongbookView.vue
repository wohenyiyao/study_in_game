<template>
  <div>
    <el-page-header content="错题本" @back="$router.push('/map')" class="header" />
    <el-empty v-if="!list.length" description="没有错题，继续保持！" />
    <el-card v-for="w in list" :key="w.id" class="w-card">
      <div class="w-top">
        <el-tag size="small" type="warning">关卡：{{ w.level_title }}</el-tag>
        <span class="w-time">{{ new Date(w.created_at).toLocaleString() }}</span>
      </div>
      <div class="w-q">{{ w.content }}</div>
      <div class="w-opts">
        <div v-for="(opt, oi) in w.options" :key="oi" class="w-opt"
             :class="{ right: oi === w.answer_index, wrong: oi === w.your_answer && oi !== w.answer_index }">
          {{ String.fromCharCode(65 + oi) }}. {{ opt }}
          <el-icon v-if="oi === w.answer_index" color="#67c23a"><CircleCheckFilled /></el-icon>
          <el-icon v-else-if="oi === w.your_answer" color="#f56c6c"><CircleCloseFilled /></el-icon>
        </div>
      </div>
      <div class="w-exp" v-if="w.explanation">💡 {{ w.explanation }}</div>
      <div class="w-actions">
        <el-button size="small" @click="$router.push(`/level/${w.level_id}`)">再练一遍</el-button>
        <el-button size="small" type="danger" plain @click="remove(w)">移除</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const list = ref([])
async function load() { list.value = await http.get('/wrongbook') }
async function remove(w) {
  await http.delete(`/wrongbook/${w.question_id}`)
  ElMessage.success('已移除')
  load()
}
onMounted(load)
</script>

<style scoped>
.header { margin-bottom: 16px; }
.w-card { margin-bottom: 14px; }
.w-top { display: flex; justify-content: space-between; margin-bottom: 8px; }
.w-time { font-size: 12px; color: #aaa; }
.w-q { font-weight: 600; margin-bottom: 8px; }
.w-opt { padding: 6px 10px; border-radius: 6px; margin: 4px 0; display: flex; gap: 8px; align-items: center; }
.w-opt.right { background: #f0f9eb; color: #529b2e; }
.w-opt.wrong { background: #fef0f0; color: #d03050; }
.w-exp { margin-top: 8px; font-size: 13px; color: #666; line-height: 1.7; }
.w-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 6px; }
</style>
