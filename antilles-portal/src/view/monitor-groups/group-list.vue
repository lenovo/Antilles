<style>

</style>
<template>
    <nodes-table :node-external-filter="nodeExternalFilter"></nodes-table>
</template>
<script>
  import NodesTable from '../../widget/nodes-table'
  export default {
    data(){
      return {

      }
    },
    props: [
      "nodeExternalFilter"
    ],
    components: {
      "nodes-table": NodesTable
    }
  }
</script>