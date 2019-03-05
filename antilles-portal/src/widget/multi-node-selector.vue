<style>
  .multi-node-selector .el-input{width: 300px;}
</style>
<template>
  <div class="multi-node-selector">
    <el-input v-model="inputValue" readonly :placeholder="placeholderAll"></el-input>
    <el-button type="primary" @click="onSelectClick(nodeValueObj)">{{$t('MultNode.Select')}}</el-button>
    <multi-node-selector-dialog ref="multiNodeSelectorDialog"
      :filterType="filterType"
      :hostnameMax="hostnameMax"
      :rackMax="rackMax"
      :nodeGroupMax="nodeGroupMax"
      :allable="allable"
    >
    </multi-node-selector-dialog>
  </div>
</template>
<script>
  import MultiNodeSelectorDialog from '../widget/multi-node-selector/multi-node-selector-dialog'
  import RackService from '../service/rack'
  export default {
    data(){
      return {
        nodeValueObj:'',
        inputValue:'',
      }
    },
    components:{
      'multi-node-selector-dialog':MultiNodeSelectorDialog
    },
    props:{
      filterType:{
        default:'hostname,rack,nodegroup'
      },
      'hostnameMax':{
        default:10
      },
      'rackMax':{
        default:10
      },
      'nodeGroupMax':{
        default:10
      },
      'allable':{
        default:true
      },
      'nodes':{
        default:()=>{
         return {'value_type':'hostname','values':[]}
        }
      }
    },
    mounted(){
      this.handleNodes();
      this.renderingData(this.nodeValueObj);
    },
    computed:{
      placeholderAll(){
        if (this.allable==true){
          return this.$t('MultNode.Select.All');
        } else {
          return this.$t('MultNode.Select.Placeholder');
        }
      }
    },
    watch:{
      nodeValueObj:function (val) {
        this.$emit('nodes-selected-change', val);
        this.renderingData(this.nodeValueObj);
      },
      nodes:function (val) {
        this.handleNodes();
      }
    },
    methods:{
      onSelectClick(nodeValueObj,filterValue){
        this.$refs.multiNodeSelectorDialog.selectNode(nodeValueObj,filterValue)
      },
      renderingData(nodeValueObj){
        this.inputValue='';
        let index='';
        let rackOptions=[];
        if (nodeValueObj.values.length==0){
            this.inputValue='';
        } else {
          if (nodeValueObj.value_type=='hostname'){
            for (let i in nodeValueObj.values){
              this.inputValue+=nodeValueObj.values[i]+',';
            }
          } else if (nodeValueObj.value_type=='rack'){
            this.escapeRack(nodeValueObj,index,rackOptions);
          } else {
            for (let i in nodeValueObj.values){
              this.inputValue+=nodeValueObj.values[i]+',';
            }
          }
        }
        this.inputValue=this.inputValue.slice(0,this.inputValue.length-1);
      },
      escapeRack(nodeValueObj,index,rackOptions){
        RackService.getAllRacks().then((res)=>{
          for (let i in res) {
            rackOptions.push(
              {
                name:res[i].name,
                value:res[i].id
              });
          }
        }).then(()=>{
          this.inputValue="";
          nodeValueObj.values.forEach((value,index)=>{
            for (let i in rackOptions){
              if (rackOptions[i].value==value){
                this.inputValue+=rackOptions[i].name+',';
              }
            }
          });
          this.inputValue=this.inputValue.slice(0,this.inputValue.length-1);
        });
      },
      handleNodes(){
        if(this.nodes.length==0){
          this.nodeValueObj={'value_type':'hostname','values':[]}
        }else {
          this.nodeValueObj=this.nodes
        }
      }
    }
  }
</script>