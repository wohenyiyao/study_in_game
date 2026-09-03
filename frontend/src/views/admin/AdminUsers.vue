<template>
  <div>
    <el-page-header content="用户列表" class="header" />
    <el-table :data="list" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
            {{ row.role === 'admin' ? '管理员' : '学员' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="注册时间" width="200">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../../api/http'

const list = ref([])
onMounted(async () => { list.value = await http.get('/admin/users') })
</script>

<style scoped>
.header { margin-bottom: 14px; }
</style>
