<style>
.card-container {
  box-sizing: border-box;
  height: 330px;
  padding: 20px;
  overflow: hidden;
  border:1px solid #eee;
  margin:0 20px 20px 0;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  position: relative;
}
.card-description {
  line-height: 20px;
  max-height: 240px;
  overflow: hidden;
  word-wrap: break-word;
  p::after {
    content: "...";
    bottom: 0;
    right: 0;
    padding-left: 20px;
    background: -webkit-linear-gradient(to right, transparent, #fff 55%);
    background: -o-linear-gradient(to right, transparent, #fff 55%);
    background: -moz-linear-gradient(to right, transparent, #fff 55%);
    background: linear-gradient(to right, transparent, #fff 55%);
  };
}
.card-logo{
  text-align: center;
  margin-top: 10px;
}
.card-logo img {
  width: 180px;
  height: 40px;
  object-fit: contain;
}
.card-title{
  font-size:16px;
  font-weight: bold;
  margin-top: 15px;
}
.card-description{
  font-size: 12px;
  color:#777;
  padding-top: 5px;
}
.card-action{
  margin-top: auto;
}
.template-card-delete{
  position: absolute;
  top: 0;
  right: 0;
  padding: 5px 0 5px 5px;
  cursor: pointer;
}
.template-card-delete:hover {
  background-color: #F1F1F1;
  color: #66b1ff;
}
.card-action-btn-icon {
  margin-left: 0px !important;
  padding-left: 10px;
  padding-right: 10px;
}
.card-action-btn-icon i {
  margin: 0;
}
.card-more-action {
  margin-left: 10px;
  /* float: right; */
}
.card-action-btn-icon:hover {
  background-color: #fff;
}
.card-action-btn-used {
  padding-left: 5px;
  padding-right: 5px;
}
</style>
<template>
<div class="card-container">
  <!-- <span :title="$t('JobTemplateStore.Delete')" class="template-card-delete" v-show="type == 'private'" @click="onDeleteClick">
    <i class="el-erp-delete"></i>
  </span> -->
  <div class="card-logo">
    <img :src="logo"/>
  </div>
  <div class="card-title">{{title}}</div>
  <div class="card-description">{{description}}</div>
  <div class="card-action">

    <el-button v-if="subTemplates.length <= 0"
      type="primary" size="small"
      @click="onUseClick(code)" >{{$t('JobTemplateStore.Use')}}</el-button>

    <el-button v-for="(subTemplate, index) in subTemplates"
      :type="subTemplate.default?'primary':''" size="small" :key="index"
      @click="onUseClick(subTemplate.default?code:subTemplate.code)" >{{subTemplate.label}}</el-button>

    <el-dropdown trigger="click" class="card-more-action" v-show="type == 'private' || (type == 'public' && $store.state.auth.userid == userId)" @command='doAction'>
      <el-button size="small" type="">
        {{$t('JobTemplateStore.Action')}}<i class="el-icon-arrow-down el-icon--right"></i>
      </el-button>
      <el-dropdown-menu slot="dropdown">
        <el-dropdown-item command='edit' v-show="type == 'private'">{{$t('JobTemplateStore.Edit')}}</el-dropdown-item>
        <el-dropdown-item command='copy' v-show="$store.state.auth.userid == userId">{{$t('JobTemplateStore.Copy')}}</el-dropdown-item>
        <el-dropdown-item command='publish' v-show="type == 'private'">{{$t('JobTemplateStore.Publish')}}</el-dropdown-item>
        <el-dropdown-item command='delete' v-show="type == 'private'">{{$t('JobTemplateStore.Delete')}}</el-dropdown-item>
        <el-dropdown-item command='unpublish' v-show="type == 'public' && $store.state.auth.userid == userId">{{$t('JobTemplateStore.Unpublish')}}</el-dropdown-item>
      </el-dropdown-menu>
    </el-dropdown>
    <!-- <el-button size="small" class="card-action-btn-icon" :title="$t('JobTemplateStore.Edit')"
      v-show="type == 'private'" @click="onEditClick"><i class="el-erp-edit"></i></el-button>
    <el-button size="small" class="card-action-btn-icon" :title="$t('JobTemplateStore.Publish')"
      v-show="type == 'private'" @click="onPublishClick"><i class="el-erp-Releases"></i></el-button>
      <el-button size="small" class="card-action-btn-icon" :title="$t('JobTemplateStore.Delete')"
        v-show="type == 'private'" @click="onDeleteClick"><i class="el-erp-delete"></i></el-button>
    <el-button size="small" class="card-action-btn-icon" :title="$t('JobTemplateStore.Unpublish')"
      v-show="type == 'public' && $store.state.auth.userid == userId"@click="onUnpublishClick"><i class="el-erp-Canceltherelease"></i></el-button> -->
  </div>
</div>
</template>
<script>
export default {
  data() {
    return {
      code: this.jobTemplate.code,
      logo: this.jobTemplate.logo,
      title: this.jobTemplate.name,
      description: this.jobTemplate.description,
      type: this.jobTemplate.type,
      userId: this.jobTemplate.userId,
      subTemplates: this.localizeSubTemplates(this.jobTemplate.subTemplates?this.jobTemplate.subTemplates:[])
    };
  },
  props: [
    'jobTemplate'
  ],
  methods: {
    getLocalizeVal(lang, label) {
      if(label[lang]) {
        return label[lang];
      }
      if(label['en']) {
        return label['en'];
      }
      return label;
    },
    localizeSubTemplates(subTemplates) {
      var lang = this.$i18n.locale;
      subTemplates.forEach((subTemplate) => {
        subTemplate.label = this.getLocalizeVal(lang, subTemplate.label);
      });
      return subTemplates;
    },
    onUseClick(code) {
      if(isNaN(parseInt(code))) {
        this.$router.push({ path: '/main/job-template/' + code });
      } else {
        this.$router.push({ path: '/main/job-template-ex/' + code });
      }
    },
    doAction(command) {
      if(command == 'edit') {
        this.$router.push({ path: '/main/job-template-editor/' + this.code });
      } else if(command == 'copy'){
        this.$router.push({ path: '/main/job-template-editor/copy/' + this.code });
      } else {
        this.$emit(`${command}-click`, this.jobTemplate);
      }
    },
    onEditClick() {
      this.$router.push({ path: './job-template-editor/' + this.code });
    },
    onDeleteClick() {
      this.$emit('delete-click', this.jobTemplate);
    },
    onPublishClick() {
      this.$emit('publish-click', this.jobTemplate);
    },
    onUnpublishClick() {
      this.$emit('unpublish-click', this.jobTemplate);
    }
  }
}
</script>
