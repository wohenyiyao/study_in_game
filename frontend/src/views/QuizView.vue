<template>
  <div class="quiz-wrap">
    <el-page-header :content="data.title || '闯关'" @back="back" class="header" />

    <!-- 答题阶段 -->
    <el-card v-if="!result" class="q-card">
      <div v-for="(q, i) in questions" :key="q.id" class="q-item">
        <div class="q-text"><b>{{ i + 1 }}.</b> {{ q.content }}</div>
        <el-radio-group v-model="answers[i]" class="q-opts">
          <el-radio v-for="(opt, oi) in q.options" :key="oi" :value="oi" border class="q-opt">
            {{ String.fromCharCode(65 + oi) }}. {{ opt }}
          </el-radio>
        </el-radio-group>
      </div>
      <el-button type="primary" size="large" style="width:100%" :disabled="!allAnswered"
                 :loading="submitting" @click="submit">
        交卷判分
      </el-button>
    </el-card>

    <!-- 结果阶段 -->
    <el-card v-else class="q-card">
      <el-result :icon="result.passed ? 'success' : 'warning'"
                 :title="result.passed ? `通关成功！获得 ${result.stars} 星` : '未通关，再试试吧'"
                 :sub-title="`正确 ${result.correct} / ${result.total}（${Math.round(result.accuracy * 100)}%）`">
        <template #extra>
          <el-button type="primary" @click="nextLevel" v-if="result.passed">下一关</el-button>
          <el-button @click="resetQuiz">{{ result.passed ? '再玩一次' : '重新挑战' }}</el-button>
          <el-button @click="back">返回地图</el-button>
        </template>
      </el-result>
      <el-divider content-position="left">题目讲解</el-divider>
      <div v-for="d in result.details" :key="d.question_id" class="detail"
           :class="d.is_correct ? 'ok' : 'bad'">
        <div class="d-q">{{ d.content }}</div>
        <div class="d-line">
          <el-tag :type="d.is_correct ? 'success' : 'danger'" size="small">
            {{ d.is_correct ? '✓ 答对' : '✗ 答错' }}
          </el-tag>
          <span v-if="!d.is_correct" class="d-your">
            你选了 {{ String.fromCharCode(65 + d.your) }}，正确答案是
            {{ String.fromCharCode(65 + d.correct_index) }}
          </span>
        </div>
        <div class="d-exp" v-if="d.explanation">💡 {{ d.explanation }}</div>
      </div>
    </el-card>

    <!-- AI 助教（Agent 开发位） -->
    <el-button class="tutor-btn" type="primary" circle size="large"
               title="问 AI 助教" @click="tutorVisible = true">🤖</el-button>
    <el-drawer v-model="tutorVisible" title="🤖 AI 助教（Agent 开发位）" size="420px">
      <div class="chat-box">
        <div v-for="(m, i) in chat" :key="i" class="chat-msg" :class="m.role">
          <div class="bubble" v-if="m.role === 'user'">🧑 {{ m.content }}</div>
          <div class="bubble" v-else>{{ m.content }}</div>
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
const allAnswered = computed(() =>
  questions.value.length > 0 && answers.value.every((a) => a !== undefined && a !== null))

const tutorVisible = ref(false)
const chatInput = ref('')
const chatting = ref(false)
const chat = ref([{ role: 'ai', content: '（助教未接入时这里是占位回复。Agent 开发位见 backend/app/agent/tutor.py）' }])

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
  const all = map.flatMap((c) => c.levels)
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
.quiz-wrap { max-width: 860px; margin: 0 auto; }
.header { margin-bottom: 16px; }
.q-item { padding: 12px 4px; border-bottom: 1px dashed #ebeef5; }
.q-text { font-size: 15px; margin-bottom: 10px; line-height: 1.7; }
.q-opts { display: flex; flex-direction: column; align-items: stretch; gap: 4px; }
.q-opt { margin: 0; height: auto; padding: 8px 14px; }
.detail { padding: 10px 12px; border-radius: 8px; margin-bottom: 10px; }
.detail.ok { background: #f0f9eb; }
.detail.bad { background: #fef0f0; }
.d-q { font-weight: 500; margin-bottom: 6px; }
.d-line { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; font-size: 13px; }
.d-your { color: #d03050; }
.d-exp { font-size: 13px; color: #555; line-height: 1.7; }
.tutor-btn { position: fixed; right: 24px; bottom: 24px; z-index: 20; }
.chat-box { height: calc(100vh - 260px); overflow: auto; padding-bottom: 12px; }
.chat-msg { margin-bottom: 10px; }
.chat-msg .bubble { padding: 8px 12px; border-radius: 8px; font-size: 13px; line-height: 1.7;
  white-space: pre-wrap; }
.chat-msg.user .bubble { background: #ecf5ff; }
.chat-msg.ai .bubble { background: #f4f4f5; }
.chat-input { display: flex; gap: 8px; }
</style>
