<template>
  <div>
    <div class="bar">
      <el-page-header content="科目管理" />
      <el-button type="primary" @click="openDialog()">新增科目</el-button>
    </div>

    <el-table :data="list" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="图标" width="70">
        <template #default="{ row }"><span class="ico">{{ row.icon || '🎮' }}</span></template>
      </el-table-column>
      <el-table-column label="科目" width="160">
        <template #default="{ row }">
          <b>{{ row.name }}</b>
          <el-tag size="small" type="info" class="code-tag">{{ row.code }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="order" label="排序" width="70" />
      <el-table-column prop="chapter_count" label="章节数" width="80" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" plain @click="del(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="form.id ? '编辑科目' : '新增科目'" width="480px">
      <el-form label-width="80px">
        <el-form-item label="科目名称"><el-input v-model="form.name" placeholder="如：Java 面试" /></el-form-item>
        <el-form-item label="编码">
          <el-input v-model="form.code" placeholder="如：java（唯一，用作科目 key）" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="form.icon" placeholder="一个 emoji，如 ☕ / 🐍 / 💼" maxlength="8" />
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.order" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const list = ref([])
const dlg = ref(false)
const form = ref({ id: null, name: '', code: '', icon: '🎮', description: '', order: 0 })

async function load() { list.value = await http.get('/admin/subjects') }
function openDialog(row) {
  form.value = row
    ? { ...row }
    : { id: null, name: '', code: '', icon: '🎮', description: '', order: list.value.length }
  dlg.value = true
}
async function save() {
  const body = {
    name: form.value.name,
    code: form.value.code.trim().toLowerCase(),
    icon: form.value.icon || '🎮',
    description: form.value.description,
    order: form.value.order
  }
  if (!body.name || !body.code) return ElMessage.warning('请填写科目名称与编码')
  if (form.value.id) await http.put(`/admin/subjects/${form.value.id}`, body)
  else await http.post('/admin/subjects', body)
  ElMessage.success('已保存')
  dlg.value = false
  load()
}
async function del(row) {
  await ElMessageBox.confirm(
    `删除科目「${row.name}」？科目下仍有章节时会删除失败，请先清理其章节。`,
    '警告', { type: 'warning' })
  await http.delete(`/admin/subjects/${row.id}`)
  ElMessage.success('已删除')
  load()
}
onMounted(load)
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.ico { font-size: 20px; }
.code-tag { margin-left: 8px; vertical-align: middle; }
</style>
