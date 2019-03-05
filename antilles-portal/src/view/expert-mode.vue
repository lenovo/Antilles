<style>
.expert-model .table-top-manage, .expert-model .job-tab, .expert-model .table-style{
  padding: 0;
}
</style>
<template>
<div class="height--100 p-10">
  <el-tabs v-model="activeName" @tab-click="handleClick" class="expert-model height--100 b-w p-20">
    <el-tab-pane :label="$t('ExpertMode.Shell')" name="shell">
      <web-shell ref="webShell"></web-shell>
    </el-tab-pane>
    <el-tab-pane :label="$t('ExpertMode.FileManage')" name="file-manager">
      <file-manager></file-manager>
    </el-tab-pane>
    <el-tab-pane :label="$t('ExpertMode.JobManage')" name="job-manager">
      <job-manage-view></job-manage-view>
    </el-tab-pane>
  </el-tabs>
</div>
</template>

<script>
import WebShell from '../widget/web-shell'
import FileManager from './../component/file-manager'
import JobManageView from './job-manage'

export default {
  data() {
    return {
      activeName: 'shell'
    };
  },
  components: {
    'web-shell': WebShell,
    'file-manager': FileManager,
    'job-manage-view': JobManageView
  },
  mounted() {
    // NodesService.getAllNodes().then((res) => {
    //   res.forEach((item) => {
    //     this.nodeSelectOptions.push({
    //       value: item.id,
    //       label: item.name
    //     });
    //   })
    //   this.selectedNode = res[0].id;
    // },(res) => {
    //   this.$message(res)
    // })
  },
  methods: {
    handleClick(tab, event) {
      this.$refs.webShell.autoResizeTerminalWindows();
    }
  }
}
</script>
