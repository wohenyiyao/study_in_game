<template>
  <div class="map-page">
    <!-- 页头 -->
    <div class="page-head">
      <div class="head-left">
        <h1 class="head-title">🗺️ 学习地图</h1>
        <p class="head-sub">选择一个科目，按顺序闯关，通关上一关解锁下一关！</p>
      </div>
      <div class="head-right">
        <div v-if="active" class="chip"><span class="chip-dot indigo"></span>通关 <b>{{ activeCleared }}/{{ activeTotal }}</b></div>
        <div v-if="active" class="chip"><span class="chip-dot gold"></span>累计 <b>{{ activeStars }}</b> ⭐</div>
        <el-button text class="to-stats" @click="$router.push('/stats')">我的战绩 →</el-button>
      </div>
    </div>

    <!-- 科目切换（Python / Java / 面试题库…） -->
    <div v-if="subjects.length > 1" class="subject-tabs">
      <button v-for="s in subjects" :key="s.id" class="subject-tab"
              :class="{ active: s.code === activeCode }" @click="activeCode = s.code">
        <span class="sub-ico">{{ s.icon }}</span>
        <span class="sub-name">{{ s.name }}</span>
        <span class="sub-mini">{{ clearedIn(s) }}/{{ levelIn(s) }} 关</span>
      </button>
    </div>

    <template v-if="active">
      <div class="legend">
        <span><i class="dot d-play"></i>可挑战</span>
        <span><i class="dot d-done"></i>已通关</span>
        <span><i class="dot d-lock"></i>未解锁</span>
      </div>

      <section v-for="(ch, ci) in active.chapters" :key="ch.id" class="chapter-block">
        <!-- 章节横幅 -->
        <div class="chapter-banner">
          <span class="ch-no">第 {{ ci + 1 }} 章</span>
          <div class="ch-text">
            <h2>{{ ch.title }}</h2>
            <p v-if="ch.description">{{ ch.description }}</p>
          </div>
          <span class="ch-stats">{{ clearedInChapter(ch) }}/{{ ch.levels.length }} 关通关</span>
        </div>

        <!-- 关卡卡片网格 -->
        <div class="lv-grid">
          <div v-for="lv in ch.levels" :key="lv.id" class="lv-card" :class="stateOf(lv)">
            <div class="lv-top">
              <span class="lv-no">LEVEL {{ lv.order + 1 }}</span>
              <span class="lv-ico">{{ icoOf(lv) }}</span>
            </div>
            <div class="lv-title">{{ lv.title }}</div>
            <div class="lv-meta">{{ lv.question_count }} 题 · 正确率 ≥ {{ Math.round(lv.pass_ratio * 100) }}% 通关</div>

            <div v-if="lv.cleared" class="lv-stars">
              <span v-for="i in 3" :key="i" class="star" :class="{ on: i <= lv.stars }">★</span>
              <span class="lv-acc">最佳 {{ Math.round(lv.best_accuracy * 100) }}%</span>
            </div>
            <div v-else-if="lv.unlocked" class="lv-hint">就差临门一脚，冲！</div>
            <div v-else class="lv-hint">通关前置关卡解锁</div>

            <el-button v-if="lv.unlocked" type="primary" class="go-btn"
                       @click="$router.push(`/level/${lv.id}`)">
              {{ lv.cleared ? '再战一次' : '开始闯关' }}
            </el-button>
            <el-button v-else class="go-btn" disabled>未解锁</el-button>
          </div>
        </div>
      </section>
    </template>

    <el-empty v-else-if="!subjects.length" description="暂无科目内容，等管理员添加吧" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import http from '../api/http'

const subjects = ref([])
const activeCode = ref(null)

const active = computed(() =>
  subjects.value.find((s) => s.code === activeCode.value) || subjects.value[0] || null)

const levelIn = (s) => s.chapters.reduce((n, c) => n + c.levels.length, 0)
const clearedIn = (s) =>
  s.chapters.reduce((n, c) => n + c.levels.filter((l) => l.cleared).length, 0)
const clearedInChapter = (ch) => ch.levels.filter((l) => l.cleared).length

const activeCleared = computed(() => (active.value ? clearedIn(active.value) : 0))
const activeTotal = computed(() => (active.value ? levelIn(active.value) : 0))
const activeStars = computed(() =>
  active.value
    ? active.value.chapters.reduce(
        (n, c) => n + c.levels.reduce((m, l) => m + (l.stars || 0), 0), 0)
    : 0)

const stateOf = (lv) => (lv.cleared ? 'cleared' : lv.unlocked ? 'unlocked' : 'locked')
const icoOf = (lv) => (lv.cleared ? '⭐' : lv.unlocked ? '▶' : '🔒')

async function load() {
  subjects.value = await http.get('/map')
  if (subjects.value.length && !activeCode.value) activeCode.value = subjects.value[0].code
}
onMounted(load)
</script>

<style scoped>
.map-page {
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeUp 0.4s ease both;
}

/* ---------- 页头 ---------- */
.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 16px;
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
.head-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid rgba(99, 102, 241, 0.12);
  box-shadow: 0 4px 12px -8px rgba(35, 37, 63, 0.2);
  font-size: 12.5px;
  color: #565c7d;
}
.chip b {
  color: #23253f;
  font-size: 13.5px;
}
.chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.chip-dot.indigo {
  background: var(--lq-grad);
}
.chip-dot.gold {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}
.to-stats {
  color: #6366f1;
  font-weight: 600;
}

/* ---------- 科目切换 ---------- */
.subject-tabs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.subject-tab {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 9px 16px;
  border: 1.5px solid rgba(99, 102, 241, 0.14);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.85);
  cursor: pointer;
  font-family: inherit;
  font-size: 14px;
  color: #565c7d;
  transition: all 0.18s ease;
}
.subject-tab:hover {
  border-color: #a5b4fc;
  transform: translateY(-1px);
}
.subject-tab.active {
  background: var(--lq-grad);
  border-color: transparent;
  color: #fff;
  font-weight: 700;
  box-shadow: 0 10px 20px -8px rgba(99, 102, 241, 0.7);
}
.sub-ico {
  font-size: 18px;
}
.sub-mini {
  font-size: 11px;
  opacity: 0.75;
}

/* 图例 */
.legend {
  display: flex;
  gap: 18px;
  margin: 0 0 18px 2px;
  font-size: 12px;
  color: #8a90b5;
}
.legend .dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 5px;
  vertical-align: -1px;
}
.d-play {
  background: var(--lq-grad);
}
.d-done {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}
.d-lock {
  background: #cfd4ec;
}

/* ---------- 章节块 ---------- */
.chapter-block {
  margin-bottom: 26px;
}
.chapter-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 18px;
  background: linear-gradient(100deg, rgba(255, 255, 255, 0.96), rgba(245, 246, 255, 0.92));
  border: 1px solid rgba(99, 102, 241, 0.1);
  box-shadow: 0 10px 26px -18px rgba(35, 37, 63, 0.35);
}
.ch-no {
  flex: none;
  padding: 8px 14px;
  border-radius: 12px;
  background: var(--lq-grad);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 1px;
  box-shadow: 0 8px 16px -6px rgba(99, 102, 241, 0.6);
}
.ch-text {
  flex: 1;
  min-width: 0;
}
.ch-text h2 {
  margin: 0;
  font-size: 18px;
  color: #23253f;
}
.ch-text p {
  margin: 4px 0 0;
  font-size: 12.5px;
  color: #9aa0c4;
}
.ch-stats {
  flex: none;
  font-size: 12px;
  color: #8b5cf6;
  background: var(--lq-grad-soft);
  padding: 6px 12px;
  border-radius: 999px;
  font-weight: 600;
}

/* ---------- 关卡卡片 ---------- */
.lv-grid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(232px, 1fr));
  gap: 14px;
}
.lv-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 16px;
  padding: 16px 16px 14px;
  border: 1px solid rgba(99, 102, 241, 0.09);
  box-shadow: 0 6px 18px -14px rgba(35, 37, 63, 0.3);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.lv-card.unlocked:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 34px -18px rgba(99, 102, 241, 0.55);
}
.lv-card.cleared {
  background: linear-gradient(180deg, #fffdf6, #ffffff);
  border-color: rgba(251, 191, 36, 0.35);
}
.lv-card.cleared:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 34px -18px rgba(245, 158, 11, 0.5);
}
.lv-card.locked {
  background: #f5f6fc;
  border: 1.5px dashed #dfe3f3;
  box-shadow: none;
}

.lv-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.lv-no {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1.6px;
  color: #8b5cf6;
}
.lv-card.locked .lv-no {
  color: #b7bce0;
}
.lv-ico {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  font-size: 18px;
  border-radius: 13px;
}
.lv-card.unlocked .lv-ico {
  background: var(--lq-grad);
  color: #fff;
  font-size: 15px;
  box-shadow: 0 8px 16px -6px rgba(99, 102, 241, 0.6);
}
.lv-card.cleared .lv-ico {
  background: linear-gradient(135deg, #fde68a, #fbbf24);
}
.lv-card.locked .lv-ico {
  background: #e6e9f6;
}

.lv-title {
  margin: 12px 0 6px;
  font-size: 16px;
  font-weight: 700;
  color: #23253f;
}
.lv-card.locked .lv-title {
  color: #a3a9cc;
}
.lv-meta {
  font-size: 12px;
  color: #9aa0c4;
  line-height: 1.6;
}

.lv-stars {
  display: flex;
  align-items: center;
  margin-top: 12px;
  gap: 3px;
}
.star {
  font-size: 18px;
  color: #e6e9f6;
}
.star.on {
  color: #f5b301;
  text-shadow: 0 2px 6px rgba(245, 179, 1, 0.4);
}
.lv-acc {
  margin-left: auto;
  font-size: 11.5px;
  font-weight: 700;
  color: #f59e0b;
  background: #fff7e6;
  padding: 3px 8px;
  border-radius: 999px;
}
.lv-hint {
  margin-top: 12px;
  font-size: 12px;
  color: #6366f1;
  font-weight: 600;
}
.lv-card.locked .lv-hint {
  color: #a3a9cc;
  font-weight: 400;
}

.go-btn {
  width: 100%;
  margin-top: 14px;
  border-radius: 10px;
  font-weight: 600;
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 640px) {
  .head-right {
    width: 100%;
  }
}
</style>
