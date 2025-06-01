<template>
  <div class="p-6 max-w-3xl mx-auto">
    <h1 class="text-xl font-bold mb-4">角色调价系统</h1>

    <table class="table-auto w-full mb-4 border">
      <thead>
        <tr>
          <th class="border px-2">人气排序</th>
          <th class="border px-2">角色名</th>
          <th class="border px-2">数量</th>
          <th class="border px-2">调价结果</th>
          <th class="border px-2">操作</th>
        </tr>
      </thead>
      <tbody ref="sortableContainer">
        <tr v-for="(row, index) in roles" :key="row.id" class="border">
          <td class="border px-2">{{ index + 1 }}</td>
          <td class="border px-2">
            <input v-model="row.name" class="border w-full" />
          </td>
          <td class="border px-2">
            <input v-model.number="row.count" type="number" min="1" class="border w-full" />
          </td>
          <td class="border px-2 text-center">
            {{ row.adjustment ?? '-' }}
          </td>
          <td class="border px-2">
            <button @click="removeRow(index)" class="text-red-500">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="flex gap-4 mb-4">
      <button @click="addRow" class="bg-green-500 text-white px-3 py-1 rounded">添加角色</button>
      <button @click="calculate" class="bg-blue-600 text-white px-3 py-1 rounded">计算调价</button>
      <button @click="exportCSV" class="bg-gray-500 text-white px-3 py-1 rounded">导出CSV</button>
      <input type="file" accept=".csv" @change="importCSV" class="mt-2" />
    </div>

    <div class="mb-2">
      原价：<input v-model.number="basePrice" type="number" class="border w-24 px-1" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sortable from 'sortablejs'
import axios from 'axios'
function exportCSV() {
  const header = '角色名称,数量,调价'
  const rows = roles.value.map(role =>
    [role.name, role.count, role.adjustment != null ? role.adjustment : ''].join(',')
  )
  const csvContent = '\uFEFF' + [header, ...rows].join('\n')  // 加 BOM

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', '角色调价.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function importCSV(event) {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = () => {
    const lines = reader.result.split('\n').filter(Boolean)
    const newRows = []
    for (let i = 1; i < lines.length; i++) { // 跳过第一行标题
      const [name, count, adjustment] = lines[i].split(',').map(s => s.trim())
      newRows.push({
        id: nextId.value++,
        name,
        count: parseInt(count),
        adjustment: adjustment ? Number(adjustment) : null
      })
    }
    roles.value = newRows
  }
  reader.readAsText(file)
}

const roles = ref([
  { id: 1, name: 'A', count: 6 },
  { id: 2, name: 'B', count: 4 },
  { id: 3, name: 'C', count: 3 },
])

const basePrice = ref(100)
const nextId = ref(4)
const sortableContainer = ref(null)

onMounted(() => {
  Sortable.create(sortableContainer.value, {
    animation: 150,
    onEnd: (evt) => {
      const oldIndex = evt.oldIndex
      const newIndex = evt.newIndex
      if (oldIndex === newIndex) return

      const movedItem = roles.value.splice(oldIndex, 1)[0]
      roles.value.splice(newIndex, 0, movedItem)
    },
  })
})

function addRow() {
  roles.value.push({ id: nextId.value++, name: '', count: 1 })
}

function removeRow(index) {
  roles.value.splice(index, 1)
}

async function calculate() {
  const payload = {
    base_price: basePrice.value,
    role_names: roles.value.map(r => r.name),
    role_counts: Object.fromEntries(roles.value.map(r => [r.name, r.count])),
    popularity: roles.value.map(r => r.name),
    integer_only: true
  }

  const res = await axios.post('http://localhost:5000/api/solve', payload)
  const solution = res.data?.[0] ?? {}
  roles.value.forEach(r => {
    r.adjustment = solution.adjustments?.[r.name] ?? null
  })
}
</script>

<style scoped>
table input {

  /* 页面整体居中、留白更自然 */
  .p-6 {
    background: #f9f9fb;
    font-family: 'Segoe UI', sans-serif;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }

  /* 表格更清晰 */
  table {
    border-collapse: collapse;
    background-color: white;
    width: 100%;
    border-radius: 6px;
    overflow: hidden;
  }

  th,
  td {
    padding: 10px 12px;
    border: 1px solid #ddd;
    text-align: center;
  }

  thead {
    background-color: #f0f4f8;
    font-weight: bold;
  }

  /* 输入框统一风格 */
  input[type="text"],
  input[type="number"] {
    border: 1px solid #ccc;
    padding: 6px 10px;
    border-radius: 4px;
    width: 100%;
    box-sizing: border-box;
  }

  /* 按钮风格改进 */
  button {
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
  }

  button:hover {
    opacity: 0.9;
  }

  .bg-green-500 {
    background-color: #38a169;
  }

  .bg-blue-600 {
    background-color: #2b6cb0;
  }

  .bg-gray-500 {
    background-color: #718096;
  }

  .text-white {
    color: white;
  }

  .text-red-500 {
    color: #e53e3e;
  }

}
</style>
