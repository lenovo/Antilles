# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import falcon


class ReachDailyLimit(falcon.HTTPError):
    title = 'Reach Daily Limit'

    def __init__(self, description):
        super(ReachDailyLimit, self).__init__(
            falcon.HTTP_BAD_REQUEST,
            description=description
        )
