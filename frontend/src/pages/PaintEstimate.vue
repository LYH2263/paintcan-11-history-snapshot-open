<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { postJSON } from '../api'
const router = useRouter()
const room_id = ref(1)
const persist = ref(true)
const out = ref(null)
const run = async () => {
  out.value = await postJSON('/api/estimate', { room_id: room_id.value, persist: persist.value })
  if (persist.value && out.value.run_id) router.push(`/history/${out.value.run_id}`)
}
</script>
<template><div class="page"><h1>估漆工作台</h1>
<label>房间ID <input v-model.number="room_id" /></label>
<label><input type="checkbox" v-model="persist" /> 写入记录</label>
<button @click="run">估算</button>
<p v-if="out" class="hint">净 {{ out.net_m2 }} m² · {{ out.liters }} 升 · {{ out.coats }} 遍
  <router-link v-if="out.run_id" :to="`/history/${out.run_id}`">查看编号 #{{ out.run_id }}</router-link></p></div></template>
