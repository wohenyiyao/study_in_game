<template>
  <div class="auth-wrap">
    <!-- 左侧品牌介绍 -->
    <div class="auth-side">
      <div class="side-inner">
        <div class="side-logo">
          <span class="logo-emoji">🐍</span>
        </div>
        <h1 class="side-title">Python 闯关学</h1>
        <p class="side-slogan">像打游戏一样，把 Python 一关一关刷通关</p>

        <ul class="side-points">
          <li><span class="pt-ico">🗺️</span><div><b>闯关式学习地图</b><small>链式解锁，越学越上瘾</small></div></li>
          <li><span class="pt-ico">⭐</span><div><b>正确率换星级</b><small>每关 1~3 星，挑战满分</small></div></li>
          <li><span class="pt-ico">📕</span><div><b>错题自动入本</b><small>薄弱点一题不漏</small></div></li>
          <li><span class="pt-ico">🤖</span><div><b>AI 助教随时问</b><small>讲思路，不给答案</small></div></li>
        </ul>
      </div>
    </div>

    <!-- 右侧表单卡片 -->
    <div class="auth-panel">
      <el-card class="auth-card" shadow="never">
        <div class="card-head">
          <h2 class="card-title">{{ tab === 'login' ? '欢迎回来 👋' : '加入闯关冒险' }}</h2>
          <p class="card-sub">
            {{ tab === 'login' ? '输入邮箱与密码继续你的征程' : '创建账号，从第一关开始' }}
          </p>
        </div>

        <el-tabs v-model="tab" class="auth-tabs" stretch>
          <!-- 登录：QQ邮箱 + 密码 -->
          <el-tab-pane label="登录" name="login">
            <el-form @submit.prevent>
              <el-form-item>
                <el-input v-model="loginForm.email" placeholder="QQ 邮箱" size="large" clearable>
                  <template #prefix><el-icon><Message /></el-icon></template>
                </el-input>
              </el-form-item>
              <el-form-item>
                <el-input v-model="loginForm.password" type="password" show-password
                          placeholder="密码" size="large" @keyup.enter="doLogin">
                  <template #prefix><el-icon><Lock /></el-icon></template>
                </el-input>
              </el-form-item>
              <el-button type="primary" size="large" class="submit-btn"
                         :loading="loading" @click="doLogin">
                登录
              </el-button>
            </el-form>
          </el-tab-pane>

          <!-- 注册：QQ邮箱 + 邮箱验证码 + 密码 -->
          <el-tab-pane label="注册" name="register">
            <el-form @submit.prevent>
              <el-form-item>
                <el-input v-model="regForm.email" placeholder="QQ 邮箱" size="large" clearable>
                  <template #prefix><el-icon><Message /></el-icon></template>
                </el-input>
              </el-form-item>
              <el-form-item>
                <div class="code-row">
                  <el-input v-model="regForm.code" placeholder="6 位邮箱验证码" size="large" />
                  <el-button class="code-btn" :disabled="counting > 0 || !regForm.email"
                             size="large" @click="doSendCode">
                    {{ counting > 0 ? `${counting}s 后重发` : '发送验证码' }}
                  </el-button>
                </div>
              </el-form-item>
              <el-form-item>
                <el-input v-model="regForm.password" type="password" show-password
                          placeholder="设置密码（至少 6 位）" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="regForm.confirm" type="password" show-password
                          placeholder="确认密码" size="large" @keyup.enter="doRegister" />
              </el-form-item>
              <el-button type="primary" size="large" class="submit-btn"
                         :loading="loading" @click="doRegister">
                注册并登录
              </el-button>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-card>
      <p class="auth-foot">© {{ new Date().getFullYear() }} Python 闯关学 · 边玩边学 Python</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const router = useRouter()
const store = useUserStore()
const tab = ref('login')
const loading = ref(false)
const counting = ref(0)
let timer = null

const loginForm = reactive({ email: '', password: '' })
const regForm = reactive({ email: '', password: '', confirm: '', code: '' })

async function doLogin() {
  if (!loginForm.email || !loginForm.password) return ElMessage.warning('请填写邮箱和密码')
  loading.value = true
  try {
    await store.login(loginForm.email, loginForm.password)
    ElMessage.success('欢迎回来！')
    router.push('/map')
  } finally { loading.value = false }
}

async function doSendCode() {
  counting.value = 60
  timer = setInterval(() => {
    counting.value -= 1
    if (counting.value <= 0) clearInterval(timer)
  }, 1000)
  try {
    await store.sendCode(regForm.email)
    ElMessage.success('验证码已发送到邮箱')
  } catch (e) {
    clearInterval(timer)
    counting.value = 0
  }
}

async function doRegister() {
  const { email, password, confirm, code } = regForm
  if (!email) return ElMessage.warning('请填写邮箱')
  if (!code) return ElMessage.warning('请填写邮箱验证码')
  if (password.length < 6) return ElMessage.warning('密码至少 6 位')
  if (password !== confirm) return ElMessage.warning('两次密码不一致')
  loading.value = true
  try {
    await store.register(email, password, code)
    ElMessage.success('注册成功，开始闯关吧！')
    router.push('/map')
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-wrap {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  align-items: stretch;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 45%, #6366f1 100%);
}

/* ---------- 左侧品牌区 ---------- */
.auth-side {
  flex: 1.1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  padding: 40px;
  position: relative;
  overflow: hidden;
}
.auth-side::before {
  content: '';
  position: absolute;
  width: 480px;
  height: 480px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.22), transparent 65%);
  top: -140px;
  left: -120px;
}
.auth-side::after {
  content: '';
  position: absolute;
  width: 560px;
  height: 560px;
  border-radius: 50%;
  background: radial-gradient(circle at 60% 40%, rgba(34, 211, 238, 0.25), transparent 65%);
  bottom: -200px;
  right: -140px;
}
.side-inner {
  position: relative;
  z-index: 1;
  max-width: 420px;
  animation: rise 0.7s ease both;
}
.side-logo .logo-emoji {
  font-size: 52px;
  line-height: 1;
}
.side-title {
  margin: 18px 0 8px;
  font-size: 34px;
  font-weight: 800;
  letter-spacing: 1px;
}
.side-slogan {
  margin: 0 0 30px;
  font-size: 15px;
  opacity: 0.9;
}
.side-points {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.side-points li {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255, 255, 255, 0.18);
}
.pt-ico {
  font-size: 24px;
}
.side-points b {
  display: block;
  font-size: 14.5px;
}
.side-points small {
  display: block;
  margin-top: 2px;
  font-size: 12px;
  opacity: 0.78;
}

/* ---------- 右侧表单区 ---------- */
.auth-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(8px);
  border-left: 1px solid rgba(255, 255, 255, 0.16);
}
.auth-card {
  width: 400px;
  max-width: 92vw;
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  padding: 8px 10px 4px;
  animation: rise 0.7s 0.08s ease both;
  box-shadow: 0 30px 70px -25px rgba(20, 16, 60, 0.55);
}
.card-head {
  text-align: center;
  padding: 10px 0 4px;
}
.card-title {
  margin: 0;
  font-size: 23px;
  font-weight: 800;
  color: #23253f;
}
.card-sub {
  margin: 6px 0 10px;
  font-size: 13px;
  color: #9aa0c4;
}

.auth-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 0;
}
.auth-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 600;
}
.auth-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 3px;
  background: var(--lq-grad);
}
.auth-tabs :deep(.el-form-item) {
  margin-bottom: 18px;
}
.auth-tabs :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 2px 14px;
  box-shadow: 0 0 0 1.5px #e3e6f5 inset;
}
.auth-tabs :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1.5px var(--el-color-primary) inset;
}

.code-row {
  display: flex;
  gap: 8px;
  width: 100%;
}
.code-btn {
  flex: none;
  border-radius: 12px;
  font-size: 13px;
}
.submit-btn {
  width: 100%;
  height: 46px;
  margin-top: 6px;
  font-size: 16px;
  letter-spacing: 6px;
  border-radius: 12px;
}

.auth-foot {
  margin-top: 18px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 窄屏时隐藏品牌区 */
@media (max-width: 900px) {
  .auth-side {
    display: none;
  }
  .auth-panel {
    border-left: none;
    background: transparent;
  }
  .auth-wrap {
    background: linear-gradient(160deg, #4f46e5 0%, #7c3aed 60%, #6366f1 100%);
  }
}
</style>
