/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Admin from './admin'
import Operator from './operator'
import Staff from './staff'

function formatMenu(menu) {
  for(var i=0; i<menu.length; i++) {
    fillMenuProperties(menu[i]);
  }
  return menu;
}

function fillMenuProperties(menu) {
  if(menu.children) {
    for(var i=0; i<menu.children.length; i++) {
      fillMenuProperties(menu.children[i]);
    }
  } else {
    menu.children = [];
  }
}

export default {
  admin: formatMenu(Admin),
  operator: formatMenu(Operator),
  staff: formatMenu(Staff)
}
