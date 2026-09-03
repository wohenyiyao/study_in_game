<template>
  <div>
    <div class="bar">
      <el-page-header content="章节管理" />
      <div class="right">
        <el-select v-model="filterSubject" placeholder="全部科目" clearable style="width: 180px"
                   @change="load">
          <el-option v-for="s in subjects" :key="s.id"
                     :label="`${s.icon || ''} ${s.name}`" :value="s.id" />
        </el-select>
        <el-button type="primary" @click="openDialog()">新增章节</el-button>
      </div>
    </div>

    <el-table :data="list" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="科目" width="140">
        <template #default="{ row }">
          <el-tag size="small" effect="plain">{{ row.subject_name || '—' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="order" label="排序" width="70" />
      <el-table-column prop="level_count" label="关卡数" width="80" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" plain @click="del(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="form.id ? '编辑章节' : '新增章节'" width="480px">
      <el-form label-width="70px">
        <el-form-item label="科目">
          <el-select v-model="form.subject_id" placeholder="选择科目" style="width: 100%">
            <el-option v-for="s in subjects" :key="s.id"
                       :label="`${s.icon || ''} ${s.name}`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
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
const subjects = ref([])
const dlg = ref(false)
const filterSubject = ref(null)
const form = ref({ id: null, subject_id: null, title: '', description: '', order: 0 })

async function load() {
  const params = filterSubject.value ? { subject_id: filterSubject.value } : {}
  list.value = await http.get('/admin/chapters', { params })
}
function openDialog(row) {
  form.value = row
    ? { id: row.id, subject_id: row.subject_id, title: row.title,
        description: row.description, order: row.order }
    : { id: null, subject_id: filterSubject.value || subjects.value[0]?.id || null,
        title: '', description: '', order: list.value.length }
  dlg.value = true
}
async function save() {
  if (!form.value.subject_id) return ElMessage.warning('请选择所属科目')
  const body = {
    subject_id: form.value.subject_id,
    title: form.value.title,
    description: form.value.description,
    order: form.value.order
  }
  if (form.value.id) await http.put(`/admin/chapters/${form.value.id}`, body)
  else await http.post('/admin/chapters', body)
  ElMessage.success('已保存')
  dlg.value = false
  load()
}
async function del(row) {
  await ElMessageBox.confirm(`删除章节「${row.title}」将连带删除其关卡与题目，确定？`, '警告', { type: 'warning' })
  await http.delete(`/admin/chapters/${row.id}`)
  ElMessage.success('已删除')
  load()
}
onMounted(async () => {
  subjects.value = await http.get('/admin/subjects')
  load()
})
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.right { display: flex; gap: 10px; }
</style>
