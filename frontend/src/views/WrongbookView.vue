<template>
  <div class="wrong-page">
    <!-- 页头 -->
    <div class="page-head">
      <div class="head-left">
        <h1 class="head-title">🗂️ 错题本</h1>
        <p class="head-sub">共 {{ list.length }} 道错题 · 消灭它们，就离通关更近一步</p>
      </div>
      <el-button text class="to-map" @click="$router.push('/map')">← 返回地图</el-button>
    </div>

    <div v-if="!list.length" class="empty-wrap">
      <div class="empty-emoji">🎉</div>
      <p class="empty-text">没有错题，继续保持！</p>
    </div>

    <div v-for="w in list" :key="w.id" class="w-card">
      <div class="w-top">
        <span class="w-source">🎯 {{ w.level_title }}</span>
        <span class="w-time">{{ new Date(w.created_at).toLocaleString() }}</span>
      </div>
      <div class="w-q">{{ w.content }}</div>
      <div class="w-opts">
        <div v-for="(opt, oi) in w.options" :key="oi" class="w-opt"
             :class="{ right: oi === w.answer_index, wrong: oi === w.your_answer && oi !== w.answer_index }">
          <span class="w-letter">{{ String.fromCharCode(65 + oi) }}</span>
          <span class="w-opt-text">{{ opt }}</span>
          <el-icon v-if="oi === w.answer_index" color="#10b981"><CircleCheckFilled /></el-icon>
          <el-icon v-else-if="oi === w.your_answer" color="#f43f5e"><CircleCloseFilled /></el-icon>
        </div>
      </div>
      <div class="w-exp" v-if="w.explanation">💡 {{ w.explanation }}</div>
      <div class="w-actions">
        <el-button size="small" type="primary" plain @click="$router.push(`/level/${w.level_id}`)">
          🔁 再练一遍
        </el-button>
        <el-button size="small" type="danger" text @click="remove(w)">移除</el-button>
      </div>
    </div>
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
  ElMessage.success('已移除，加油！')
  load()
}
onMounted(load)
</script>

<style scoped>
.wrong-page {
  max-width: 860px;
  margin: 0 auto;
  padding-bottom: 30px;
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

/* 空状态 */
.empty-wrap {
  text-align: center;
  padding: 60px 0;
  background: #fff;
  border-radius: 18px;
  border: 1px dashed rgba(99, 102, 241, 0.2);
}
.empty-emoji {
  font-size: 52px;
}
.empty-text {
  color: #9aa0c4;
  font-size: 14px;
}

/* 错题卡片 */
.w-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px 18px;
  margin-bottom: 14px;
  border: 1px solid rgba(99, 102, 241, 0.09);
  border-left: 5px solid #fb7185;
  box-shadow: 0 8px 22px -16px rgba(35, 37, 63, 0.35);
}
.w-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}
.w-source {
  font-size: 12px;
  font-weight: 700;
  color: #f43f5e;
  background: #fff1f2;
  padding: 4px 12px;
  border-radius: 999px;
}
.w-time {
  font-size: 12px;
  color: #b0b5d9;
}
.w-q {
  margin-top: 10px;
  font-size: 15px;
  font-weight: 600;
  color: #34385c;
  line-height: 1.75;
  white-space: pre-wrap;
}

.w-opts {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.w-opt {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13.5px;
  padding: 9px 13px;
  border-radius: 11px;
  background: #f7f8fd;
  color: #565c7d;
  border: 1.5px solid transparent;
}
.w-opt.right {
  background: #ecfdf5;
  border-color: rgba(16, 185, 129, 0.35);
  color: #047857;
}
.w-opt.wrong {
  background: #fff1f2;
  border-color: rgba(244, 63, 94, 0.35);
  color: #be123c;
}
.w-letter {
  width: 24px;
  height: 24px;
  flex: none;
  display: grid;
  place-items: center;
  border-radius: 7px;
  font-weight: 800;
  font-size: 12.5px;
  background: #e6e9f6;
  color: #6b7093;
}
.w-opt.right .w-letter {
  background: #a7f3d0;
  color: #047857;
}
.w-opt.wrong .w-letter {
  background: #fecdd3;
  color: #be123c;
}
.w-opt-text {
  flex: 1;
}

.w-exp {
  margin-top: 12px;
  padding: 11px 14px;
  border-radius: 11px;
  background: #f6f7ff;
  border: 1px dashed rgba(99, 102, 241, 0.25);
  font-size: 13px;
  color: #5a5f86;
  line-height: 1.8;
}

.w-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  margin-top: 12px;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
