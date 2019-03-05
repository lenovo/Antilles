<style>
.termwindow {
  padding-top: 15px;
  border: #fafafa solid 1px;
  background: linear-gradient(to right, #282828, #444444);
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 200000;
  transition: opacity 0.5s;
  box-shadow: rgba(0, 0, 0, 0.8) 2px 2px 20px;
}

.maximized .termwindow {
  border: none;
  box-shadow: none;
}

.dark .termwindow {
  box-shadow: none;
}

.bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 13px;
  padding: 1px 0;
  font-family: "Courier New", "DejaVu Sans Mono", "Liberation Mono", monospace;
  color: #fafafa;
}

.dark .bar .maximized .bar {}

.title {
  position: absolute;
  left: 10px;
  top: 2px;
  font-size: 11px;
  cursor: default;
}

.tab {
  font-size: 13px;
  margin-right: 8px;
  margin-top: -2px;
  float: right;
  cursor: pointer;
}

.tab:hover {
  font-weight: bold;
}

.grip {
  position: absolute;
  bottom: -10px;
  right: -10px;
  width: 22px;
  height: 22px;
  cursor: se-resize;
  z-index: -1;
  background: transparent;
}

.grip:hover {}

.terminal {
  border: #000 solid 5px;
  font-family: "Courier New", "DejaVu Sans Mono", "Liberation Mono", monospace;
  font-size: 1pc;
  transition: font-size 0.5s;
  color: #f0f0f0;
  background: #000;
}

.reverse-video {
  color: #000;
  background: #f0f0f0;
}
</style>
<template>
<div id="terminalWindowElement" class="terminalWindowElement"></div>
</template>
<script>
export default {
  data() {
    return {
      popupCount: 0
    }
  },
  props: [
    'popup'
  ],
  methods: {
    openConsole(hostname) {
      this.open(hostname, 'console');
    },
    openSSH(hostname) {
      this.open(hostname, 'ssh');
    },
    open(hostname, type) {
      let offset = this.calculateOffsetAxis(this.popupCount);
      let terminal = new TerminalWindow('/api/nodes/' + hostname + '/' + type + '/sessions/', hostname + "  " + type, offset.xAxis, offset.yAxis);
      if (this.popup) {
        this.popupCount = this.popupCount + 1;
      } else {
        document.getElementById('terminalWindowElement').appendChild(terminal);
      }
    },
    calculateOffsetAxis(count) {
      return {
        yAxis: count * 30 + 100,
        xAxis: count * 30 + 100
      }
    }
  }
}
</script>
