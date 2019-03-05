<style scoped>
.breadcrumb-container {
  padding-left: 10px;
  padding-right: 10px;
}
.breadcrumb-nolink {
  font-weight: 400;
  color: #606266;
  cursor: text;
}
</style>
<template>
<el-row class="breadcrumb-container">
  <el-col :span="22">
    <el-breadcrumb style="padding-top: 3px" separator-class="el-icon-arrow-right">
      <el-breadcrumb-item
        v-for="path in this.pathStack" :key="path.path"
        :to="{ path: path.path }">
        <span v-if="path.path && path.path.length > 0">{{path.name}}</span>
        <span v-else class="breadcrumb-nolink">{{path.name}}</span>
      </el-breadcrumb-item>
    </el-breadcrumb>
  </el-col>
  <el-col :span="2" align="right">
    <el-button v-show="this.pathStack.length > 1"
      @click="onBackClick" style="padding: 0px;" type="text">{{$t('Breadcrumb.Back')}}</el-button>
  </el-col>
</el-row>
</template>
<script>
import menu from '../menu/menu'
import JobService from '../service/job'
import UserService from '../service/user'
import RackService from '../service/rack'
import JobTemplateService from '../service/job-template'
export default {
  data () {
    return {
      pathStack: ['']
    }
  },
  watch:{
    $route() {
      this.init();
    }
  },
  mounted () {
    this.init();
  },
  methods:{
    init() {
      var route = this.$route;
      var access = this.$store.state.auth.access;
      var currentMenu = menu[access];
      var pathStack = [];
      // Only root menu can be home
      currentMenu.forEach((menu) => {
        if(menu.home) {
          pathStack.push(this.getPathByMenu(menu));
        }
      });
      this.findPath(route, pathStack, currentMenu);
      this.pathStack = pathStack;
    },
    findPath(route, pathStack, subItems) {
      for(var i=0; i<subItems.length; i++) {
        var subItem = subItems[i];
        if(subItem.home) {
          continue;
        }
        // Need improve this function to fit param
        if(route.path.indexOf(subItem.path) == 0) {
          pathStack.push(this.getPathByMenu(subItem));
          return true;
        }
        if(subItem.details) {
          for(var j=0; j<subItem.details.length; j++) {
            var detail = subItem.details[j];
            if(route.path.indexOf(detail.path) == 0) {
              pathStack.push(this.getPathByMenu(subItem));
              this.asyncAddPath(detail.type, route.params[detail.param]);
              return true;
            }
          }
        }
        pathStack.push(this.getPathByMenu(subItem));
        if(this.findPath(route, pathStack, subItem.children)) {
          return true;
        }
        pathStack.pop();
      }
      return false;
    },
    getPathByMenu(menu) {
      return {
        name: this.$t('Menu.' + menu.label),
        path: menu.path
      }
    },
    asyncAddPath(type, id) {
      if(type == 'user') {
        UserService.getUserById(id).then((res) => {
          this.addDetailPath(id, res.username);
        }, (res) => {
          this.$message.error(res);
        });
      }
      if(type == 'job') {
        JobService.getJobById(id).then((res) => {
          this.addDetailPath(id, res.name);
        }, (res) => {
          this.$message.error(res);
        });
      }
      if(type == 'rack') {
        RackService.getRackById(id).then((res) => {
          this.addDetailPath(id, res.name);
        }, (res) => {
          this.$message.error(res);
        })
      }
    },
    addDetailPath(id, name) {
      this.pathStack.push({
        name: name,
        path: ''
      });
    },
    onBackClick() {
      window.history.back();
    }
  }
}
</script>
