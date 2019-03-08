# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import yaml
import os
import logging

logger = logging.getLogger(__name__)


class ConfUtil(object):
    @staticmethod
    def parse_paste_conf():
        from paste.deploy import appconfig
        conf_path = '/etc/antilles/antilles.ini'
        return appconfig('config:{0}'.format(conf_path))

    @staticmethod
    def get_jobgen_script(jobtype):
        conf_file = '/etc/antilles/job_cmd_conf.yaml'
        currpath = os.path.abspath(os.path.dirname(__file__))
        try:
            with open(conf_file) as f:
                conf_jobtype = yaml.load(f)

            if jobtype not in conf_jobtype:
                logger.warn('unsupport jobtype: %s', jobtype)
                return None

            return os.path.join(currpath, '../..', conf_jobtype[jobtype])
        except Exception:
            logger.exception('raise exception')
            return None
