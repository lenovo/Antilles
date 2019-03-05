<style lang="css">
.jobTemplate-parameter-add-dialog .el-form-item__content {
  width: 370px;
}
</style>
<template lang="html">
  <composite-form-dialog ref="innerDialog" size="580px"
    class="jobTemplate-parameter-add-dialog"
    :title="title"
    :form-model="formParameter"
    :form-rules="formRules"
    form-label-width='140px'
    :successMessageFormatter="successMessageFormatter"
    :errorMessageFormatter="errorMessageFormatter"
    :external-validate='externalValidate'
    >
    <el-form-item v-if="mode!='delete'" :label="$t('JobTemplate.Parameters.Id')" prop="id">
      <el-input id="tid_jobTemplate-parameter-id" v-model="formParameter.id"></el-input>
    </el-form-item>
    <el-form-item v-if="mode!='delete'" :label="$t('JobTemplate.Parameters.Name')" prop="name">
      <el-input id="tid_jobTemplate-parameter-name" v-model="formParameter.name"></el-input>
    </el-form-item>
    <el-form-item v-if="mode!='delete'" :label="$t('JobTemplate.Parameters.Class')" prop="class">
      <el-select id="tid_jobTemplate-parameter-class" v-model="formParameter.class">
        <el-option
          v-for="item in classOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value">
        </el-option>
      </el-select>
    </el-form-item>
    <el-form-item v-if="mode!='delete'" :label="$t('JobTemplate.Parameters.DataType')" prop="dataType">
      <el-select id="tid_jobTemplate-parameter-dataType" v-model="formParameter.dataType">
        <el-option
          v-for="item in dataTypeOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value">
        </el-option>
      </el-select>
    </el-form-item>
    <el-form-item  v-if="mode!='delete'&&(formParameter.dataType == 'string'||formParameter.dataType =='number')"
     :label="$t('JobTemplate.Parameters.Input')" prop="input">
      <el-select id="tid_jobTemplate-parameter-input" v-model="formParameter.input">
        <el-option
          v-for="item in inputOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value">
        </el-option>
      </el-select>
    </el-form-item>
    <string-option v-if="mode!='delete' && formParameter.dataType == 'string' && formParameter.input=='input'" :form-parameter='formParameter' :form-rules='formRules' ref='stringOption' />
    <number-option v-if="mode!='delete' && formParameter.dataType == 'number' && formParameter.input=='input'" :form-parameter='formParameter' :form-rules='formRules' ref='numberOption' :max-value-function='onMaxValueChange' :min-value-function='onMinValueChange'/>
    <select-option v-if="mode!='delete' && (formParameter.dataType == 'string' || formParameter.dataType=='number') && formParameter.input=='select'" :form-parameter='formParameter' :form-rules='formRules' ref='selectOption' />
    <file-option v-if="mode!='delete' && formParameter.dataType=='file'" ref='fileOption' />
    <folder-option v-if="mode!='delete' && formParameter.dataType=='folder'" ref='folderOption' />
    <el-form-item v-if="mode!='delete' && (formParameter.dataType == 'string' || formParameter.dataType =='number')" :label="$t('JobTemplate.Parameters.Default.Value')" prop="defaultValue">
      <el-input id="tid_jobTemplate-parameter-default-value" v-model="formParameter.defaultValue"></el-input>
    </el-form-item>
    <el-form-item v-if="mode!='delete'" :label="$t('JobTemplate.Parameters.Must')" prop="must">
      <el-checkbox id="tid_jobTemplate-parameter-must" v-model="formParameter.must"></el-checkbox>
    </el-form-item>
    <div class="" v-if="mode == 'delete'">
      <p>{{$t('JobTemplate.Parameters.Delete.Text', {name: formParameter.name})}}</p>
    </div>
  </composite-form-dialog>
</template>

<script>
import StringOption from './parameter-dialog/string-option'
import NumberOption from './parameter-dialog/number-option'
import SelectOption from './parameter-dialog/select-option'
import FileOption from './parameter-dialog/file-option'
import FolderOption from './parameter-dialog/folder-option'
import CompositeFormDialog from '../../component/composite-form-dialog'
import ValidRoleFactory from '../../common/valid-role-factory'
export default {
  data() {
    return {
      index: null,
      title: '',
      mode: '',
      invalidParameter: null,
      formParameter: {},
      formRules: {
        id: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Parameters.Id')),
          ValidRoleFactory.getLengthRoleForText(this.$t('JobTemplate.Parameters.Id'), 3, 32),
          ValidRoleFactory.getValidSystemNameRoleForText(this.$t('JobTemplate.Parameters.Id'), false)
        ],
        name: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Parameters.Name')),
          ValidRoleFactory.getLengthRoleForText(this.$t('JobTemplate.Parameters.Name'), 3, 32),
          //ValidRoleFactory.getValidIdentityNameRoleForText(this.$t('JobTemplate.Parameters.Name'))
        ],
        class: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Parameters.Class')),
          ValidRoleFactory.getLengthRoleForText(this.$t('JobTemplate.Parameters.Class'), 3, 32),
          ValidRoleFactory.getValidIdentityNameRoleForText(this.$t('JobTemplate.Parameters.Class'))
        ],
        dataType: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Parameters.DataType'))
        ],
        input: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Parameters.Input'))
        ],
        maxLength: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Parameters.Max.Length')),
          ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.Parameters.Max.Length')),
          ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.Parameters.Max.Length'), 1, 255),
          ValidRoleFactory.getNumberDecimalRoleForText(this.$t('JobTemplate.Parameters.Max.Length'), 0)
        ],
        minValue: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Parameters.Min.Value')),
          ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.Parameters.Min.Value')),
          // ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.Parameters.Min.Value'), 0, 99999999),
        ],
        maxValue: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Parameters.Max.Value')),
          ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.Parameters.Max.Value')),
          // ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.Parameters.Max.Value'), 0, 99999999),
        ],
        floatLength: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Parameters.Float.Length')),
          ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.Parameters.Float.Length')),
          ValidRoleFactory.getNumberDecimalRoleForText(this.$t('JobTemplate.Parameters.Float.Length'), 0),
          ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.Parameters.Float.Length'), 0, 6),
        ],
        selectOption: [],
        framework: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Parameters.framework')),
        ],
        defaultValue: [],
        must: [],
      },
      classOptions: [],
      inputOptions: [],
      dataTypeOptions: []
    };
  },
  components: {
    CompositeFormDialog,
    StringOption,
    NumberOption,
    SelectOption,
    FileOption,
    FolderOption
  },
  props: [
    'externalValidator'
  ],
  mounted() {
    this.initClassOptions();
    this.initInputOptions();
    this.initDataTypeOptions();
  },
  watch: {

  },
  methods: {
    initClassOptions() {
      this.classOptions = [{
        value: 'base',
        label: this.$t('JobTemplate.BaseInformation')
      },{
        value: 'param',
        label: this.$t('JobTemplate.Parameters')
      },{
        value: 'resource',
        label: this.$t('JobTemplate.ResourceOptions')
      }];
    },
    initInputOptions() {
      this.inputOptions = [{
        value: 'input',
        label: this.$t('JobTemplate.Parameters.Input.Input')
      },{
        value: 'select',
        label: this.$t('JobTemplate.Parameters.Input.Select')
      }];
    },
    initDataTypeOptions() {
      this.dataTypeOptions = [{
        value: 'string',
        label: this.$t('JobTemplate.Parameters.DataType.string')
      },{
        value: 'number',
        label: this.$t('JobTemplate.Parameters.DataType.number')
      },{
        value: 'file',
        label: this.$t('JobTemplate.Parameters.DataType.file')
      },{
        value: 'folder',
        label: this.$t('JobTemplate.Parameters.DataType.folder')
      }];
    },
    externalValidate(callback) {
      if(this.formParameter.dataType == 'number'
        && !isNaN(parseFloat(this.formParameter.minValue))
        && !isNaN(parseFloat(this.formParameter.maxValue))
        && parseFloat(this.formParameter.minValue) > parseFloat(this.formParameter.maxValue))
      {
        this.$message.error(this.$t('JobTemplate.Parameters.Max.Error'))
        callback(false);
      } else {
        callback(true);
      }
    },
    submitForm() {
      var param = this.getParameter();
      if(this.mode == 'delete' || this.externalValidator == null) {
        return new Promise((resolve, reject) => {
          resolve({'data': param, 'index': this.index});
        });
      } else {
        return new Promise((resolve, reject) => {
          if(param.input == 'select' && param.selectOption.length<1) {
            reject({name: '', value: ''});
          }
          var valid = this.externalValidator(param, this.index);
          if(valid != null) {
            reject(valid);
          } else {
            resolve({'data': param, 'index': this.index});
          }
        });
      }
    },
    successMessageFormatter(res) {
      if(this.mode == 'add') {
        return this.$t('JobTemplate.Parameters.Add.Success', {'name': this.formParameter.name});
      }
      if(this.mode == 'edit') {
        return this.$t('JobTemplate.Parameters.Edit.Success', {'name': this.formParameter.name});
      }
      if(this.mode == 'delete') {
        return this.$t('JobTemplate.Parameters.Delete.Success', {'name': this.formParameter.name});
      }
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      if(this.formParameter.input == 'select' && res.name == '' && res.value == '') {
        return this.$t('JobTemplate.Parameters.Select.Option.Nodata');
      }
      if(this.mode=='add') {
        return this.$t('JobTemplate.Parameters.Add.repeat', {label: this.$t(`JobTemplate.Parameters.${res.name}`), value: res.value})
      }
      if(this.mode=='edit') {
        return this.$t('JobTemplate.Parameters.Edit.repeat', {label: this.$t(`JobTemplate.Parameters.${res.name}`), value: res.value})
      }
      return this.$t(errMsg);
    },
    initData(data) {
      return {
        id: data ? data.id : '',
        name: data ? data.name : '',
        class: data ? data.class : 'base',
        dataType: data ? data.dataType : 'string',
        input: data ? data.input : 'input',
        maxLength: data && data.maxLength ? data.maxLength: 255,
        minValue: data && data.minValue ? data.minValue: 0,
        maxValue: data && data.maxValue ? data.maxValue: 99999999,
        floatLength: data && data.floatLength ? data.floatLength: 0,
        invalid: data && data.invalid ? data.invalid : 'none',
        framework: data && data.framework ? data.framework : '',
        selectOption: data && data.selectOption ? data.selectOption: [],
        defaultValue: data && data.defaultValue ? data.defaultValue: '',
        must: data ? data.must: true
      }
    },
    doAdd() {
      this.formParameter = this.initData();
      this.mode = 'add';
      this.index = null;
      this.title = this.$t('JobTemplate.Parameters.Add.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doEdit(data, index) {
      this.formParameter = this.initData(data);
      this.mode = 'edit';
      this.index = index;
      this.title = this.$t('JobTemplate.Parameters.Edit.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doDelete(data, index) {
      this.formParameter = this.initData(data);
      this.mode = 'delete';
      this.index = index;
      this.title = this.$t('JobTemplate.Parameters.Delete.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    getParameter() {
      var param = new Object();
      param.id = this.formParameter.id;
      param.name = this.formParameter.name;
      param.class = this.formParameter.class;
      param.dataType = this.formParameter.dataType;
      if(param.dataType == 'string') {
          param.input = this.formParameter.input;
          if(param.input == 'input') {
            param.maxLength = this.formParameter.maxLength;
            param.invalid = this.formParameter.invalid;
          }
          if(param.input == 'select') {
            param.selectOption = [];
            this.formParameter.selectOption.forEach((option) => {
              var item = new Object();
              item.label = option.label;
              item.value = option.value;
              param.selectOption.push(item);
            });
          }
          param.defaultValue = this.formParameter.defaultValue;
      }
      if(param.dataType == 'number') {
        param.input = this.formParameter.input;
        if(param.input == 'input') {
          param.minValue = this.formParameter.minValue;
          param.maxValue = this.formParameter.maxValue;
          param.floatLength = this.formParameter.floatLength;
        }
        if(param.input == 'select') {
          param.selectOption = [];
          this.formParameter.selectOption.forEach((option) => {
            var item = new Object();
            item.label = option.label;
            item.value = option.value;
            param.selectOption.push(item);
          });
        }
        param.defaultValue = this.formParameter.defaultValue;
      }
      if(param.dataType == 'image') {
        param.framework = this.formParameter.framework;
      }
      param.must = this.formParameter.must;
      return param;
    },
    onMaxValueChange(val) {
      // this.formRules.minValue[3] = ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.Parameters.Min.Value'), 0, this.formParameter.maxValue);
    },
    onMinValueChange(val) {
      // this.formRules.maxValue[3] = ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.Parameters.Max.Value'), this.formParameter.minValue, 99999999999);
    }
  }
}
</script>
