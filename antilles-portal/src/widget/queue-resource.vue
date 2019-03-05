<style scoped>
  .container{
    display: inline-block;
  }
  @media screen and (max-width: 1336px) {
    .container{
      margin-top: 20px;
    }
  }
  .maxresourse{
    border-radius: 4px;
    display: flex;
    background:rgba(248,248,248,1);
  }
  .maxresourse li{
    margin-right: 20px;
    color:rgba(153,153,153,1);
  }
  .state{
    margin-left: 20px;
  }
</style>
<template>
  <div class="container">
    <div v-if="nodes!='' || cores!='' || memory!='' || wallTime!=''">
      <ul class="maxresourse">
        <li class="state"><i class="el-erp-state"></i>&nbsp;{{state}}</li>
        <li class="nodes"><i class="el-erp-monitor_node"></i>&nbsp;{{nodes}}</li>
        <li class="cores"><i class="el-erp-cpu"></i>&nbsp;{{cores}}</li>
        <li class="memory"><i class="el-erp-memory"></i>&nbsp;{{memory}}</li>
        <li class="walltime"><i class="el-erp-time"></i>&nbsp;{{wallTime}}</li>
      </ul>
    </div>
  </div>
</template>
<script>
export default {
  data(){
    return{

    }
  },
  props:['queueOptions','queue'],
  computed:{
    state: function () {
      var state = '';
      this.queueOptions.forEach(element => {
        if(element.value == this.queue){
          state = element.state;
        }
      });
      return state;
    },
    nodes: function () {
      var nodes = '';
      this.queueOptions.forEach(element => {
        if(element.value == this.queue){
          nodes = element.maxNodes == 'UNLIMITED' && element.totalNodes == 'UNLIMITED'
          ?'UNLIMITED'
          :element.maxNodes == 'UNLIMITED'
            ?element.totalNodes + ' / ' + element.totalNodes+ ' nodes'
            :element.totalNodes == 'UNLIMITED'
              ?element.maxNodes + ' nodes' + ' / ' + element.totalNodes
              :element.maxNodes + ' / ' + element.totalNodes+ ' nodes';
        }
      });
      return nodes;
    },
    cores: function () {
      var cores = '';
      this.queueOptions.forEach(element => {
        if(element.value == this.queue){
          cores = element.maxCoresPerNode == 'UNLIMITED' && element.totalCores == 'UNLIMITED'
          ?'UNLIMITED'
          :element.maxCoresPerNode == 'UNLIMITED'
            ?element.totalCores + ' / ' + element.totalCores+ ' cores'
            :element.totalCores == 'UNLIMITED'
              ?element.maxCoresPerNode + ' cores' + ' / ' + element.totalCores
              :element.maxCoresPerNode + ' / ' + element.totalCores+ ' cores';
        }
      });
      return cores;
    },
    memory: function () {
      var memory = '';
      this.queueOptions.forEach(element => {
        if(element.value == this.queue){
          memory = element.maxMemoryPerNode == 'UNLIMITED' && element.defineMemoryPerNode == 'UNLIMITED'
          ?'UNLIMITED'
          :element.maxMemoryPerNode == 'UNLIMITED'
            ?element.defineMemoryPerNode + ' / ' + element.defineMemoryPerNode+ ' MB'
            :element.defineMemoryPerNode == 'UNLIMITED'
              ?element.maxMemoryPerNode + ' MB' + ' / ' + element.defineMemoryPerNode
              :element.maxMemoryPerNode + ' / ' + element.defineMemoryPerNode+ ' MB';
        }
      });
      return memory;
    },
    wallTime: function () {
      var wallTime = '';
      this.queueOptions.forEach(element => {
        if(element.value == this.queue){
          wallTime = element.walltime;
        }
      });
      return wallTime;
    }
  }
}
</script>
