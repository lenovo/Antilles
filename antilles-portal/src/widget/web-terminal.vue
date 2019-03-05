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
</template>
<script>
import NodeService from '../service/node'

export default {
  data() {
    return {
      terminalWindows: [],
      terminalContainer: null,
      screenWidth: document.body.clientWidth,
      autoResizeTimerId: 0,
      autoConnectTimerId: 0,
      latestHostname: null
    }
  },
  mounted() {
    const self = this;
    window.onresize = () => {
      return(() => {
        self.screenWidth = document.body.clientWidth;
      })();
    };
    this.startAutoConnect();
  },
  watch: {
    screenWidth(val, oldVal) {
      if(this.autoResizeTimerId <= 0) {
        let self = this;
        self.autoResizeTimerId = setTimeout(function() {
          self.autoResizeTerminalWindows();
          self.autoResizeTimerId = 0;
        }, 200);
      }
    }
  },
  beforeDestroy() {
    window.onresize = null;
    this.stopAutoConnect();
  },
  methods: {
    popupConsole(hostname) {
      var serviceUrl = NodeService.getNodeConsoleServiceUrl(hostname);
      var title = this.$t('WebTerminal.Console.Title', {'hostname': hostname});
      this.createTerminalWindow(hostname, serviceUrl, title);
    },
    popupShell(hostname) {
      var serviceUrl = NodeService.getNodeShellServiceUrl(hostname);
      var title = this.$t('WebTerminal.Shell.Title', {'hostname': hostname});
      this.createTerminalWindow(hostname, serviceUrl, title);
    },
    initShell(hostname, domElement) {
      if(this.terminalWindows.length > 0) {
        window.CloseTerminals();
        this.terminalWindows = [];
        this.terminalContainer = null;
      }
      var serviceUrl = NodeService.getNodeShellServiceUrl(hostname);
      var title = this.$t('WebTerminal.Shell.Title', {'hostname': hostname})
      var terminal = this.createTerminalWindow(hostname, serviceUrl, title);
      var css = [
        'box-shadow: none',
        'position: relative',
        'float: left',
        'border: none',
        'padding-top: 0px',
        'top: 0px',
        'left: 0px',
        'z-index: 0'
      ]
      terminal.element.style.cssText = css.join(';');
      terminal.element.children[1].style.display = 'none';
      domElement.appendChild(terminal.element);
      this.terminalWindows.push(terminal);
      this.terminalContainer = domElement;
      this.$nextTick(() => {
        this.autoResizeTerminalWindows();
      });
    },
    createTerminalWindow(hostname, serviceUrl, title) {
      this.latestHostname = hostname;
      var position = this.calculateWindowPosition(this.terminalWindows.length);
      let terminalWindow = new TerminalWindow(serviceUrl,
        title,
        position.x,
        position.y);
      this.terminalWindows.push(terminalWindow);
      return terminalWindow;
    },
    calculateWindowPosition(index) {
      var startPosition = {
        x: 50,
        y: 50
      }
      return {
        x: startPosition.x + 10 * index,
        y: startPosition.y + 10 * index
      };
    },
    autoResizeTerminalWindows() {
      if(this.terminalWindows.length <= 0 || this.terminalContainer == null) {
        return;
      }
      var terminalWindow = this.terminalWindows[0];
      var container = this.terminalContainer;
      // console.log(terminalWindow);
      // console.log(container);
      // console.log(terminalWindow.element.clientHeight);
      // console.log(terminalWindow.element.clientWidth);
      // console.log(terminalWindow.rows);
      // console.log(terminalWindow.cols);
      // console.log(terminalWindow.element.style.visibility);
      if(terminalWindow.element.clientWidth > 0 &&
        terminalWindow.element.clientHeight > 0 &&
        terminalWindow.element.style.visibility != 'hidden') {
        var containerWidth = container.clientWidth;
        var containerHeight = container.clientHeight;
        var termWidth = terminalWindow.element.clientWidth;
        var termHeight = terminalWindow.element.clientHeight;
        var currentCols = terminalWindow.cols;
        var currentRows = terminalWindow.rows;
        var x = containerWidth / termWidth;
        var consoleCols = (x * currentCols) | 0;
        var y = containerHeight / termHeight;
        var consoleRows = (y * currentRows) | 0;
        terminalWindow.resize(consoleCols, consoleRows);
      }
    },
    startAutoConnect() {
      this.stopAutoConnect();
      let self = this;
      this.autoConnectTimerId = setTimeout(function() {
        if(self.terminalContainer != null) {
          if(self.terminalContainer.children.length <= 0) {
            self.initShell(self.latestHostname, self.terminalContainer);
          }
        }
        self.startAutoConnect();
      }, 1000);
    },
    stopAutoConnect() {
      if(this.autoConnectTimerId > 0) {
        clearTimeout(this.autoConnectTimerId);
      }
    }
  }
}
</script>
