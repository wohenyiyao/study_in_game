<template>
  <div>
    <div class="bar">
      <el-page-header content="题目管理" />
      <div class="right">
        <el-select v-model="levelId" placeholder="选择关卡（共 {{ levels.length }} 个）" clearable
                   filterable style="width: 300px" @change="load">
          <el-option v-for="lv in levels" :key="lv.id" :value="lv.id"
                     :label="`${lv.chapter_title} · ${lv.title}`">
            <span class="lv-label">{{ lv.chapter_title }} · {{ lv.title }}</span>
            <span class="lv-count">{{ lv.question_count }} 题</span>
          </el-option>
        </el-select>
        <el-button type="primary" :disabled="!levelId" @click="openDialog()">新增题目</el-button>
      </div>
    </div>
    <el-table :data="list" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="content" label="题干" min-width="220" show-overflow-tooltip />
      <el-table-column label="选项" min-width="260">
        <template #default="{ row }">
          <div v-for="(o, i) in row.options" :key="i"
               :style="{ color: i === row.answer_index ? '#67c23a' : '' }">
            {{ String.fromCharCode(65 + i) }}. {{ o }}
            <span v-if="i === row.answer_index"> ✓</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" plain @click="del(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="form.id ? '编辑题目' : '新增题目'" width="640px" top="6vh">
      <el-form label-width="80px">
        <el-form-item label="题干"><el-input v-model="form.content" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="选项">
          <div v-for="(o, i) in form.options" :key="i" class="opt-row">
            <el-input v-model="form.options[i]" :placeholder="`选项 ${String.fromCharCode(65 + i)}`" />
            <el-radio :value="i" v-model="form.answer_index">正确</el-radio>
            <el-button link type="danger" :disabled="form.options.length <= 2" @click="form.options.splice(i, 1)">删</el-button>
          </div>
          <el-button size="small" @click="form.options.push('')">+ 添加选项</el-button>
        </el-form-item>
        <el-form-item label="解析"><el-input v-model="form.explanation" type="textarea" :rows="2" /></el-form-item>
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

const levels = ref([])
const levelId = ref(null)
const list = ref([])
const dlg = ref(false)
const form = ref(emptyForm())

function emptyForm() {
  return { id: null, content: '', options: ['', '', '', ''], answer_index: 0, explanation: '' }
}

async function loadLevels() {
  const [lv, ch] = await Promise.all([http.get('/admin/levels'), http.get('/admin/chapters')])
  const chMap = Object.fromEntries(ch.map((c) => [c.id, c]))
  levels.value = lv.map((l) => ({
    ...l,
    chapter_title: chMap[l.chapter_id]?.title || '未命名章节',
    subject_name: chMap[l.chapter_id]?.subject_name || ''
  }))
}
async function load() {
  if (!levelId.value) return
  list.value = await http.get('/admin/questions', { params: { level_id: levelId.value } })
}
function openDialog(row) {
  if (!row && !levelId.value) return
  form.value = row
    ? { ...row, options: [...row.options] }
    : { ...emptyForm(), level_id: levelId.value }
  dlg.value = true
}
async function save() {
  if (form.value.options.some((o) => !o.trim())) return ElMessage.warning('选项不能为空')
  const body = { level_id: levelId.value, content: form.value.content, options: form.value.options,
    answer_index: form.value.answer_index, explanation: form.value.explanation }
  if (form.value.id) await http.put(`/admin/questions/${form.value.id}`, body)
  else await http.post('/admin/questions', body)
  ElMessage.success('已保存')
  dlg.value = false
  load()
}
async function del(row) {
  await ElMessageBox.confirm('确定删除该题？', '警告', { type: 'warning' })
  await http.delete(`/admin/questions/${row.id}`)
  ElMessage.success('已删除')
  load()
}
onMounted(async () => {
  await loadLevels()
  if (levels.value.length) { levelId.value = levels.value[0].id; load() }
})
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 10px; }
.right { display: flex; gap: 10px; align-items: center; }
.lv-label { flex: 1; }
.lv-count { color: #9aa0c4; font-size: 12px; margin-left: auto; padding-left: 12px; }
.opt-row { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; }
</style>
