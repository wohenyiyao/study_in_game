<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="brand">🐍 闯关学</div>
      <el-menu router :default-active="$route.path" class="menu">
        <el-menu-item index="/map"><el-icon><MapLocation /></el-icon>学习地图</el-menu-item>
        <el-menu-item index="/stats"><el-icon><Trophy /></el-icon>我的战绩</el-menu-item>
        <el-menu-item index="/wrongbook"><el-icon><Document /></el-icon>错题本</el-menu-item>
        <template v-if="store.isAdmin">
          <el-sub-menu index="admin">
            <template #title><el-icon><Setting /></el-icon>内容管理</template>
            <el-menu-item index="/admin/chapters">章节管理</el-menu-item>
            <el-menu-item index="/admin/levels">关卡管理</el-menu-item>
            <el-menu-item index="/admin/questions">题目管理</el-menu-item>
            <el-menu-item index="/admin/users">用户列表</el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
      <div class="footer">
        <span>{{ store.user?.email }}</span>
        <el-button link type="danger" @click="logout">退出</el-button>
      </div>
    </el-aside>
    <el-main class="main"><router-view /></el-main>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const store = useUserStore()
function logout() {
  store.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout { height: 100vh; }
.aside { background: #fff; border-right: 1px solid #ebeef5; display: flex; flex-direction: column; }
.brand { font-size: 20px; font-weight: 700; padding: 18px 20px; color: #1f6feb; }
.menu { border-right: none; flex: 1; }
.footer { padding: 14px 18px; border-top: 1px solid #ebeef5; display: flex;
  align-items: center; justify-content: space-between; font-size: 12px; color: #666; }
.main { background: #f5f7fa; overflow: auto; }
</style>
