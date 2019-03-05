<style>
  .sidebar {
    display: flex;
    flex-direction: column;
  }
</style>
<template>
  <div id="tid_left-bar" class="sidebar antilles-left-bar">
    <logo :logo-url='logoUrl'></logo>
    <culster id="tid_cluster-status"></culster>
    <el-menu id="tid_leftbar-menu"
      ref="navigator"
      :unique-opened='true'
      background-color='#343C4A'
      text-color='#bfcad9'
      :default-active="defaultSelected"
      class="el-menu-vertical-demo"
      @select="handleSelect"
      :collapse="isCollapse">
      <template v-for="(item, index) in menu.concat(quickLinkMenu)">
        <el-submenu v-if="item.children.length>0" :index="String(index)">
          <template slot="title">
            <i :class="'el-erp-' + item.icon"></i>
            <span slot="title">{{ formatLabel(item) }}</span>
          </template>
          <el-menu-item v-for="list in item.children" :key="list.path" :index="list.path">
            <i :class="'el-erp-' + list.icon"></i>
            <span slot="title">{{ formatLabel(list) }}</span>
          </el-menu-item>
        </el-submenu>
        <el-menu-item v-else :index="item.path" >
          <!-- <i class="el-erp-home"></i> -->
          <i :class="'el-erp-'+ item.icon">{{outLogoUrl(item)}}</i>
          <span slot="title">{{ formatLabel(item) }}</span>
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>
<script>
  import Logo from './../../widget/logo'
  import Culster from './../../widget/culster-status'
  import AccessService from './../../service/access'
  import menu from './../../menu/menu'

  export default {
    data() {
      var access = this.$store.state.auth.access
      return {
        menu: AccessService.getMenuByAccess(access),
        quickLinkMenu: [],
        isCollapse: gApp.isCollapse,
        defaultSelected: '',
        logoUrl: '',
      };
    },
    components:{ Logo, Culster },
    mounted() {
      //this.defaultSelected = window.location.hash.replace('#','');
      this.setDefaultMenu();
      this.initQuickLinkMenu();
      var _this = this;
      gApp.$watch('isCollapse',function (newValue, oldValue) {
        _this.isCollapse = newValue;
      });
    },
    watch: {
      $route(val){
        this.setDefaultMenu();
      }
    },
    methods: {
      handleSelect(key, keyPath) {
        this.defaultSelected = key;
        if(key.indexOf('http') == 0) {
          window.open(key);
        } else {
          gApp.$router.push({path: key});
        }
      },
      outLogoUrl(item) {
        if(item.icon == 'home') {
          this.logoUrl = item.path;
        }
      },
      setDefaultMenu() {
        var route = this.$route;
        var access = this.$store.state.auth.access;
        var currentMenu = menu[access];
        var defaultMenu = this.findMenu(route, currentMenu);
        if(defaultMenu != null) {
          this.defaultSelected = defaultMenu.path;
        }
      },
      findMenu(route, subItems) {
        for(var i=0; i<subItems.length; i++) {
          var subItem = subItems[i];
          // Need improve this function to fit param better
          if(route.path.indexOf(subItem.path) == 0) {
            return subItem;
          }
          if(subItem.details) {
            for(var j=0; j<subItem.details.length; j++) {
              var detail = subItem.details[j];
              if(route.path.indexOf(detail.path) == 0) {
                return subItem;
              }
            }
          }
          var result = this.findMenu(route, subItem.children);
          if(result != null) {
            return result;
          }
        }
        return null;
      },
      initQuickLinkMenu() {
        AccessService.getQuickLinkMenu(this.$store.state.auth.access).then((res) => {
          this.quickLinkMenu = res;
        }, (res) => {
          this.$message.error(res);
        });
      },
      formatLabel(menu) {
        if(menu.quickLink) {
            return menu.label;
        }
        return this.$t('Menu.' + menu.label);
      }
    }
  }
</script>
