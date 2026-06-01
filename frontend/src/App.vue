<template>
  <n-config-provider :theme-overrides="{}">
    <n-message-provider>
      <RouterView />
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
// 根组件：注入 Naive UI 上下文，渲染当前路由视图
import { RouterView } from 'vue-router'
import { NConfigProvider, NMessageProvider } from 'naive-ui'
</script>
