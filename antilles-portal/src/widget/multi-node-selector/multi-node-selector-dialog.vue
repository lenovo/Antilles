<template>
  <composite-form-dialog ref="innerDialog"
    :title="$t('MultNode.Title')"
    size="500px"
   :form-model="selectForm"
   :form-rules="selectRules">
    <!--Filter-->
    <el-form-item :label="$t('MultNode.Filter')">
      <el-select v-model="selectForm.filterValue"  @change="resetFormValidation(selectForm.filterValue)">
        <el-option
          v-for="item in filterOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value">
        </el-option>
      </el-select>
    </el-form-item>
    <!--By hostname-->
    <el-form-item :label="$t('MultNode.Nodes')" v-if="this.selectForm.filterValue=='hostname'" prop="hostnameValue">
      <el-input type="textarea" :autosize="{ minRows: 4, maxRows: 6 }" v-model="selectForm.hostnameValue" :placeholder="placeholderAll"></el-input>
    </el-form-item>
    <!--By rack-->
    <el-form-item :label="$t('MultNode.Racks')" v-if="this.selectForm.filterValue=='rack'" prop="rackValue">
      <el-select
        v-model="selectForm.rackValue"
        multiple
        :placeholder="placeholderAll">
        <el-option
          v-for="item in rackOptions"
          :key="item.value"
          :label="item.name"
          :value="item.value">
        </el-option>
      </el-select>
    </el-form-item>
    <!--By node group-->
    <el-form-item :label="$t('MultNode.NodeGroups')" v-if="this.selectForm.filterValue=='nodegroup'" prop="nodeGroupValue">
      <el-select
        v-model="selectForm.nodeGroupValue"
        multiple
        :placeholder="placeholderAll">
        <el-option
          v-for="item in nodeGroupOptions"
          :key="item.value"
          :label="item.name"
          :value="item.name">
        </el-option>
      </el-select>
    </el-form-item>
    <el-form-item  v-show="selectForm.hostnameValue||selectForm.rackValue.length>0||selectForm.nodeGroupValue.length>0">
      <el-button @click="onClearClick" size="mini" type="danger">{{$t('MultiTagsInput.Clean')}}</el-button>
    </el-form-item>
  </composite-form-dialog>
</template>

<script>
  import CompositeFormDialog from '../../component/composite-form-dialog'
  import RackService from '../../service/rack'
  import NodeGroupService from '../../service/node-group'

  export default {
    components:{
      'composite-form-dialog':CompositeFormDialog
    },
    data(){
      return {        
        filterOptions: [],
        rackOptions: [],
        nodeGroupOptions: [],
        selectForm:{
          filterValue:'',
          hostnameValue:'',
          rackValue:[],
          nodeGroupValue:[],
        },
        selectRules:{
          hostnameValue:[{
            validator: (rule,value,callback) =>{
              let reg = /^[a-zA-Z0-9_,-]*$/;
              let arrValueLength = 1;
              for (let i in value){
                if (value[i]==','){
                  arrValueLength++;
                }
              }
              if(arrValueLength>this.hostnameMax){
                callback(new Error(this.$t('MultNode.Error.Limit')));
              }else if (value.length==0){
                if (this.allable){
                  callback();
                } else {
                  callback(new Error(this.$t('MultNode.Error.Empty')));
                }
              } else if (!reg.test(value)) {
                callback(new Error(this.$t('MultNode.Error.Format')));
              }else {
                callback();
              }
            },
            required: true
          }],
          rackValue:[{
            validator: (rule, value, callback) =>{
              if(value.length>this.rackMax){
                callback(new Error(this.$t('MultNode.Error.Limit')));
              }else if (value.length==0){
                if (this.allable){
                  callback();
                } else {
                  callback(new Error(this.$t('MultNode.Error.Empty')));
                }
              } else{
                callback();
              }
            },
            required: true
          }],
          nodeGroupValue:[{
            validator: (rule, value, callback) =>{
              if(value.length>this.nodeGroupMax){
                callback(new Error(this.$t('MultNode.Error.Limit')))
              }else if (value.length==0){
                if (this.allable){
                  callback();
                } else {
                  callback(new Error(this.$t('MultNode.Error.Empty')));
                }
              } else {
                callback();
              }
            },
            required: true
          }]
        }
      }
    },
    props:[
      'filterType',
      'hostnameMax',
      'rackMax',
      'nodeGroupMax',
      'allable'
    ],
    mounted(){
      this.initFilterOptions();
    },
    computed:{
      placeholderAll(){
        if (this.allable){
          return this.$t('MultNode.Select.All');
        } else {
          if (this.selectForm.filterValue=='hostname'){
            return this.$t('MultNode.Placeholder.Hostname')
          } else if (this.selectForm.filterValue=='rack'){
            return this.$t('MultNode.Placeholder.Rack')
          }else {
            return this.$t('MultNode.Placeholder.NodeGroup')
          }
        }
      }
    },
    methods:{
      submitForm(){
        let _this = this;
        switch(this.selectForm.filterValue)
        {
          case 'hostname':
            let arrNodesValue = this.selectForm.hostnameValue.split(',')
            return({
              "value_type":"hostname",
              "values":this.emptyIsAll(arrNodesValue)
            });
            break;
          case 'rack':
            return({
              "value_type":"rack",
              "values":this.emptyIsAll(_this.selectForm.rackValue)
            });
            break;
          case 'nodegroup':
            return({
              "value_type":"nodegroup",
              "values":this.emptyIsAll(_this.selectForm.nodeGroupValue)
            });
            break;
          default:
        }
      },
      selectNode(nodeValueObj,filterValue){
        this.initOptions();
        // Reset the form data
        this.selectForm={
          filterValue:filterValue||nodeValueObj.value_type,
          hostnameValue:'',
          rackValue:[],
          nodeGroupValue:[],
        }       
        if (nodeValueObj.values =='all'){
          this.selectForm.hostnameValue='';
          this.selectForm.rackValue=[];
          this.selectForm.nodeGroupValue=[];
        }else {
          if (nodeValueObj.value_type == 'hostname'){
            let hostnameValue = "";
            for (var i in nodeValueObj.values){
              hostnameValue+=nodeValueObj.values[i]+',';
            }
            this.selectForm.hostnameValue = hostnameValue.slice(0,hostnameValue.length-1);
          } else if (nodeValueObj.value_type=='rack') {
            this.selectForm.rackValue = nodeValueObj.values;
          } else {
            this.selectForm.nodeGroupValue = nodeValueObj.values;
          }
        }
        // Close the dialog and assign the form data to the node-selector
        this.$refs.innerDialog.emptyPopup().then((res) => {
          this.$parent.nodeValueObj = this.submitForm();
        },(res) => {
          // Do nothing
        });
      },
      initOptions() {
        this.rackOptions=[];
        this.nodeGroupOptions=[];
        RackService.getAllRacks().then((res)=>{
          for (let i in res) {
            this.rackOptions.push(
              {
                name:res[i].name,
                value:res[i].id
              });
          }
        });
        NodeGroupService.getAllNodeGroups().then((res)=>{
          for (let i in res) {
            this.nodeGroupOptions.push({
              name: res[i]._name,
              value:res[i]._id
            });
          }
        });
      },
      initFilterOptions(){
        let arrFilterType = this.filterType.split(",");
        for (var i in arrFilterType){
          this.filterOptions.push({value: arrFilterType[i] , label: this.$t(`MultNode.Select.By${arrFilterType[i]}`)})
        }
      },
      emptyIsAll(valuesArr){
        if (valuesArr.length==0||(valuesArr.length==1&&valuesArr[0]=='')) {
          return []
        }else {
          return valuesArr
        }
      },
      resetFormValidation(filterValue){
        this.$parent.onSelectClick(this.$parent.nodeValueObj,filterValue)
      },
      onClearClick(){        
        this.selectForm.hostnameValue = '';
        this.selectForm.rackValue = [];
        this.selectForm.nodeGroupValue = [];
      }   
    }
  }
</script>