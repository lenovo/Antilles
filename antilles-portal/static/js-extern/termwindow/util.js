/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

function addMenuItem(menu, label, callback, icon, keepopen) {
  var menuitem = document.createElement('li');
  function deactive(e) {
    // This will trigger dehover if applicable
    menu.style.pointerEvents = 'none';
    setTimeout(function() {
        menu.style.pointerEvents = '';
    }, 1);
    this(e);
  }
  if (keepopen) {
      menuitem.addEventListener('click', callback);
  } else {
      menuitem.addEventListener('click', deactive.bind(callback));
  }
  var i = document.createElement('span');
  i.style.width = "1.3em";
  i.style.textAlign = "center";
  if (icon) {
    i.classList.add('fa', 'fa-' + icon);
  } else {
    i.classList.add('fa');
  }
  menuitem.appendChild(i);
  menuitem.appendChild(document.createTextNode(' ' + l(label)));
  menu.appendChild(menuitem);
  return menuitem;
}

function clickOpen(e) {
    if (!this.classList.contains('clicked')) {
        this.classList.add('clicked');
        var mc = this;
        function unClick(e) {
            document.removeEventListener('click', unClick);
            mc.classList.remove('clicked');
        }
        setTimeout(function() {
            document.addEventListener('click', unClick);
        }, 1);
    }
}

function closeDialog() {
    var dlg;
    var bg;
    var callback;
    dlg = this[0];
    bg = this[1];
    callback = this[2];
    dlg.parentElement.removeChild(dlg);
    bg.parentElement.removeChild(bg);
    if (callback) {
        callback();
    }
}
function maketoollabel(text) {
    var mylabel = document.createElement('span');
    mylabel.textContent = text;
    mylabel.classList.add('tool');
    return mylabel;
}
function confirmAction(question, callback, cancelcall) {
    var confirmd = document.createElement('div');
    confirmd.style.textAlign = 'left';
    confirmd.style.maxWidth = '500px';
    confirmd.classList.add('modaldialog');
    var tspan = document.createElement('span');
    tspan.textContent = question;
    confirmd.appendChild(tspan);
    var hr = document.createElement('hr');
    hr.style.marginBottom = '0';
    confirmd.appendChild(hr);
    var ysbtn = document.createElement('button');
    ysbtn.appendChild(document.createTextNode(l('Yes')));
    var nobtn = document.createElement('button');
    nobtn.appendChild(document.createTextNode(l('No')));
    var bg = document.createElement('div');
    bg.classList.add('modalbg');
    document.body.appendChild(bg);
    if (cancelcall === null) {
        cancelcall = function() {};
    }
    nobtn.addEventListener('click', closeDialog.bind([confirmd, bg, cancelcall]));
    ysbtn.addEventListener('click', closeDialog.bind([confirmd, bg, callback]));
    var buttonarea = document.createElement('div');
    confirmd.appendChild(buttonarea);
    buttonarea.style.textAlign = 'right';
    buttonarea.appendChild(ysbtn);
    buttonarea.appendChild(nobtn);
    bg.appendChild(confirmd);
}
function addNavMenu(bar, label, icon) {
    return addMenu(bar, label, icon, 'navcolor');
}
function addToolMenu(bar, label, icon) {
    return addMenu(bar, label, icon, 'toolcolor');
}
function addMenu(bar, label, icon, menuclass, menucolor) {
    var menu = document.createElement('li');
    menu.classList.add('dropdown', 'navitem');
    menu.classList.add(menuclass);
    var header = document.createElement('span');
    menu.appendChild(header);
    var i = document.createElement('span');
    if (icon) {
        i.classList.add('fa', 'fa-' + icon);
    } else {
        i.classList.add('fa');
    }
    i.style.width = "1.3em";
    i.style.textAlign = "center";
    header.appendChild(i);
    header.labeltext = document.createTextNode(' ' + l(label) + ' ');
    header.appendChild(header.labeltext);
    var arrow = document.createElement('span');
    arrow.classList.add('fa', 'fa-caret-down');
    header.appendChild(arrow);
    var menucontent = document.createElement('ul');
    menucontent.classList.add('navitem', menuclass);
    menucontent.header = header;
    menu.appendChild(menucontent);
    bar.appendChild(menu);
    header.addEventListener('click', clickOpen.bind(menu));
    return menucontent;
}

var asyncRequests = {};
var asyncSessid = false;

function getRequest(url, success, failure, username, password, sync) {
  var request = new XMLHttpRequest();
  request.open('GET', url, true);
  request.setRequestHeader('Accept', 'application/json');
  request.setRequestHeader('SuppressAuthHeader', 'true');
  // Below would be interesting if wanting to skip browser use of
  // storing basic http auth....
  if (username) {
      request.setRequestHeader("Authorization", "Basic " + btoa(username + ":" + password));
  }
  if (!sync && asyncSessid) {
        request.setRequestHeader('ConfluentAsyncId', asyncSessid);
        requestid = hookRequestId(success, failure);
        request.setRequestHeader('ConfluentRequestId', requestid);
        request.onload = function() {
            if (this.status == 401) {
                show_auth();
            } else if (this.status != 201 && failure) {
                failure(this.status);
            }
        }
  } else {
      request.onload = function() {
        if (this.status >= 200 && this.status <= 400) {
            success(JSON.parse(this.responseText));
        } else if (this.status == 401) {
            show_auth();
        } else {
            failure(this.status);
    }
      };
  }
  request.send();
}

function hookRequestId(success, failure) {
   var rid = 0;
   while (asyncRequests.hasOwnProperty(rid)) {
       rid += 1;
   }
   asyncRequests[rid] = {success: success, failure: failure};
   return rid;
}
function stopAsync() {
    asyncSsesid = undefined;
    asyncServiceEnd = true;
}
function gotAsync(response) {
    asyncSessid = response.asyncid;
    this();
    postRequest('/api/sessions/current/async/', {asyncid: asyncSessid}, nextAsync, failAsync);
}
function nextAsync(response) {
    if (response.hasOwnProperty('asyncresponse')) {
        response.asyncresponse.forEach(function(val) {
            try {
            asyncRequests[val.requestid].success(val.response);
            }
            catch (e)
            {
                console.log(e);
                console.log(e.stack);
            }
//   asyncRequests[rid] = {success: success, failure: failure};
        });
    }
    if(asyncServiceEnd) {
      return;
    }
    postRequest('/api/sessions/current/async/', {asyncid: asyncSessid}, nextAsync, failAsync);
}
function failAsync(response) {
  console.log("failAsync");
}

function startAsync(callback) {
    asyncServiceEnd = false;
    postRequest('/api/sessions/current/async/', false, gotAsync.bind(callback), failAsync.bind(callback));
}

function postRequest(url, data, success, failure, async) {
    var request = new XMLHttpRequest();
    request.open('POST', url, true);
    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('Accept', 'application/json');
    request.setRequestHeader('SuppressAuthHeader', 'true');
    // Add auth feature for web console. Add by wengmh1 2018/4/28
    var token = window.gApp.$store.state.auth.token;
    if(token && token.length > 0) {
      request.setRequestHeader('authorization', 'Jwt ' + token);
    }
    if (async) {
        request.setRequestHeader('ConfluentAsyncId', asyncSessid);
        requestid = hookRequestId(async, failure);
        request.setRequestHeader('ConfluentRequestId', requestid);

        request.onload = function() {
            if (this.status >= 200 && this.status < 400) {
                success(JSON.parse(this.responseText));
            } else if (this.status == 401) {
                show_auth();
            } else if (failure) {
                failure(this.status);
            }
        }
    } else {
        request.onload = function() {
            if (this.status >= 200 && this.status < 400) {
                success(JSON.parse(this.responseText));
            } else if (this.status == 401) {
               show_auth();
            } else if (failure) {
                failure(this.status);
            }
        };
    }
    if (data) {
        request.send(JSON.stringify(data));
    } else {
        request.send("");
    }
    request = null;
}

window.onscroll = function() {
    [].forEach.call(document.getElementsByClassName('header'), function (e) { e.style.left = document.body.scrollLeft + 'px'; e.style.position = "relative"; });
}
