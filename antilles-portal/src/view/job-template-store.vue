<style scoped>
.store-container-top{
  margin-bottom: 20px;
}
.store-container{
  box-sizing: border-box;
}
.createMyTemplate {
  box-sizing: border-box;
  border: 1px solid #eee;
  border-radius: 4px;
  height: 330px;
}
.createMyTemplate-card-logo{
  text-align: center;
  margin-top: 45px;
}
.createMyTemplate-card-logo i{
  display: inline-block;
  height: 150px;
  width: 150px;
  font-size: 120px;
  color: #F1F1F1;
}
.createMyTemplate-card-btn{
  text-align: center;
  margin-top: 35px;
}
</style>
<template>
<div class="height--100 p-10">
  <div class="store-container b-w p-20">
    <el-row class="store-container-top">
      <el-col :span="18" align="left">
        <el-radio-group v-model="selected">
          <el-radio-button v-for="category in categories"
            :key="category.key"
            :label="category.key">
            {{getCategoryDisplayName(category.name)}}
          </el-radio-button>
        </el-radio-group>
      </el-col>
      <el-col :span="6" align="right">
        <el-radio-group v-model="selected">
          <el-radio-button v-for="mode in modes"
            :key="mode.key"
            :label="mode.key">
            {{mode.name}}
          </el-radio-button>
        </el-radio-group>
      </el-col>
    </el-row>
    <el-row>
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-show="selected == 'mytemplates'">
        <div class="createMyTemplate p-20 m-r-20 m-b-20">
          <div class="createMyTemplate-card-logo">
            <i class="el-erp-models"></i>
          </div>
          <!-- <div class="card-title">&nbsp;</div> -->
          <div class="card-description">&nbsp;</div>
          <div class="createMyTemplate-card-btn">
            <el-button type="primary" style="width:75%;" size="small" @click="onCreateClick">{{$t('JobTemplateStore.Create')}}</el-button>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="jobTemplate in jobTemplates"
        :key="jobTemplate.code" class="store-container-middle">
        <job-template-card
          :jobTemplate="jobTemplate"
          @delete-click="onDeleteClick"
          @publish-click="onPublishClick"
          @unpublish-click="onUnpublishClick">
        </job-template-card>
      </el-col>
    </el-row>
    <el-row style="text-align:right;padding-right:15px;">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-size="pageSize"
        layout="total, prev, pager, next, jumper"
        :total="total">
      </el-pagination>
    </el-row>
  </div>
  <job-template-action-dialog id="tid_job-template-action-dialog" ref="actionDialog" />
</div>
</template>
<script>
import JobTemplateService from '../service/job-template.js'
import JobTemplateCard from './job-template-store/job-template-card'
import JobTemplateActionDialog from './job-template-store/job-template-action-dialog'
import Collection from '../common/collection'

export default {
  data() {
    return {
      jobTemplates: [],
      categories: [],
      modes: [
        {
          key: 'mytemplates',
          name: this.$t('JobTemplateStore.Mode.Mine')
        }
      ],
      selected: '',
      currentPage: 1,
      pageSize: 16,
      total: 0
    };
  },
  components: {
    'job-template-card': JobTemplateCard,
    'job-template-action-dialog': JobTemplateActionDialog
  },
  mounted() {
    var route = this.$route.path;
    this.selected = route.split('/').pop();
  },
  watch: {
    selected(val, oldVal) {
      this.$router.push({ path: `/main/job-template-store/${val}` });
      this.initJobTemplates();
    },
    categories(val, oldVal) {
      if(this.selected != 'mytemplates' && !this.isIncludes(val, this.selected)) {
        this.selected = val[0].key
      }
    }
  },
  methods: {
    initJobTemplates() {
      var filterJobTemplates = [];
      JobTemplateService.getAllJobTemplates().then((res) => {
        this.categories = [];
        var systemCategories = [];
        var publicCategories = [];
        res.forEach((jobTemplate) => {
          var categories = null;
          if(jobTemplate.type == 'system' || jobTemplate.type == 'public') {
            var existCategory = false;
            for(var i=0; i<systemCategories.length; i++) {
              if(systemCategories[i].key == jobTemplate.category) {
                existCategory = true;
                break;
              }
            }
            for(var i=0; i<publicCategories.length; i++) {
              if(publicCategories[i].key == jobTemplate.category) {
                existCategory = true;
                break;
              }
            }
            if(!existCategory) {
              if(jobTemplate.type == 'system') {
                systemCategories.push({
                  key: jobTemplate.category,
                  name: jobTemplate.category
                });
              }
              if(jobTemplate.type == 'public') {
                publicCategories.push({
                  key: jobTemplate.category,
                  name: jobTemplate.category
                });
              }
            }
          }
          if(this.selected == 'mytemplates') {
            if(jobTemplate.type == 'private') {
              filterJobTemplates.push(jobTemplate);
            }
          } else {
            if((jobTemplate.type == 'system' || jobTemplate.type == 'public')
              && this.selected == jobTemplate.category) {
              filterJobTemplates.push(jobTemplate);
            }
          }
        });
        this.total = filterJobTemplates.length;
        this.jobTemplates = filterJobTemplates.splice((this.currentPage-1)*this.pageSize, this.pageSize);
        systemCategories = this.sortCategory(systemCategories);
        systemCategories.forEach((category) => {
          this.categories.push(category);
        });
        Collection.sortObjectsByProp(publicCategories, 'name', 'asc');
        publicCategories.forEach((category) => {
          this.categories.push(category);
        });
      }, (res) => {
        this.$message.error(res);
      })
    },
    isIncludes(val, selected) {
      var key = false;
      val.forEach((item) => {
        if(item.key == selected) {
          key = true;
        }
      })
      return key;
    },
    isSystemCategory(categroy) {
      if(['HPC', 'General'].includes(categroy)) {
        return true;
      } else {
        return false;
      }
    },
    sortCategory(categories) {
      var defaultCategories = ['HPC', 'General'];
      var sortCategories = [];
      defaultCategories.forEach((item) => {
        for(var i=0;i<categories.length;i++) {
          if(categories[i].key == item) {
            sortCategories.push(categories[i])
            break;
          }
        }
      })
      return sortCategories;
    },
    onCreateClick() {
      this.$router.push({ path: '/main/job-template-editor/' });
    },
    onDeleteClick(jobTemplate) {
      this.$refs.actionDialog.doDelete(jobTemplate).then((res) => {
        this.initJobTemplates();
      }, (res) => {
        // Do nothing
      });
    },
    onPublishClick(jobTemplate) {
      this.$refs.actionDialog.doPublish(jobTemplate).then((res) => {
        this.initJobTemplates();
      }, (res) => {
        // Do nothing
      });
    },
    onUnpublishClick(jobTemplate) {
      this.$refs.actionDialog.doUnpublish(jobTemplate).then((res) => {
        this.initJobTemplates();
      }, (res) => {
        // Do nothing
      });
    },
    handleSizeChange(val) {
      this.pageSize = val;
      this.initJobTemplates();
    },
    handleCurrentChange(val) {
      this.currentPage = val;
      this.initJobTemplates();
    },
    getCategoryDisplayName(name) {
      if(this.isSystemCategory(name)) {
        return this.$t(`JobTemplateStore.Category.${name}`);
      } else {
        return name;
      }
    }
  }
}
</script>
