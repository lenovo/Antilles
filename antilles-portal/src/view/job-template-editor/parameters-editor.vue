
<style lang="css">
.job-template-parameters-table-header {
  background-color: #EEEEEE !important;
}
.parameters-add {
  margin: 20px;
}
</style>
<template lang="html">
  <div class="parameters-add">
    <el-row class="m-b-20">
        <el-button class="parameters-add-but" @click='addParameter'>{{$t('JobTemplate.Parameters.Add.button')}}</el-button>
    </el-row>
    <el-row>
      <el-table
      ref='parameterTable'
      :data="parameters"
      :border='true'
      header-cell-class-name='job-template-parameters-table-header'
      style="width: 100%">
      <el-table-column
        prop="id"
        :label="$t('JobTemplate.Parameters.Table.Id')"
        align='left'
        width="260">
      </el-table-column>
      <el-table-column
        prop="name"
        :label="$t('JobTemplate.Parameters.Table.Name')"
        align='left'>
      </el-table-column>
      <el-table-column
        prop="class"
        align='center'
        width='200'
        :formatter='columnFormatter'
        :label="$t('JobTemplate.Parameters.Table.Class')">
      </el-table-column>
      <el-table-column
        prop="dataType"
        align='center'
        width='150'
        :label="$t('JobTemplate.Parameters.Table.DataType')">
        <template slot-scope='scope'>{{$t(`JobTemplate.Parameters.DataType.${scope.row.dataType}`)}}</template>
      </el-table-column>
      <el-table-column
        prop="must"
        align='center'
        width='100'
        :label="$t('JobTemplate.Parameters.Table.Must')">
        <template slot-scope='scope'>{{scope.row.must?$t('JobTemplate.Parameters.Table.Must.Yse'):$t('JobTemplate.Parameters.Table.Must.No')}}</template>
      </el-table-column>
      <el-table-column
        align='center'
        width='200'
        :label="$t('JobTemplate.Parameters.Table.Action')">
        <template slot-scope='scope'>
          <span size="small" v-show="scope.row.type!='system'" class="table-but-icon button-edit" :title="$t('JobTemplate.Parameters.Table.Edit')" @click="editParameter(scope)"><i class="el-erp-edit"></i></span>
          <span size="small" v-show="scope.row.type!='system'" class="table-but-icon button-delete" :title="$t('JobTemplate.Parameters.Table.Delete')" @click="deleteParameter(scope)"><i class="el-erp-delete"></i></span>
        </template>
      </el-table-column>
    </el-table>
    </el-row>
    <parameter-dialog ref='parameterDialog' :external-validator="duplicateParameterValidator"/>
  </div>
</template>

<script>
import ParameterDialog from './parameter-dialog'
export default {
  data() {
    return {
      parameter: null
    }
  },
  components: {
    'parameter-dialog': ParameterDialog
  },
  props: [
    'parameters'
  ],
  mounted() {

  },
  methods: {
    addParameter() {
      this.$refs.parameterDialog.doAdd().then((res) => {
        this.parameters.push(res.data);
        console.log('data',res.data);
      })
    },
    editParameter(scope) {
      this.$refs.parameterDialog.doEdit(scope.row, scope.$index).then((res) => {
        this.parameters.splice(res.index, 1, res.data);
      });
    },
    deleteParameter(scope) {
      this.$refs.parameterDialog.doDelete(scope.row, scope.$index).then((res) => {
        this.parameters.splice(res.index, 1);
      });
    },
    duplicateParameterValidator(parameter, index) {
      for (var i = 0; i < this.parameters.length; i++) {
        if(i != index) {
          if(this.parameters[i].id == parameter.id) {
            return {name: 'Id', value: parameter.id};
          }
          if(this.parameters[i].name == parameter.name) {
            return {name: 'Name', value: parameter.name};
          }
        }
      }
      return null;
    },
    columnFormatter(row, column) {
      return row[column.property]=='base'?this.$t('JobTemplate.BaseInformation'):
                row[column.property]=='param'?this.$t('JobTemplate.Parameters'):
                    row[column.property]=='resource'?this.$t('JobTemplate.ResourceOptions'):
                        row[column.property];
    }
    // processParameter(data) {
    //   var obj = {};
    //   for(var key in data) {
    //     obj[key] = data[key];
    //   }
    //   return obj;
    // }
  }
}
</script>
