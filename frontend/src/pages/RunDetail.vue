<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON } from '../api'
const route = useRoute()
const item = ref(null)
const error = ref('')
const loading = ref(false)
const load = async () => {
  loading.value = true; error.value = ''; item.value = null
  try {
    item.value = await getJSON(`/api/history/${route.params.id}`)
  } catch (e) {
    error.value = `编号 ${route.params.id} 打开失败：不存在该估算记录`
  } finally { loading.value = false }
}
onMounted(load); watch(() => route.params.id, load)
</script>
<template><div class="page">
  <h1>估算详情 #{{ route.params.id }}</h1>
  <p v-if="loading">读取中…</p>
  <p v-else-if="error" class="error">{{ error }}</p>
  <table v-else-if="item">
    <tr><th>编号</th><td>#{{ item.id }}</td></tr>
    <tr><th>房间</th><td>{{ item.room_id }}</td></tr>
    <tr><th>写入时间</th><td>{{ item.created_at }}</td></tr>
    <tr><th>净面积</th><td>{{ item.net_m2 }} m²</td></tr>
    <tr><th>开洞扣除</th><td>{{ item.openings_m2 }} m²（毛面积 {{ item.gross_m2 }} m²）</td></tr>
    <tr><th>用漆量</th><td><span class="hero-num">{{ item.liters }}</span> 升</td></tr>
    <tr><th>涂布率</th><td>{{ item.coverage }} m²/升</td></tr>
    <tr><th>遍数</th><td>{{ item.coats }} 遍</td></tr>
  </table>
  <p><router-link to="/history">返回记录列表</router-link></p>
</div></template>
