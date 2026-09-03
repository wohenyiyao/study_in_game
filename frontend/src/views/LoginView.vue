<template>
  <div class="auth-wrap">
    <el-card class="auth-card">
      <h2 class="title">🐍 Python 闯关学</h2>
      <el-tabs v-model="tab">
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
            <el-button type="primary" size="large" style="width:100%" :loading="loading" @click="doLogin">
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
                <el-button :disabled="counting > 0 || !regForm.email" size="large"
                           @click="doSendCode">
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
            <el-button type="primary" size="large" style="width:100%" :loading="loading"
                       @click="doRegister">注册并登录</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
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
.auth-wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #1f6feb 0%, #00b4d8 100%); }
.auth-card { width: 420px; border-radius: 12px; padding: 8px 4px; }
.title { text-align: center; margin: 4px 0 14px; color: #1f2328; }
.code-row { display: flex; gap: 8px; width: 100%; }
</style>
