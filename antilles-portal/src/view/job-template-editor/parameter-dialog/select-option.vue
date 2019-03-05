<style lang="css">
  .jobTemplate-parameter-select-option-table th{
    padding: 0;
  }
</style>
<template lang="html">
  <el-form-item :label="$t('JobTemplate.Parameters.Select.Option')" prop="selectOption">
    <!-- <el-input style="display: none;" v-model="formParameter.selectOption"></el-input> -->
    <el-table id="tid_jobTemplate-parameter-selectOption" :border='true' :data="tableData" header-row-class-name='jobTemplate-parameter-select-option-table'>
      <el-table-column
        prop="name"
        align='center'
        :label="$t('JobTemplate.Parameters.Select.Option.Name')"
        width="140">
        <template slot-scope='scope'>
          <el-input v-model='scope.row.name' @change='onLabelChange(scope)'></el-input>
        </template>
      </el-table-column>
      <el-table-column
        prop="value"
        align='center'
        :label="$t('JobTemplate.Parameters.Select.Option.Value')"
        width="140">
        <template slot-scope='scope'>
          <el-input v-model='scope.row.value' @change='onValueChange(scope)'></el-input>
        </template>
      </el-table-column>
      <el-table-column
        align='center'
        :label="$t('JobTemplate.Parameters.Select.Option.Action')">
        <template slot-scope='scope'>
          <span v-if='scope.$index>0' size="small" class="table-but-icon button-delete"
          :title="$t('JobTemplate.Parameters.Table.Delete')"
          @click="deleteOption(scope)"><i class="el-erp-delete"></i></span>
        </template>
      </el-table-column>
    </el-table>
    <el-button style="width:100%;" :disabled='tableData.length>=10'  @click='addOption'>{{$t('JobTemplate.Parameters.Select.Option.Add')}}</el-button>
  </el-form-item>
</template>

<script>
export default {
  data() {
    return {
      tableData: []
    }
  },
  props: [
    'formParameter',
    'formRules'
  ],
  mounted() {
    this.formParameter.selectOption.length<=0?this.addOption():
      this.formParameter.selectOption.forEach((item) => {
        this.addOption(item)
      })
  },
  watch: {
    formParameter: {
      handler: function(val, oldVal) {
        this.tableData = [];
        val.selectOption.length<=0?this.addOption():
          val.selectOption.forEach((item) => {
            this.addOption(item)
          })
      }
    }
  },
  methods: {
    onLabelChange(scope) {
      this.processData(scope.row, scope.$index)
    },
    onValueChange(scope) {
      this.processData(scope.row, scope.$index)
    },
    addOption(item) {
      this.tableData.push({
        name: item?item.label:'',
        value: item?item.value:''
      })
    },
    deleteOption(scope) {
      this.tableData.splice(scope.$index);
      this.formParameter.selectOption.splice(scope.$index);
    },
    processData(row, index) {
      var option = new Object();
      option.label = row.name||'';
      option.value = row.value||'';
      for(var i=0;i<this.formParameter.selectOption.length;i++){
        if(this.formParameter.selectOption[i].label==option.label && i!=index) {
          this.$message.error(this.$t('JobTemplate.Parameters.Select.Option.Repeat',{name: option.label}));
          return ;
        }
      }
      for(var i=0;i<this.tableData.length;i++){
        if(this.tableData[i].name==option.label && i != index) {
          this.$message.error(this.$t('JobTemplate.Parameters.Select.Option.Repeat',{name: option.label}));
          return ;
        }
      }
      if(index >= this.formParameter.selectOption.length) {
        if(option.label != '' && option.value != '') {
          this.formParameter.selectOption.push(option);
        }
      } else {
        this.formParameter.selectOption[index].label = option.label;
        this.formParameter.selectOption[index].value = option.value;
      }

    }
  }
}
</script>
