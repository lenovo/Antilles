# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.utils.translation import ugettext as _

def getcurrentuserinfo(user):
    workspace = ""
    billgroup = ""
    try:
        workspace = user.workspace
        if workspace[-1] == '/' or workspace[-1] == "\\":
            workspace = workspace[0:-1]
        billgroup = user.bill_group.name
    except Exception:
        logger.exception(_("Error occured when creating bill group"))
    return workspace, billgroup
