<style>
.multi-tags-input {
  width: 100%;
  display: inline-block;
}
.multi-tags-input.multi-tags .el-tag+.el-tag {
  margin-left: 10px
}

.multi-tags-input.multi-tags .new-tag-button {
  margin-left: 10px;
  height: 24px;
  line-height: 22px;
  padding-top: 0;
  padding-bottom: 0
}

.multi-tags-input.multi-tags .new-tag-input {
  width: 160px;
  margin-left: 10px;
  vertical-align: bottom
}

.multi-tags-input.multi-tags .new-tag-input .el-input__inner {
  height: 24px
}

.multi-tags-input.multi-tags .error-label {
  color: #ff4949;
  font-size: 12px;
  padding-top: 4px;
  left: 0;
}
</style>
<template>
<div class="multi-tags-input multi-tags">
  <el-tag
    :key="tag"
    v-for="tag in value"
    :closable="!disabled"
    :close-transition="true"
    @close="onTagClose(tag)">
    {{tag}}
  </el-tag>
  <el-input id="tid_multi-tags-input"
    class="new-tag-input"
    v-show="inputVisible && !disabled"
    v-model="inputValue"
    ref="newTagInput"
    size="mini"
    @keyup.enter.native="onNewTagInputConfirm"
    @blur="onNewTagInputConfirm">
  </el-input>
  <el-button id="tid_multi-tags-new"
    class="new-tag-button"
    size="small"
    v-show="!inputVisible && !disabled"
    @click="showInput">
    {{newTagButtonText}}
  </el-button>
  <el-button id="tid_multi-tags-clean"
    class="new-tag-button" size="small" type="danger"
    v-if="!inputVisible && this.value.length > 0 && !disabled"
    @click="cleanTags">
    {{$t("MultiTagsInput.Clean")}}
  </el-button>
  <span v-if="errorMessage.length > 0" class="error-label">{{errorMessage}}</span>
</div>
</template>
<script>
import Schema from 'async-validator'

export default {
  data() {
    return {
      //tags: [],
      inputVisible: false,
      inputValue: '',
      errorMessage: ''
    };
  },
  props: {
    value: Array,
    newTagButtonText: String,
    validRoles: Array,
    disabled: {
      type: Boolean,
      default: true
    }
  },
  methods: {
    copyArray(arr) {
      var newArr = new Array();
      arr.forEach((item) => {
        newArr.push(item);
      });
      return newArr;
    },
    onTagClose(tag) {
      //this.value.splice(this.value.indexOf(tag), 1);
      var newValue = this.copyArray(this.value);
      newValue.splice(newValue.indexOf(tag), 1);
      this.$emit('input', newValue);
    },
    showInput() {
      this.inputVisible = true;
      this.$nextTick(() => {
       this.$refs.newTagInput.$refs.input.focus();
      });
    },
    cleanTags() {
      //this.value.splice(0, this.value.length);
      this.$emit('input', []);
    },
    onNewTagInputConfirm() {
      let inputValue = this.inputValue;
      let validRoles = this.validRoles;
      if(validRoles) {
        var descriptor = {
          email: validRoles
        };
        var validator = new Schema(descriptor);
        validator.validate({email: inputValue}, (errors, fields) => {
          if(errors) {
            this.errorMessage = errors[0].message;
          } else {
            this.insertTag();
          }
        });
      } else {
        this.insertTag();
      }
    },
    insertTag() {
      let inputValue = this.inputValue;
      if (inputValue) {
        //this.value.push(inputValue);
        var newValue = this.copyArray(this.value);
        newValue.push(inputValue);
        this.$emit('input', newValue);
      }
      this.inputVisible = false;
      this.inputValue = '';
      this.errorMessage = '';
    },
    validate() {
      if(this.errorMessage.length > 0) {
        return false;
      } else {
        return true;
      }
    },
    cleanInput() {
      this.inputVisible = false;
      this.inputValue = '';
      this.errorMessage = '';
    }
  }
}
</script>
