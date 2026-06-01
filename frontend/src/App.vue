<template>
  <n-config-provider :theme-overrides="{}">
    <n-message-provider>
      <n-h1 style="text-align:center;margin-top:40vh">脚手架就绪</n-h1>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
// 临时根组件：Task 17 会替换为带 RouterView 的版本
import { NConfigProvider, NMessageProvider, NH1 } from 'naive-ui'
</script>
