<template>
  <RouterView v-slot="{ Component }">
    <Transition name="route-fade" mode="out-in">
      <component :is="Component" />
    </Transition>
  </RouterView>
</template>

<script setup lang="ts">
import { Transition } from 'vue'
import { RouterView } from 'vue-router'
</script>
