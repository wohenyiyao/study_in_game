<template>
  <el-container class="shell">
    <!-- 侧边栏 -->
    <el-aside class="sidebar" width="244px">
      <div class="brand">
        <span class="brand-logo">🐍</span>
        <div class="brand-text">
          <span class="brand-name lq-grad-text">Python 闯关学</span>
          <span class="brand-sub">L E A R N · Q U E S T</span>
        </div>
      </div>

      <div class="menu-caption">开始学习</div>
      <el-menu router :default-active="route.path" class="side-menu">
        <el-menu-item index="/map">
          <el-icon><MapLocation /></el-icon><span>学习地图</span>
        </el-menu-item>
        <el-menu-item index="/stats">
          <el-icon><Trophy /></el-icon><span>我的战绩</span>
        </el-menu-item>
        <el-menu-item index="/wrongbook">
          <el-icon><Document /></el-icon><span>错题本</span>
        </el-menu-item>

        <template v-if="store.isAdmin">
          <div class="menu-caption admin-caption">内容管理</div>
          <el-menu-item index="/admin/chapters">
            <el-icon><FolderOpened /></el-icon><span>章节管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/levels">
            <el-icon><Flag /></el-icon><span>关卡管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/questions">
            <el-icon><EditPen /></el-icon><span>题目管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon><span>用户列表</span>
          </el-menu-item>
        </template>
      </el-menu>

      <div class="side-foot">
        <div class="user-box">
          <span class="avatar">{{ initial }}</span>
          <div class="user-meta">
            <span class="user-mail" :title="store.user?.email">{{ store.user?.email }}</span>
            <span class="user-role" :class="store.isAdmin ? 'is-admin' : ''">
              {{ store.isAdmin ? '管理员' : '学习者' }}
            </span>
          </div>
          <el-button class="logout-btn" text circle title="退出登录" @click="logout">
            <el-icon><SwitchButton /></el-icon>
          </el-button>
        </div>
      </div>
    </el-aside>

    <!-- 主内容 -->
    <el-main class="main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const store = useUserStore()

const initial = computed(() => (store.user?.email || '?')[0].toUpperCase())

function logout() {
  store.logout()
  router.push('/login')
}
</script>

<style scoped>
.shell {
  height: 100vh;
}

/* ---------- 侧边栏 ---------- */
.sidebar {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(14px);
  border-right: 1px solid rgba(99, 102, 241, 0.08);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 22px 20px 18px;
}
.brand-logo {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  font-size: 24px;
  border-radius: 14px;
  background: var(--lq-grad);
  box-shadow: 0 8px 18px -6px rgba(99, 102, 241, 0.65);
}
.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.brand-name {
  font-size: 17px;
  font-weight: 800;
  letter-spacing: 0.5px;
}
.brand-sub {
  margin-top: 3px;
  font-size: 9.5px;
  letter-spacing: 2.5px;
  color: #b7bce0;
}

.menu-caption {
  padding: 10px 22px 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #b0b5d9;
}
.admin-caption {
  margin-top: 10px;
  border-top: 1px dashed rgba(99, 102, 241, 0.12);
  padding-top: 14px;
}

.side-menu {
  flex: 1;
  border-right: none;
  background: transparent;
  padding: 0 12px;
  overflow-y: auto;
}
.side-menu :deep(.el-menu-item) {
  height: 46px;
  line-height: 46px;
  margin: 4px 0;
  border-radius: 12px;
  color: #565c7d;
  font-size: 14px;
}
.side-menu :deep(.el-menu-item .el-icon) {
  font-size: 17px;
  margin-right: 8px;
}
.side-menu :deep(.el-menu-item:hover) {
  background: #eef1ff;
  color: #4f46e5;
}
.side-menu :deep(.el-menu-item.is-active) {
  background: var(--lq-grad);
  color: #fff;
  font-weight: 600;
  box-shadow: 0 8px 18px -6px rgba(99, 102, 241, 0.7);
}
.side-menu :deep(.el-menu-item.is-active .el-icon) {
  color: #fff;
}

/* ---------- 底部用户区 ---------- */
.side-foot {
  padding: 14px;
}
.user-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 14px;
  background: #fff;
  border: 1px solid rgba(99, 102, 241, 0.1);
  box-shadow: 0 6px 16px -10px rgba(35, 37, 63, 0.25);
}
.avatar {
  width: 36px;
  height: 36px;
  flex: none;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--lq-grad);
  color: #fff;
  font-weight: 800;
  font-size: 15px;
}
.user-meta {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.user-mail {
  font-size: 12.5px;
  color: #34385c;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-role {
  margin-top: 2px;
  font-size: 10.5px;
  color: #9aa0c4;
}
.user-role.is-admin {
  color: #8b5cf6;
  font-weight: 700;
}
.logout-btn {
  flex: none;
  color: #c0c4dc;
}
.logout-btn:hover {
  color: #f43f5e;
}

/* ---------- 主内容区 ---------- */
.main {
  position: relative;
  z-index: 1;
  padding: 24px 28px 48px;
  overflow-y: auto;
  background: transparent;
}
</style>
