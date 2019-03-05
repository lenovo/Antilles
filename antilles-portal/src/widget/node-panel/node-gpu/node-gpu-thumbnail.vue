<style lang="css">
  .gpu-thumbnail {
    width: 72px;
    /*display: flex;*/
  }
  .gpu-thumbnail-up {
    height: 6px;
    margin: 5px 0 0;
    position: relative;
    top: 5px;
  }
  .gpu-thumbnail-up-active {
    background: #6bcb01 !important;
  }
  .gpu-thumbnail-down {
    margin: 0 0 20px;
    height: 190px;
    border: 1px solid #dddddd;
  }
  .gpu-thumbnail-down-active {
    background: #40aaff;
  }
  .gpu-name {
    transform: rotate(90deg) translateX(50%);
    position: relative;
    left: -195%;
    color: #666666;
    font-size: 14px;
    width: 100px;
    white-space: nowrap;
  }
  .gpu-name-active {
    color: #ffffff !important;
  }
  .gpu-message-up {
    height: 190px;
  }
  .gpu-message-down {
    text-align: right;
    color: #999999;
    font-size: 14px;
    padding: 0 5px 10px 0;
  }
  .gpu-message-down-active {
    color: #ffffff !important;
  }
  .gpu-message {
    margin: 100px 0 0;
    height: 90px;
  }
</style>
<template lang="html">
  <div class="gpu-thumbnail">
    <div class="gpu-thumbnail-up" :class="gpu.used ? 'gpu-thumbnail-up-active' : ''"></div>
    <div class="gpu-thumbnail-down" :class="gpu.index==current ? 'gpu-thumbnail-down-active' : ''">
      <el-row :gutter="10">
        <el-col :span='8'>
          <div class="gpu-message-up">
            <div class="gpu-name" :class="gpu.index==current ? 'gpu-name-active': ''">{{`${gpu.type}`}}</div>
          </div>
        </el-col>
        <div class="gpu-message">
          <el-col :span='16'>
            <el-row :gutter="10">
              <el-col>
                <div class="gpu-message-down" :class="gpu.index==current ? 'gpu-message-down-active' : ''">
                  {{temperature}}℃
                </div>
              </el-col>
            </el-row>
            <el-row :gutter="10">
              <el-col>
                <div class="gpu-message-down" :class="gpu.index==current ? 'gpu-message-down-active' : ''">
                  {{util}}%
                </div>
              </el-col>
            </el-row>
            <el-row :gutter="10">
              <el-col>
                <div class="gpu-message-down" :class="gpu.index==current ? 'gpu-message-down-active' : ''">
                  {{memory}}%
                </div>
              </el-col>
            </el-row>
          </el-col>
        </div>
      </el-row>
    </div>
  </div>
</template>

<script>
import Format from './../../../common/format'
import GpuService from '../../../service/monitor-data'
export default {
  data() {
    return {
      data: this.node,
      memory: '-',
      temperature: '-',
      util: '-'
    }
  },
  props: [
    'node',
    'gpu',
    'current'
  ],
  watch: {
    node(val, oldVal) {
      this.refresh()
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.refresh()
      gApp.$watch('isCollapse', (newValue, oldValue) => {
        setTimeout(() => {
          this.onResize();
        },300)
      })
    });
  },
  methods: {
    setValue(category) {
      GpuService.getNodeGpuDataByHour(this.data.id, this.gpu.index, category).then((res) => {
        if (res.data.length > 0) {
          let d = res.current
          this.callback(category, d)
        }
      })
    },
    refresh() {
      var self = this
      if(this.data != null && this.gpu.index != null) {
        this.setValue('ram')
        this.setValue('temperature')
        this.setValue('util')
      }
    },
    callback(category, value) {
      if (category == 'ram') {
        this.memory = Math.round(value * 10) / 10
      } else if (category == 'util') {
        this.util = Math.round(value * 10) / 10
      } else if (category == 'temperature') {
        this.temperature = Math.round(value * 10) / 10
      }
    }
  }
}
</script>
