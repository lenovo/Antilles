<style media="screen">
.rack-inner-public {
  position: relative;
  width: 100%;
  height: 100%;
}

.chassis-10u {
  position: absolute;
  width: 252px;
  height: 222px;
  left: 2px;
}

.chassis-2u {
  position: absolute;
  width: 252px;
  height: 40px;
  left: 2px;
}

.node-half {
  position: absolute;
  padding: 3px 1px 0px;
  box-sizing: border-box;
}
</style>

<template>
  <div class="">
    <div :style="rack_css">
      <div class="rack-inner-public">
        <div v-for="node in nodes" :style="get_node_css(node.location.height, node.location.width, node.location.u, node.frontimage)" v-if="node.location.chassisId == 'null'" @click="onNodeClick(node)">
          <physical-node :colors="levelColors" :ranges="levelRanges" :node='node' :mode='mode' node-type=''></physical-node>
        </div>
        <div v-for="sw in switches" :style="get_node_css(sw.location.height, sw.location.width, sw.location.u, sw.frontimage)">
          <physical-node :colors="levelColors" :ranges="levelRanges" :node='sw' :mode='mode' nodetype='switch'></physical-node>
        </div>
        <div v-for="c in chassis" :style="get_node_css(get_u_num(c.width_height[1]), 1, c.location.u, c.frontimage)">
          <div :style="get_chassis_css(c)">
            <div :id="'chassis_'+c.id" class="rack-inner-public">
              <div v-for="n in nodes"  @click="onNodeClick(n)" :style="get_node_css(n.location.height, n.location.width, n.location.u, n.frontimage, 'in_chassis', c)" v-if="n.location.chassisId == c.id">
                <physical-node :colors="levelColors" :ranges="levelRanges" :node='n' :mode='mode' nodetype=''></physical-node>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <level-card :colors="levelColors" :ranges="levelRanges" :mode="mode"></level-card>
  </div>
</template>

<script type="text/javascript">
import RackService from './../service/rack'
import PhysicalNode from '../widget/physicalnode'
import LevelCard from '../widget/levelcard'

export default {
  data() {
    return {
      rack: {},
      switches: {},
      chassis: {},
      nodes: {},
      tmp_node_loc: '66px',
      rack_css: {
        position: 'relative',
        top: '0px',
        left: '0px',
        width: '0px',
        height: '0px',
        padding: '0px 0px',
        'box-sizing': 'border-box',
        background: "url('./../../static/image/rack/rack_img/RACK.png') no-repeat"
      },
      levelRanges: {
        temp: [0, 100],
        energy: [0, 2000],
        load: [0, 100],
        cpu: [0, 100],
        mem: [0, 100],
        storage: [0, 100],
        network: [0, 50000],
      },
      levelColors: ['#F6EFA6', '#EFD79B', '#E9BF8F', '#E2A684', '#DB8E79', '#D57B6F', '#D06D66', '#CA605D', '#C55255', '#BF444C'],
    }
  },
  props: [
    "mode",
    "rackInfo"
  ],
  components: {
    'physical-node': PhysicalNode,
    'level-card': LevelCard,
  },
  mounted() {
    this.cookRackInfo();
  },
  methods: {
    cookRackInfo() {
      //RackService.getRackInfo().then((res) => {

      //get rack info
      this.rack = this.rackInfo;
      this.nodes = this.rackInfo.nodes;
      this.switches = this.rackInfo.switches;
      this.chassis = this.rackInfo.chassis;

      //set rack css
      this.rack_css.width = this.rack.width_height[0] + 'px';
      this.rack_css.height = this.rack.width_height[1] + 'px';
      this.rack_css.padding = this.rack.padding[0] + 'px ' + this.rack.padding[1] + 'px ' + this.rack.padding[2] + 'px ' + this.rack.padding[3] + 'px';

      //})
    },
    get_img(img_file) {
      return '../../../static/image/rack/rack_img/' + img_file;
    },
    get_u_num(height) {
      return Math.round((height) / (this.rack.uheight[0] + this.rack.gap[0]))
    },
    get_chassis_css(chassis) {
      var chassis_css = {
        position: 'absolute',
        padding: chassis.padding[0] + 'px ' + chassis.padding[1] + 'px ' + chassis.padding[2] + 'px ' + chassis.padding[3] + 'px',
        'box-sizing': 'border-box',
        width: '100%',
        height: '100%',
        bottom: '0px'
      };

      return chassis_css
    },
    get_node_css(u_height, u_width, location, image, type, chassis) {
      if (!type) {
        type = 'in_rack';
      }

      if (type == 'in_chassis' && chassis) {
        //var css_width = '49%';
        var css_width = String((chassis.width_height[0] - chassis.padding[1] * 2) / (1/u_width) - chassis.gap[1]) + 'px';
        if(u_width == 1 && location % 2 == 0) {
          location = location - 1;
        }
        if (location % 2 == 0) {
          //var css_left = '50%';
          var css_left = String(50 + 100 * chassis.gap[1] / (chassis.width_height[0] - chassis.padding[1] * 2)) + '%';
        } else {
          var css_left = '';
        }
        var node_css = {
          position: 'absolute',
          width: css_width,
          height: String(u_height * (chassis.uheight[0] - 2)) + 'px',
          bottom: String((Math.floor((parseInt(location) + 1) / 2) - 1) * (chassis.uheight[0]) + (Math.floor((parseInt(location) + 1) / 2) * (chassis.gap[0]) - chassis.gap[0] + 1)) + 'px',
          background: 'url(' + this.get_img(image) + ')',
          left: css_left
        };
      } else {
        if (location.substring(location.length - 1, location.length) == 'R') {
          var css_left = String(50 + 100 * this.rack.gap[1] / (this.rack.width_height[0] - this.rack.padding[1] * 2)) + '%';
          var loc = parseInt(location.substring(0, location.length - 2));
        } else if (location.substring(location.length - 1, location.length) == 'L') {
          var css_left = ''
          var loc = parseInt(location.substring(0, location.length - 2));
        } else {
          var css_left = ''
          var loc = location;
        }

        if (u_width != 0.5) {
          var css_width = String(u_width * (this.rack.width_height[0] - this.rack.padding[1] * 2)) + 'px';
        } else {
          var css_width = String((this.rack.width_height[0] - this.rack.padding[1] * 2) / 2 - this.rack.gap[1]) + 'px';
        }
        var node_css = {
          position: 'absolute',
          width: css_width,
          height: String(u_height * (this.rack.uheight[0]) + (u_height - 1) * this.rack.gap[0]) + 'px',
          //bottom: String((loc-1)*2+loc*21-2+15)+'px',
          bottom: String((loc - 1) * (this.rack.uheight[0] + this.rack.gap[0])) + 'px',
          background: 'url(' + this.get_img(image) + ')',
          left: css_left
        };
      }

      return node_css;
    },
    onNodeClick(node) {
      this.$emit('node-click', node.id);
    }
  }
}
</script>
