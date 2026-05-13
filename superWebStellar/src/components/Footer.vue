<template>
  <div></div>
</template>
<script lang="ts">
import { Vue } from 'vue-class-component';

export default class Footer extends Vue {

  year = 0
  mounted(){
    this.year = new Date().getUTCFullYear()
  }
}
</script>
