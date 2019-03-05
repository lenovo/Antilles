<style media="screen">
.popstyle {
    opacity:0.4;
    background-color: black;
    color: white;
}
.node_status{
    position: absolute;
    width: 10px;
    height: 10px;
    border-radius: 2px;
    left: 2px;
    z-index: 2;
}
</style>

<template>
    <span>
        <el-popover
          class="popstyle"
          ref="popover1"
          placement="top-start"
          :title="node.hostname"
          width="200"
          trigger="hover">
          <p>{{$t('Rack.Node.Status')+ ":" + node.status}}</p>
          <p>{{ extra_property }}</p>
        </el-popover>

        <template v-if="node_display != false">
            <span v-popover:popover1 :style= "{width: '100%', height: '100%', display: 'block' }">
            </span>
            <!--
                <div :style = "{background: 'url('+get_img(node.frontimage)+')' }">
                </div>
                <img  v-bind:src=get_img(node.frontimage) :style="{width: '100%', height: '100%'}">
            -->
            <i v-if="node.status == 'On'"  class="node_status" style="background: rgb(154, 253, 35); top: 6px; display: block;"></i>
            <i v-if="node.status == 'Off'"  class="node_status" style="background: red; top: 6px; display: block;"></i>
        </template>
        <template v-else>
            <span v-popover:popover1 :style= "{width: '100%', height: '100%', background: node_color, display: 'block' }">
            </span>
        </template>

    </span>
</template>

<script type="text/javascript">

  export default {
    data() {
      return {
        temp_range : this.ranges.temp,
        energy_range : this.ranges.energy,
        load_range : this.ranges.load,
        cpu_range : this.ranges.cpu,
        mem_range : this.ranges.mem,
        storage_range : this.ranges.storage,
        network_range : this.ranges.network,
        node_color: '#BF444C',
        node_display: false,
        extra_property: '',
        color_level: this.colors,
      }
    },
    props: ["mode", "nodetype", "node", "ranges", "colors"],
    mounted() {
      this.init_node();
      this.set_node_color(this.mode, this.nodetype);
      this.$watch('mode', function (a,b){
          if(this.mode != 'common'){this.node_display = false }
          else{this.node_display = true}
          this.set_node_color(this.mode, this.nodetype);
      });
    },
    methods: {
      get_img(img_file){
          return require('./../../static/image/rack/rack_img/' + img_file)
      },
      set_node_color(mode, nodetype){
          if(nodetype == 'switch'){
              this.node_color = '#FFFFFF';
              return;
          }
          if(mode == "temp"){
              var index = parseInt(this.node.temperature/this.temp_range[1] * 10)
              var i = 0;
              (index>this.color_level.length-1) ? i=this.color_level.length-1: i=index;
              this.node_color = this.color_level[i];
              this.extra_property = this.$t("Node.Temperature") + ":" + this.node.temperature + '℃\n';
          }else if(mode == "energy"){
              if(parseInt(this.node.energy)>=parseInt(this.energy_range[1])){this.energy_range[1]=parseInt(this.node.energy)+500}
              var index = parseInt(this.node.energy/this.energy_range[1] * 10)
              var i = 0;
              (index>this.color_level.length-1) ? i=this.color_level.length-1: i=index;
              this.node_color = this.color_level[i];
              this.extra_property = this.$t("Node.energy") + ":" + this.node.energy + 'W\n';
          }else if(mode == "load"){
              var index = parseInt(this.node.load/this.load_range[1] * 10);
              var i = 0;
              (index>this.color_level.length-1) ? i=this.color_level.length-1: i=index;
              this.node_color = this.color_level[i];
              this.extra_property = this.$t("Node.Load") + ":" + this.node.load + '\n';
          }else if(mode == "cpu"){
              var index = parseInt(this.node.cpuUsed/this.cpu_range[1] * 10)
              var i = 0;
              (index>this.color_level.length-1) ? i=this.color_level.length-1: i=index;
              this.node_color = this.color_level[i];
              this.extra_property = this.$t("NodeDetail.CPU.Unit") + ":"  + this.node.cpuUsed + '%\n';
          }else if(mode == "mem"){
              var index = parseInt(this.node.memoryUsed/this.mem_range[1] * 10)
              var i = 0;
              (index>this.color_level.length-1) ? i=this.color_level.length-1: i=index;
              this.node_color = this.color_level[i];
              this.extra_property = this.$t("Node.RAM") + ":" + this.node.memoryUsed + '%\n';
          }else if(mode == "storage"){
              var index = parseInt(this.node.diskUsed/this.storage_range[1] * 10)
              var i = 0;
              (index>this.color_level.length-1) ? i=this.color_level.length-1: i=index;
              this.node_color = this.color_level[i];
              this.extra_property = this.$t("Node.Storage") + ":" + this.node.diskUsed + '%\n';
          }else if(mode == "network"){
              // var raw_string = this.node.network;
              // var raw_list = raw_string.split(",");
              var raw_list = this.node.network;;
              var network = raw_list.reduce((a, b) => parseInt(a) + parseInt(b), 0);
              var index = parseInt(network/this.network_range[1] * 10);
              var i = 0;
              (index>this.color_level.length-1) ? i=this.color_level.length-1: i=index;
              this.node_color = this.color_level[i];
              this.extra_property = this.$t("NodeDetail.Network.In") + ":" + String(raw_list[0]) + ' Mbps\n, ' + this.$t("NodeDetail.Network.Out") + ":" + String(raw_list[1]) + ' Mbps\n';
          }

      },
      init_node(){
          if(this.mode == 'common'){this.node_display = true }
      }
    }
  }
</script>
