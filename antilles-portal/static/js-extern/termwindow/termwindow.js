/**
 * termwindows.js is derived from tty.js:
 * https://github.com/chjj/tty.js/blob/master/static/tty.js
 *
 * Copyright (c) 2012-2013, Christopher Jeffrey (MIT License)
 * Copyright 2014, IBM Corporation
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

/**
 * Copyright © 2019-present Lenovo
 *
 * All changes implemented by Lenovo are licensed under both the BSD-3 license
 * for individual use and EPL-1.0 license for commercial use. Full text of both
 * licenses can be found in COPYING.BSD and COPYING.EPL files.
 */

;(function() {

'use strict'; // -Lenovo: catch probable issues
/**
 * Elements
 */

var document = this.document
  , window = this
  , root
  , body
  , h1
  , open
  , lights;

/**
 * Helpers
 */

/* Lenovo - Helper function to get access to titelbar for updates */
function getTextNode(element) {
    for (var i = 0; i < element.childNodes.length; i++) {
        if (element.childNodes[i].nodeType == Node.TEXT_NODE) {
            return element.childNodes[i];
        }
    }
}

var EventEmitter = Terminal.EventEmitter
  , inherits = Terminal.inherits
  , on = Terminal.on
  , off = Terminal.off
  , cancel = Terminal.cancel;
/**
 * Console
 */

/* Lenovo - Provide tracking of all termninals for bulk operations */
var allterms = [];
var currentfont = 'default';

/* Lenovo - Begin functions for multi terminal management */
function ScaleTerminals(factor) {
    if (factor == 1) {
        currentfont = 'default'
        var fontsize;
        if (localStorage.getItem('termfontfactor')) {
            var factor = localStorage.getItem('termfontfactor')
            factor = parseFloat(factor) / 100;
            fontsize = factor + 'pc';
        } else {
            fontsize = '1pc';
        }
        [].forEach.call(document.getElementsByClassName('terminal'), function(e) {
            e.style.fontSize = fontsize;
        });
    } else {
        [].forEach.call(document.getElementsByClassName('terminal'), function(e) {
            var currSize = document.defaultView.getComputedStyle(e).fontSize;
            var numeric = parseFloat(currSize) * factor;
            var suffix = currSize.replace(/[0-9\.]*/, '');
            e.style.fontSize = numeric + suffix;
            currentfont = numeric + suffix;

        });
    }
}

function CloseTerminals() {
    var doomed = allterms.slice()
    doomed.forEach(function (term) {
        term.destroy();
    });
}
function AllTermsKeypress(e) {
    allterms.forEach(function (term) {
        term.mymaintab.keyPress(e);
    });
}
function AllTermsKeydown(e) {
    allterms.forEach(function (term) {
        term.mymaintab.keyDown(e);
    });
}


function TileTerminals() {
    var toolbar = document.getElementsByClassName('toolbar')[0];
    var currtop = toolbar.getBoundingClientRect().bottom + window.pageYOffset;
    var winwidth = document.body.clientWidth;
    var currleft = 0;
    var biggestheight = 0;
    allterms.forEach(function (term) {
         var el = term.element;
         if (el.clientWidth + currleft > winwidth) {
            currtop = currtop + biggestheight;
            currleft = 0;
        }
        if (el.clientHeight > biggestheight) {
            biggestheight = el.clientHeight;
        }
        el.style.transition = 'left 0.5s, top 0.5s, opacity 0.5s';
        el.style.top = currtop + 'px';
        el.style.left = currleft + 'px';
        //el.style.transition = 'left 0s';
        currleft = currleft + el.clientWidth;
        setTimeout(function() {
            this.style.transition = 'left 0s, top 0s, opacity 0.5s';
        }.bind(el), 0);
    });
}

function TerminalWindow(consoleurl, nodename, x, y, quickaction) {
  var self = this;

  if (!(this instanceof TerminalWindow)) {
    return new TerminalWindow(consoleurl, nodename);
  }
  allterms.push(this);

  EventEmitter.call(this);

  var el
    , grip
    , bar
    , button
    , title;

  el = document.createElement('div');
  el.className = 'termwindow';
  if (arguments.length >= 4) {
	el.style.top = y + 'px';
	el.style.left = x + 'px';
  }

  grip = document.createElement('div');
  grip.className = 'grip';

  bar = document.createElement('div');
  bar.className = 'bar';

  button = document.createElement('div');
  button.innerHTML = 'x';
  button.title = 'close';
  button.className = 'tab';

  title = document.createElement('div');
  title.className = 'title';
  if (quickaction) {
    title.appendChild(quickaction);
  }
  title.appendChild(document.createTextNode(' '  + nodename));

  this.nodename = nodename;
  this.element = el;
  this.grip = grip;
  this.bar = bar;
  this.button = button;
  this.title = title;
  this.consoleurl = consoleurl;

  this.tabs = [];
  this.focused = null;

  this.cols = 80; //Terminal.geometry[0];
  this.rows = 25; //Terminal.geometry[1];
  var defgeometry = localStorage.getItem('termsize');
  if (defgeometry && defgeometry.search('x') >= 0) {
    defgeometry = defgeometry.split('x');
    if (parseInt(defgeometry[0])) { this.cols = parseInt(defgeometry[0]); }
    if (parseInt(defgeometry[1])) { this.rows = parseInt(defgeometry[1]); }
  }



  el.appendChild(grip);
  el.appendChild(bar);
  bar.appendChild(title);
  bar.appendChild(button);
  el.style.opacity = 0;
  document.body.appendChild(el);
  setTimeout(function() { el.style.opacity = 1; }, 1);

  //tty.windows.push(this);

  self.mymaintab = this.createTab();
  this.focus();
  this.bind();

  this.tabs[0].once('open', function() {
    //tty.emit('open window', self);
    self.emit('open');
  });
}

/* Lenovo - End multi-window management code */

inherits(TerminalWindow, EventEmitter);

TerminalWindow.prototype.bind = function() {
  var self = this
    , el = this.element
    , bar = this.bar
    , grip = this.grip
    , button = this.button
    , last = 0;

  on(button, 'click', function(ev) {
    self.destroy();
    return cancel(ev);
  });

  on(grip, 'mousedown', function(ev) {
    self.focus();
    self.resizing(ev);
    return cancel(ev);
  });

  on(el, 'mousedown', function(ev) {
    if (ev.target !== el && ev.target !== bar) return;

    self.focus();

    cancel(ev);

    if (new Date - last < 600) {
      return self.maximize();
    }
    last = new Date;

    self.drag(ev);

    return cancel(ev);
  });
};

TerminalWindow.prototype.focus = function() {
  // Restack
  var parent = this.element.parentNode;
  if (parent) {
    parent.removeChild(this.element);
    parent.appendChild(this.element);
  }

  // Focus Foreground Tab
  this.focused.focus();

  //tty.emit('focus window', this);
  this.emit('focus');
};

function cleanElement() {
    this.parentNode.removeChild(this);
    if (document.getElementsByClassName('terminal').length == 0) {
        currentfont = 'default';
    }
}



TerminalWindow.prototype.destroy = function() {
  if (this.destroyed) return;
  var idx = allterms.indexOf(this);
  if (idx != -1) {
    allterms.splice(idx, 1);
  }
  this.destroyed = true;

  if (this.minimize) this.minimize();

  //splice(tty.windows, this);
  //if (tty.windows.length) tty.windows[0].focus();

  var that = this;
  this.element.style.opacity = 0;
  setTimeout(cleanElement.bind(that.element), 500);

  this.each(function(term) {
    term.destroy();
  });

  //tty.emit('close window', this);
  this.emit('close');
};

TerminalWindow.prototype.drag = function(ev) {
  var self = this
    , el = this.element;

  if (this.minimize) return;

  var drag = {
    left: el.offsetLeft,
    top: el.offsetTop,
    pageX: ev.pageX,
    pageY: ev.pageY
  };

  el.style.opacity = '0.60';
  el.style.cursor = 'move';
  document.documentElement.style.cursor = 'move';

  function move(ev) {
    el.style.left =
      (drag.left + ev.pageX - drag.pageX) + 'px';
    var tmptop = (drag.top + ev.pageY - drag.pageY);
    if (tmptop < 0) {
       tmptop = 0;
    }
    el.style.top = tmptop + 'px';
  }

  function up() {
    el.style.opacity = '';
    el.style.cursor = '';
    document.documentElement.style.cursor = '';

    off(document, 'mousemove', move);
    off(document, 'mouseup', up);

    var ev = {
      left: el.style.left.replace(/\w+/g, ''),
      top: el.style.top.replace(/\w+/g, '')
    };

    //tty.emit('drag window', self, ev);
    self.emit('drag', ev);
  }

  on(document, 'mousemove', move);
  on(document, 'mouseup', up);
};

TerminalWindow.prototype.resizing = function(ev) {
  var self = this
    , el = this.element
    , term = this.focused;

  if (this.minimize) delete this.minimize;

  var resize = {
    w: el.clientWidth,
    h: el.clientHeight
  };

  el.style.overflow = 'hidden';
  el.style.opacity = '0.70';
  el.style.cursor = 'se-resize';
  document.documentElement.style.cursor = 'se-resize';
  term.element.style.height = '100%';

  function move(ev) {
    var x, y;
    y = el.offsetHeight - term.element.clientHeight;
    x = ev.pageX - el.offsetLeft;
    y = (ev.pageY - el.offsetTop) - y;
    el.style.width = x + 'px';
    el.style.height = y + 'px';
  }

  function up() {
    var x, y;

    x = el.clientWidth / resize.w;
    y = el.clientHeight / resize.h;
    x = (x * term.cols) | 0;
    y = (y * term.rows) | 0;

    self.resize(x, y);

    el.style.width = '';
    el.style.height = '';

    el.style.overflow = '';
    el.style.opacity = '';
    el.style.cursor = '';
    document.documentElement.style.cursor = '';
    term.element.style.height = '';

    off(document, 'mousemove', move);
    off(document, 'mouseup', up);
  }

  on(document, 'mousemove', move);
  on(document, 'mouseup', up);
};

TerminalWindow.prototype.maximize = function() {
  if (this.minimize) return this.minimize();

  var self = this
    , el = this.element
    , term = this.focused
    , x
    , y;

  var m = {
    cols: term.cols,
    rows: term.rows,
    left: el.offsetLeft,
    top: el.offsetTop,
    root: root.className
  };

  this.minimize = function() {
    delete this.minimize;
    el.style.opacity = 0;

    el.style.left = m.left + 'px';
    el.style.top = m.top + 'px';
    el.style.width = '';
    el.style.height = '';
    term.element.style.width = '';
    term.element.style.height = '';
    el.style.boxSizing = '';
    self.grip.style.display = '';
    root.className = m.root;

    self.resize(m.cols, m.rows);

    //tty.emit('minimize window', self);
    self.emit('minimize');
  };

  window.scrollTo(0, 0);

  x = root.clientWidth / term.element.offsetWidth;
  y = root.clientHeight / term.element.offsetHeight;
  x = (x * term.cols) | 0;
  y = (y * term.rows) | 0;

  el.style.left = '0px';
  el.style.top = '0px';
  el.style.width = '100%';
  el.style.height = '100%';
  term.element.style.width = '100%';
  term.element.style.height = '100%';
  el.style.boxSizing = 'border-box';
  this.grip.style.display = 'none';
  root.className = 'maximized';

  this.resize(x, y);

  //tty.emit('maximize window', this);
  this.emit('maximize');
};

TerminalWindow.prototype.resize = function(cols, rows) {
  this.cols = cols;
  this.rows = rows;

  this.each(function(term) {
    term.resize(cols, rows);
  });

  //tty.emit('resize window', this, cols, rows);
  this.emit('resize', cols, rows);
};

TerminalWindow.prototype.each = function(func) {
  var i = this.tabs.length;
  while (i--) {
    func(this.tabs[i], i);
  }
};

TerminalWindow.prototype.createTab = function() {
  return new Tab(this, this.consoleurl);
};

TerminalWindow.prototype.highlight = function() {
  var self = this;

  this.element.style.borderColor = 'orange';
  setTimeout(function() {
    self.element.style.borderColor = '';
  }, 200);

  this.focus();
};

TerminalWindow.prototype.focusTab = function(next) {
  var tabs = this.tabs
    , i = indexOf(tabs, this.focused)
    , l = tabs.length;

  if (!next) {
    if (tabs[--i]) return tabs[i].focus();
    if (tabs[--l]) return tabs[l].focus();
  } else {
    if (tabs[++i]) return tabs[i].focus();
    if (tabs[0]) return tabs[0].focus();
  }

  return this.focused && this.focused.focus();
};

TerminalWindow.prototype.nextTab = function() {
  return this.focusTab(true);
};

TerminalWindow.prototype.previousTab = function() {
  return this.focusTab(false);
};

/**
 * Tab
 */

function Tab(win, consoleurl) {
  var self = this;

  var cols = win.cols
    , rows = win.rows;

  Terminal.call(this, {
    cols: cols,
    rows: rows
  });

  this.id = '';
  this.consoleurl = consoleurl;
  this.clientcount = 0;
  this.connectstate = 'unconnected';
  this.lasterror = ''
  this.window = win;
  this.element = null;
  this.process = '';
  this.open();
  if (currentfont == 'default') {
        if (localStorage.getItem('termfontfactor')) {
            var factor = localStorage.getItem('termfontfactor')
            factor = parseFloat(factor) / 100;
            this.element.style.fontSize = factor + 'pc';
        } else {
            this.element.style.fontSize = '1pc';
        }
  } else {
    this.element.style.fontSize = currentfont;
  }
  this.hookKeys();
  this.sessid = '';
  this.datapending = false;
  this.waitingdata = false;
  this.sentdata = function(data, textStatus, jqXHR) {
    if (this.waitingdata) {
      postRequest(consoleurl,  { session: this.sessid, bytes: this.waitingdata }, this.sentdata);
      this.waitingdata = false;
    } else {
        this.datapending = false;
    }
  }.bind(this);
  this.on('data', function(data) {
    // Send data to console from terminal
    if (this.datapending) {
      if (!this.waitingdata) {
        this.waitingdata = data;
      } else {
        this.waitingdata = this.waitingdata + data;
      }
      return;
    }
    this.datapending = true;
    postRequest(consoleurl,  { session: this.sessid, bytes: data }, this.sentdata);
  }.bind(this));
  this.gotdata = function(data, textStatus, jqXHR) {
    if (this.destroyed) {
        return;
    }
    if ("data" in data) {
       this.write(data.data);
    }
    var updatetitle = false;
    var updateinfo = [];
    if ("connectstate" in data) {
        updatetitle = true;
        this.connectstate = data.connectstate;
    }
    if (this.connectstate == "closed") {
        self.destroy();
    } else if (this.connectstate != "connected") {
        updateinfo.push(this.connectstate);
    } else {
        self.lasterror = '';
    }
    if ("error" in data) {
        updatetitle = true;
        this.lasterror = data.error
    }
    if (this.lasterror != '') {
        updateinfo.push(this.lasterror);
    }
    if ("clientcount" in data) {
        updatetitle = true;
        this.clientcount = data.clientcount;
    }
    if (this.clientcount > 1) {
        updateinfo.push("clients: " + this.clientcount.toString());
    }
    if (updatetitle == true) {
        if (updateinfo.length > 0) {
            getTextNode(this.window.title).nodeValue = " " + this.window.nodename + " [" + updateinfo.join() + "]";
        } else {
            getTextNode(this.window.title).nodeValue = " " + this.window.nodename;
        }
    }
    //postRequest(consoleurl,  { session: this.sessid }, this.gotdata);
  }.bind(this);
  this.gotsession = function(data, textStatus, jqXHR) {
    this.sessid = data.session
    //postRequest(consoleurl,  { session: this.sessid }, this.gotdata, function() {}, true);
  }.bind(this);
  postRequest(consoleurl,  false, this.gotsession, function() {}, this.gotdata);

  win.tabs.push(this);
};

inherits(Tab, Terminal);

Tab.prototype._write = Tab.prototype.write;

Tab.prototype.write = function(data) {
  return this._write(data);
};

Tab.prototype._focus = Tab.prototype.focus;

Tab.prototype.focus = function() {
  if (Terminal.focus === this) return;

  var win = this.window;

  // maybe move to Tab.prototype.switch
  if (win.focused !== this) {
    if (win.focused) {
      if (win.focused.element.parentNode) {
        win.focused.element.parentNode.removeChild(win.focused.element);
      }
    }

    win.element.appendChild(this.element);
    win.focused = this;

    //win.title.innerHTML = this.process;
  }

  this._focus();

  win.focus();

  this.emit('focus');
};

Tab.prototype._resize = Tab.prototype.resize;

Tab.prototype.resize = function(cols, rows) {
  //this.socket.emit('resize', this.id, cols, rows);
  this._resize(cols, rows);
  this.emit('resize', cols, rows);
};

Tab.prototype.__destroy = Tab.prototype.destroy;

Tab.prototype._destroy = function() {
  if (this.destroyed) return;
  this.destroyed = true;

  var win = this.window;

  if (this.element.parentNode) {
    this.element.parentNode.removeChild(this.element);
  }

  splice(win.tabs, this);

  if (win.focused === this) {
    win.previousTab();
  }

  if (!win.tabs.length) {
    win.destroy();
  }

  this.__destroy();
};

Tab.prototype.destroy = function() {
  if (this.destroyed) return;
  postRequest(this.consoleurl,  {session: this.sessid, closesession: true }, this.sentdata);
  this._destroy();
  this.emit('close');
};

Tab.prototype.hookKeys = function() {
  var self = this;

  // Alt-[jk] to quickly swap between windows.
  this.on('key', function(key, ev) {
    if (Terminal.focusKeys === false) {
      return;
    }

    var offset
      , i;

    if (key === '\x1bj') {
      offset = -1;
    } else if (key === '\x1bk') {
      offset = +1;
    } else {
      return;
    }

    i = indexOf(tty.windows, this.window) + offset;

    this._ignoreNext();

    if (tty.windows[i]) return tty.windows[i].highlight();

    if (offset > 0) {
      if (tty.windows[0]) return tty.windows[0].highlight();
    } else {
      i = tty.windows.length - 1;
      if (tty.windows[i]) return tty.windows[i].highlight();
    }

    return this.window.highlight();
  });

  this.on('request paste', function(key) {
    this.socket.emit('request paste', function(err, text) {
      if (err) return;
      self.send(text);
    });
  });

  this.on('request create', function() {
    this.window.createTab();
  });

  this.on('request term', function(key) {
    if (this.window.tabs[key]) {
      this.window.tabs[key].focus();
    }
  });

  this.on('request term next', function(key) {
    this.window.nextTab();
  });

  this.on('request term previous', function(key) {
    this.window.previousTab();
  });
};

Tab.prototype._ignoreNext = function() {
  // Don't send the next key.
  var handler = this.handler;
  this.handler = function() {
    this.handler = handler;
  };
  var showCursor = this.showCursor;
  this.showCursor = function() {
    this.showCursor = showCursor;
  };
};

/**
 * Program-specific Features
 */

Tab.prototype._bindMouse = Tab.prototype.bindMouse;

Tab.prototype.bindMouse = function() {
  if (!Terminal.programFeatures) return this._bindMouse();

  var self = this;

  var wheelEvent = 'onmousewheel' in window
    ? 'mousewheel'
    : 'DOMMouseScroll';

  on(self.element, wheelEvent, function(ev) {
    if (self.mouseEvents) return;

    if ((ev.type === 'mousewheel' && ev.wheelDeltaY > 0)
        || (ev.type === 'DOMMouseScroll' && ev.detail < 0)) {
      // page up
      self.keyDown({keyCode: 33});
    } else {
      // page down
      self.keyDown({keyCode: 34});
    }

    return cancel(ev);
  });

  return this._bindMouse();
};

/**
 * Helpers
 */

function indexOf(obj, el) {
  var i = obj.length;
  while (i--) {
    if (obj[i] === el) return i;
  }
  return -1;
}

function splice(obj, el) {
  var i = indexOf(obj, el);
  if (~i) obj.splice(i, 1);
}

function sanitize(text) {
  if (!text) return '';
  return (text + '').replace(/[&<>]/g, '')
}

/* Lenovo: make functions available to required scope */
this.TerminalWindow = TerminalWindow;
this.TileTerminals = TileTerminals;
this.CloseTerminals = CloseTerminals;
this.ScaleTerminals = ScaleTerminals;
this.AllTermsKeydown = AllTermsKeydown;
this.AllTermsKeypress = AllTermsKeypress;

}).call(function() {
    return this;
}());
