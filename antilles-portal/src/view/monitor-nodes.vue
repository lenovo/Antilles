<style scoped>
</style>
<template>
  <div class="height--100 p-10">
    <nodes-table></nodes-table>
  </div>
</template>
<script>
  import NodesTable from '../widget/nodes-table.vue'
  export default {
    data() {
      return {
      }
    },
    components: {
      'nodes-table': NodesTable
    }
  }
</script>
