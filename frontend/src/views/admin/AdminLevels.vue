<template>
  <div>
    <div class="bar">
      <el-page-header content="关卡管理" />
      <el-button type="primary" @click="openDialog()">新增关卡</el-button>
    </div>
    <el-table :data="list" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="chapter_title" label="所属章节" width="200" />
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="pass_ratio" label="通关线" width="90">
        <template #default="{ row }">{{ Math.round(row.pass_ratio * 100) }}%</template>
      </el-table-column>
      <el-table-column prop="question_count" label="题数" width="70" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" plain @click="del(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="form.id ? '编辑关卡' : '新增关卡'" width="520px">
      <el-form label-width="80px">
        <el-form-item label="所属章节">
          <el-select v-model="form.chapter_id" style="width: 100%">
            <el-option v-for="ch in chapters" :key="ch.id" :value="ch.id" :label="`${ch.title}`" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.order" :min="0" /></el-form-item>
        <el-form-item label="通关线">
          <el-slider v-model="form.pass_ratio" :min="0.5" :max="1" :step="0.05" show-input />
        </el-form-item>
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
const chapters = ref([])
const dlg = ref(false)
const form = ref({ id: null, chapter_id: null, title: '', description: '', order: 0, pass_ratio: 0.6 })

async function load() {
  const [lv, ch] = await Promise.all([http.get('/admin/levels'), http.get('/admin/chapters')])
  chapters.value = ch
  const chMap = Object.fromEntries(ch.map((c) => [c.id, c]))
  list.value = lv.map((l) => ({ ...l, chapter_title: chMap[l.chapter_id]?.title || '?' }))
}
function openDialog(row) {
  form.value = row
    ? { ...row }
    : { id: null, chapter_id: chapters.value[0]?.id, title: '', description: '', order: 0, pass_ratio: 0.6 }
  dlg.value = true
}
async function save() {
  const body = { chapter_id: form.value.chapter_id, title: form.value.title,
    description: form.value.description, order: form.value.order, pass_ratio: form.value.pass_ratio }
  if (form.value.id) await http.put(`/admin/levels/${form.value.id}`, body)
  else await http.post('/admin/levels', body)
  ElMessage.success('已保存')
  dlg.value = false
  load()
}
async function del(row) {
  await ElMessageBox.confirm(`删除关卡「${row.title}」将连带删除其题目，确定？`, '警告', { type: 'warning' })
  await http.delete(`/admin/levels/${row.id}`)
  ElMessage.success('已删除')
  load()
}
onMounted(load)
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
</style>
