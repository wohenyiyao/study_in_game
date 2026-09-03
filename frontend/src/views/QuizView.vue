<template>
  <div class="quiz-page">
    <!-- 顶部导航 -->
    <div class="quiz-head">
      <el-button text class="back-btn" @click="back">
        <el-icon><ArrowLeft /></el-icon> 返回地图
      </el-button>
      <div class="head-main">
        <h1 class="head-title">{{ data.title || '闯关' }}</h1>
        <div class="head-chips" v-if="questions.length">
          <span class="meta-chip">📝 {{ questions.length }} 道题</span>
          <span class="meta-chip">答题进度 {{ answeredCount }}/{{ questions.length }}</span>
          <div class="head-progress">
            <i :style="{ width: (answeredCount / questions.length) * 100 + '%' }"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- 答题阶段 -->
    <el-card v-if="!result" v-for="(q, i) in questions" :key="q.id" class="q-card" shadow="never">
      <div class="q-top">
        <span class="q-no">{{ i + 1 }}</span>
        <span class="q-type">单选</span>
      </div>
      <div class="q-text">{{ q.content }}</div>
      <div class="q-opts">
        <div v-for="(opt, oi) in q.options" :key="oi" class="q-opt"
             :class="{ on: answers[i] === oi }" @click="answers[i] = oi">
          <span class="opt-letter">{{ String.fromCharCode(65 + oi) }}</span>
          <span class="opt-text">{{ opt }}</span>
          <el-icon v-if="answers[i] === oi" class="opt-check"><CircleCheckFilled /></el-icon>
        </div>
      </div>
    </el-card>

    <div v-if="!result" class="quiz-actions">
      <el-button type="primary" size="large" class="submit-btn"
                 :disabled="!allAnswered" :loading="submitting" @click="submit">
        交卷判分
      </el-button>
    </div>

    <!-- 结果阶段 -->
    <div v-else class="result-wrap">
      <div class="result-hero" :class="result.passed ? 'pass' : 'fail'">
        <div class="big-emoji">{{ result.passed ? '🎉' : '😤' }}</div>
        <h2 class="result-title">
          {{ result.passed ? `通关成功！获得 ${result.stars} 颗星` : '还差一点点，再来一次' }}
        </h2>
        <p class="result-sub" v-if="!result.passed">正确率未达通关线，先看看下面错在哪，再战一轮！</p>

        <div v-if="result.passed" class="result-stars">
          <span v-for="s in 3" :key="s" class="result-star" :class="{ on: s <= result.stars }"
                :style="{ animationDelay: s * 0.15 + 's' }">★</span>
        </div>

        <div class="score-chips">
          <span class="score-chip ok">正确 {{ result.correct }} / {{ result.total }}</span>
          <span class="score-chip">{{ Math.round(result.accuracy * 100) }}% 正确率</span>
          <span class="score-chip" v-if="result.passed">⭐ {{ result.stars }} 星</span>
        </div>

        <div class="result-btns">
          <el-button v-if="result.passed" type="primary" size="large" @click="nextLevel">
            下一关 →
          </el-button>
          <el-button size="large" plain @click="resetQuiz">
            {{ result.passed ? '再玩一次' : '重新挑战' }}
          </el-button>
          <el-button text @click="back">返回地图</el-button>
        </div>
      </div>

      <div class="detail-title">📖 逐题讲解</div>
      <div v-for="(d, i) in result.details" :key="d.question_id" class="detail-card"
           :class="d.is_correct ? 'ok' : 'bad'">
        <div class="d-head">
          <span class="d-no">第 {{ i + 1 }} 题</span>
          <el-tag :type="d.is_correct ? 'success' : 'danger'" effect="light" round size="small">
            {{ d.is_correct ? '✓ 答对' : '✗ 答错' }}
          </el-tag>
        </div>
        <div class="d-text">{{ d.content }}</div>
        <div class="d-opts">
          <div v-for="(opt, oi) in d.options" :key="oi" class="d-opt"
               :class="{ right: oi === d.correct_index,
                         wrong: oi === d.your && oi !== d.correct_index }">
            <span class="d-letter">{{ String.fromCharCode(65 + oi) }}</span>
            <span>{{ opt }}</span>
            <el-icon v-if="oi === d.correct_index" color="#10b981"><CircleCheckFilled /></el-icon>
            <el-icon v-else-if="oi === d.your" color="#f43f5e"><CircleCloseFilled /></el-icon>
          </div>
        </div>
        <div class="d-exp" v-if="d.explanation">💡 {{ d.explanation }}</div>
      </div>
    </div>

    <!-- AI 助教 -->
    <button class="tutor-fab" title="问 AI 助教" @click="tutorVisible = true">🤖</button>
    <el-drawer v-model="tutorVisible" class="tutor-drawer" size="420px"
               title="🤖 AI 助教 · 问思路不问答案">
      <div class="chat-box">
        <div v-for="(m, i) in chat" :key="i" class="chat-msg" :class="m.role">
          <span v-if="m.role === 'ai'" class="chat-avatar">🤖</span>
          <div class="bubble">{{ m.content }}</div>
        </div>
      </div>
      <div class="chat-input">
        <el-input v-model="chatInput" placeholder="问一道题 / 求提示…" @keyup.enter="sendChat" />
        <el-button type="primary" :loading="chatting" @click="sendChat">发送</el-button>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const route = useRoute()
const router = useRouter()
const levelId = Number(route.params.id)

const data = ref({ title: '' })
const questions = ref([])
const answers = ref([])
const submitting = ref(false)
const result = ref(null)

const answeredCount = computed(() =>
  questions.value.reduce((n, _q, i) => n + (answers.value[i] !== undefined && answers.value[i] !== null ? 1 : 0), 0))
const allAnswered = computed(() =>
  questions.value.length > 0 && answers.value.every((a) => a !== undefined && a !== null))

const tutorVisible = ref(false)
const chatInput = ref('')
const chatting = ref(false)
const chat = ref([{ role: 'ai', content: '你好，我是 AI 助教。可以问我某道题为什么错、给个思路提示，但不会直接告诉你答案哦～' }])

async function load() {
  const d = await http.get(`/levels/${levelId}/start`)
  data.value = d
  questions.value = d.questions
  answers.value = Array(d.questions.length).fill(null)
}
async function submit() {
  submitting.value = true
  try {
    result.value = await http.post(`/levels/${levelId}/submit`, { answers: answers.value })
    if (!result.value.passed) ElMessage.warning(`正确 ${result.value.correct}/${result.value.total}，未达通关线`)
  } finally { submitting.value = false }
}
function resetQuiz() { result.value = null; answers.value = questions.value.map(() => null) }
async function nextLevel() {
  const map = await http.get('/map')
  const all = map.flatMap((s) => s.chapters.flatMap((c) => c.levels))
  const idx = all.findIndex((l) => l.id === levelId)
  const next = all[idx + 1]
  if (next) router.push(`/level/${next.id}`)
  else { ElMessage.success('恭喜你完成了全部关卡！'); router.push('/map') }
}
function back() { router.push('/map') }

async function sendChat() {
  const msg = chatInput.value.trim()
  if (!msg || chatting.value) return
  chat.value.push({ role: 'user', content: msg })
  chatInput.value = ''
  chatting.value = true
  try {
    const res = await http.post('/assistant/chat', { message: msg, level_id: levelId })
    chat.value.push({ role: 'ai', content: res.reply })
  } catch (e) { /* 拦截器已提示 */ }
  finally { chatting.value = false }
}

onMounted(load)
</script>

<style scoped>
.quiz-page {
  max-width: 860px;
  margin: 0 auto;
  padding-bottom: 40px;
  animation: fadeUp 0.4s ease both;
}

/* ---------- 顶栏 ---------- */
.quiz-head {
  margin-bottom: 20px;
}
.back-btn {
  color: #8a90b5;
  font-size: 13px;
  padding: 0;
  margin-bottom: 8px;
}
.back-btn:hover {
  color: #6366f1;
}
.head-title {
  margin: 0;
  font-size: 25px;
  font-weight: 800;
  color: #23253f;
}
.head-chips {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  flex-wrap: wrap;
}
.meta-chip {
  font-size: 12.5px;
  color: #8a90b5;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(99, 102, 241, 0.12);
  padding: 5px 12px;
  border-radius: 999px;
}
.head-progress {
  flex: 1;
  min-width: 140px;
  height: 8px;
  border-radius: 8px;
  background: #e6e9f6;
  overflow: hidden;
}
.head-progress i {
  display: block;
  height: 100%;
  border-radius: 8px;
  background: var(--lq-grad);
  transition: width 0.3s ease;
}

/* ---------- 题目卡片 ---------- */
.q-card {
  border-radius: 18px;
  border: 1px solid rgba(99, 102, 241, 0.09);
  margin-bottom: 16px;
  box-shadow: 0 8px 22px -16px rgba(35, 37, 63, 0.35);
}
.q-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.q-no {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  background: var(--lq-grad);
  color: #fff;
  font-weight: 800;
  font-size: 14px;
  box-shadow: 0 6px 12px -4px rgba(99, 102, 241, 0.6);
}
.q-type {
  font-size: 11px;
  color: #9aa0c4;
  background: #f0f1fb;
  padding: 3px 10px;
  border-radius: 999px;
}
.q-text {
  font-size: 15.5px;
  line-height: 1.75;
  color: #34385c;
  white-space: pre-wrap;
  font-weight: 500;
}

.q-opts {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 16px;
}
.q-opt {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 13px;
  border: 1.5px solid #e6e9f5;
  background: #fbfbfe;
  cursor: pointer;
  transition: all 0.16s ease;
  font-size: 14px;
  color: #4b4f73;
}
.q-opt:hover {
  border-color: #a5b4fc;
  background: #f6f7ff;
  transform: translateX(2px);
}
.q-opt.on {
  border-color: #6366f1;
  background: #eef2ff;
  color: #3f3fae;
  box-shadow: 0 6px 16px -8px rgba(99, 102, 241, 0.5);
}
.opt-letter {
  width: 28px;
  height: 28px;
  flex: none;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: #e6e9f6;
  color: #6b7093;
  font-weight: 800;
  font-size: 13px;
  transition: all 0.16s ease;
}
.q-opt.on .opt-letter {
  background: var(--lq-grad);
  color: #fff;
}
.opt-text {
  flex: 1;
}
.opt-check {
  color: #6366f1;
  font-size: 18px;
}

/* 交卷按钮 */
.quiz-actions {
  margin-top: 22px;
  text-align: center;
}
.submit-btn {
  width: 320px;
  max-width: 90%;
  height: 48px;
  font-size: 16px;
  letter-spacing: 4px;
  border-radius: 13px;
}
.answered-tip {
  margin-top: 10px;
  font-size: 12px;
  color: #9aa0c4;
}

/* ---------- 结果区 ---------- */
.result-hero {
  text-align: center;
  border-radius: 22px;
  padding: 34px 20px 26px;
  background: linear-gradient(180deg, #fffdf6, #fff);
  border: 1px solid rgba(251, 191, 36, 0.3);
  box-shadow: 0 14px 34px -20px rgba(245, 158, 11, 0.5);
}
.result-hero.fail {
  background: linear-gradient(180deg, #fdf9ff, #fff);
  border-color: rgba(139, 92, 246, 0.25);
  box-shadow: 0 14px 34px -20px rgba(99, 102, 241, 0.45);
}
.big-emoji {
  font-size: 56px;
  animation: pop 0.5s cubic-bezier(0.2, 1.6, 0.4, 1) both;
}
.result-title {
  margin: 12px 0 4px;
  font-size: 23px;
  font-weight: 800;
  color: #23253f;
}
.result-sub {
  margin: 0 0 6px;
  font-size: 13.5px;
  color: #9aa0c4;
}
.result-stars {
  margin: 10px 0 4px;
  display: flex;
  justify-content: center;
  gap: 8px;
}
.result-star {
  font-size: 40px;
  color: #e8e6f6;
  opacity: 0;
  animation: starPop 0.5s cubic-bezier(0.2, 1.8, 0.4, 1) forwards;
}
.result-star.on {
  color: #f5b301;
  text-shadow: 0 4px 14px rgba(245, 179, 1, 0.55);
}
.score-chips {
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 12px;
}
.score-chip {
  font-size: 13px;
  font-weight: 700;
  color: #565c7d;
  background: #f4f5fd;
  padding: 6px 14px;
  border-radius: 999px;
}
.score-chip.ok {
  color: #047857;
  background: #ecfdf5;
}
.result-btns {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.detail-title {
  margin: 26px 0 14px;
  font-size: 16px;
  font-weight: 800;
  color: #34385c;
}
.detail-card {
  border-radius: 16px;
  background: #fff;
  padding: 16px 18px;
  margin-bottom: 14px;
  border: 1px solid rgba(99, 102, 241, 0.09);
  border-left: 5px solid #10b981;
  box-shadow: 0 8px 22px -18px rgba(35, 37, 63, 0.4);
}
.detail-card.bad {
  border-left-color: #f43f5e;
}
.d-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.d-no {
  font-size: 12px;
  font-weight: 800;
  color: #9aa0c4;
  letter-spacing: 1px;
}
.d-text {
  margin-top: 8px;
  font-size: 14.5px;
  color: #34385c;
  font-weight: 600;
  line-height: 1.7;
  white-space: pre-wrap;
}
.d-opts {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.d-opt {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  padding: 7px 12px;
  border-radius: 10px;
  background: #f7f8fd;
  color: #6b7093;
}
.d-opt.right {
  background: #ecfdf5;
  color: #047857;
}
.d-opt.wrong {
  background: #fff1f2;
  color: #be123c;
}
.d-letter {
  font-weight: 800;
}
.d-opt .el-icon {
  margin-left: auto;
}
.d-exp {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  background: #f6f7ff;
  font-size: 13px;
  color: #5a5f86;
  line-height: 1.8;
  border: 1px dashed rgba(99, 102, 241, 0.2);
}

/* ---------- AI 助教 ---------- */
.tutor-fab {
  position: fixed;
  right: 26px;
  bottom: 26px;
  z-index: 30;
  width: 56px;
  height: 56px;
  border: none;
  border-radius: 50%;
  font-size: 26px;
  cursor: pointer;
  background: var(--lq-grad);
  box-shadow: 0 12px 26px -8px rgba(99, 102, 241, 0.75);
  transition: transform 0.2s ease;
}
.tutor-fab:hover {
  transform: scale(1.08) rotate(6deg);
}

.chat-box {
  height: calc(100vh - 220px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-right: 4px;
}
.chat-msg {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}
.chat-msg .bubble {
  max-width: 78%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 13.5px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}
.chat-msg.ai .bubble {
  background: #f1f2fc;
  color: #34385c;
  border-bottom-left-radius: 4px;
}
.chat-msg.user {
  justify-content: flex-end;
}
.chat-msg.user .bubble {
  background: var(--lq-grad);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.chat-avatar {
  width: 30px;
  height: 30px;
  flex: none;
  display: grid;
  place-items: center;
  font-size: 16px;
  border-radius: 50%;
  background: #fff;
  border: 1px solid #e3e6f5;
}
.chat-input {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pop {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
@keyframes starPop {
  0% { opacity: 0; transform: scale(0.3) rotate(-20deg); }
  100% { opacity: 1; transform: scale(1) rotate(0); }
}
</style>
