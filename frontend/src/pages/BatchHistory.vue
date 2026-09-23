<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getJSON } from '../api'
const router = useRouter()
const items = ref([])
const lookupId = ref('')
const lookupError = ref('')
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
const openById = async () => {
  const id = String(lookupId.value).trim()
  lookupError.value = ''
  if (!/^\d+$/.test(id)) { lookupError.value = '请输入数字编号'; return }
  try {
    await getJSON(`/api/history/${id}`)
    router.push(`/history/${id}`)
  } catch (e) {
    lookupError.value = `编号 ${id} 不存在，无法打开`
  }
}
</script>
<template><div class="page"><h1>估算记录</h1>
<form @submit.prevent="openById">
  <label>按编号打开 <input v-model="lookupId" inputmode="numeric" placeholder="如 3" /></label>
  <button type="submit">打开</button>
  <span v-if="lookupError" class="error">{{ lookupError }}</span>
</form>
<table><tr v-for="h in items" :key="h.id">
  <td><router-link :to="`/history/${h.id}`">#{{ h.id }}</router-link></td>
  <td>{{ h.created_at }}</td>
  <td>净 {{ h.net_m2 }} m² · {{ h.liters }} 升 · {{ h.coats }} 遍</td>
</tr></table></div></template>
