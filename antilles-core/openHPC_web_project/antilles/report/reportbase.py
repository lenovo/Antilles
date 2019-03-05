# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import datetime
import logging
import os
import uuid
from abc import ABCMeta, abstractmethod

from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext as _
from pytz import FixedOffset  # , utc
from six import add_metaclass
from weasyprint import HTML
from xlwt import Workbook, easyxf as ezxf

from .etc import DOWNLOAD_PATH

logger = logging.getLogger(__name__)


def _counter(start=0, step=1):
    count = start
    while True:
        val = yield count
        count += step if val is None else val


class TZinfoClass(object):

    def __init__(self, seconds=0):
        self.seconds = seconds

    def set(self, day=None, hour=None, minute=None, seconds=None):
        if day and isinstance(day, int):
            self.seconds = -day * 86400
        if minute and isinstance(minute, int):
            self.seconds = -minute * 60
        if hour and isinstance(hour, int):
            self.seconds = -hour * 3600
        if seconds and isinstance(seconds, int):
            self.seconds = -seconds

    @property
    def get_seconds(self):
        return self.seconds

    @property
    def get_FixedOffset(self):
        return FixedOffset(self.seconds / 60)

    @property
    def get_datetime(self):
        return datetime.timedelta(seconds=self.seconds)


@add_metaclass(ABCMeta)
class ReportBase(object):
    export_path = DOWNLOAD_PATH
    encoding = 'utf-8'

    def __init__(self, headline, data, title, doctype, start_time, end_time,
                 creator, create_time, template, subtitle, page_direction,
                 fixed_offset, time_range_flag):
        self.headline = self.translate(headline)
        self.data = data
        self.title = _(title)
        self.doctype = doctype
        self.fixed_offset = fixed_offset
        self.export_time = datetime.datetime.now(
            tz=self.fixed_offset).strftime("%F %T")
        self.report_export = getattr(self, 'export_' + doctype)
        self.export_filename = str(uuid.uuid1())
        self.start_time = start_time
        self.end_time = end_time
        self.creator = creator
        self.create_time = create_time
        self.template = template
        self.subtitle = _(subtitle)
        self.page_direction = page_direction
        self.time_range_flag = time_range_flag

        if self.time_range_flag:
            self.create_info = ' '.join([
                self.creator,
                _(u'created at'),
                self.create_time.strftime('%F %T')
            ])
        else:
            self.create_info = self.creator + ' ' + _(u'created at') + ' ' + \
                self.create_time.strftime('%F %T') + '\n' + \
                _(u'data cycle') + ':' + self.start_time.strftime('%F %T') + \
                ' - ' + self.end_time.strftime('%F %T')

    '''
    :param type is list[str] or str such as ["a",["b"]] or "b"
    :function  translate
    '''

    def translate(self, param):
        if isinstance(param, str):
            return _(param)
        if isinstance(param, list):
            ret = []
            for item in param:
                if isinstance(item, str):
                    ret.append(_(item))
                elif isinstance(item, list):
                    ret.append(self.translate(item))
            else:
                return ret
        return None

    @abstractmethod
    def export_html(self):
        pass

    @abstractmethod
    def export_pdf(self):
        pass

    @abstractmethod
    def export_xls(self):
        pass


class ReportExporter(ReportBase):

    def _generate_html(self):
        return render_to_string(
            self.template,
            context={
                'title': self.title,
                'subtitle': self.subtitle,
                'headline': self.headline,
                'data': enumerate(self.data, 1),
                'start_time': self.start_time.strftime('%F %T'),
                'end_time': self.end_time.strftime('%F %T'),
                'creator': self.creator,
                'create_time': self.create_time.strftime('%F %T'),
                'page_direction': self.page_direction
            }
        )

    def export_html(self):
        filename = self.export_filename + '.html'
        html = self._generate_html().encode(self.encoding)
        with open(os.path.join(self.export_path, filename), 'w') as f:
            f.write(html)

        return filename

    def export_pdf(self):
        html = HTML(string=self._generate_html())
        filename = self.export_filename + '.pdf'
        html.write_pdf(
            os.path.join(self.export_path, filename)
        )

        return filename

    def export_xls(self):
        book = Workbook(encoding=self.encoding)
        sheet = book.add_sheet(self.title)
        counter = _counter()

        # write title
        sheet.write_merge(
            next(counter), counter.send(0),
            0, len(self.headline) - 1,
            self.title,
            ezxf(
                'font: bold on, height 500;'
                ' align:wrap on, vert centre, horiz center;'
            )
        )

        # write info
        sheet.write_merge(
            next(counter), counter.send(1),
            0, len(self.headline) - 1, self.create_info,
            ezxf(
                'font: bold on, height 200;'
                ' align:wrap on, vert centre, horiz right;'
            )
        )

        # write table head
        style = ezxf(
            'font: bold on; align:wrap on, vert centre, horiz center'
        )
        next(counter)
        for colx, value in enumerate(self.headline):
            sheet.write(
                counter.send(0), colx, value, style
            )

        # set frozen
        sheet.set_panes_frozen(True)  # frozenheadings instead of split panes
        # ingeneral, freeze after last heading row
        sheet.set_horz_split_pos(counter.send(0) + 1)
        # if userdoes unfreeze, don't leave a split there
        sheet.set_remove_splits(True)

        # write table data
        for row in self.data:
            next(counter)
            for colx, value in enumerate(row):
                if (
                    isinstance(value, datetime.datetime) or
                    isinstance(value, datetime.date) or
                    isinstance(value, datetime.time)
                ):
                    value = (timezone.localtime(value)).strftime("%F %T")
                sheet.write(counter.send(0), colx, value)

        filename = self.export_filename + '.xls'
        book.save(
            os.path.join(self.export_path, filename)
        )
        return filename


class GroupReportExporter(ReportBase):

    def _generate_html(self):
        template = self.template
        if template == 'report/node_running_statistics.html' and \
                self.doctype == 'pdf':
            template = 'report/node_running_statistics_pdf.html'
        return render_to_string(
            template,
            context={
                'title': self.title,
                'subtitle': self.subtitle,
                'headline': self.headline,
                'data': (
                    (group_title_data, enumerate(group_data, 1))
                    for (group_title_data, group_data) in self.data
                ),
                'start_time': self.start_time.strftime('%F %T'),
                'end_time': self.end_time.strftime('%F %T'),
                'creator': self.creator,
                'create_time': self.create_time.strftime('%F %T'),
                'page_direction': self.page_direction
            }
        )

    def export_html(self):
        filename = self.export_filename + '.html'
        html = self._generate_html().encode(self.encoding)
        with open(os.path.join(self.export_path, filename), 'w') as f:
            f.write(html)

        return filename

    def export_pdf(self):
        html = HTML(string=self._generate_html())
        filename = self.export_filename + '.pdf'
        html.write_pdf(
            os.path.join(self.export_path, filename)
        )
        return filename

    def export_xls(self):
        group_title, group_headline = self.headline
        book = Workbook(encoding=self.encoding)
        sheet = book.add_sheet(self.title)
        counter = _counter()

        # write title
        sheet.write_merge(
            next(counter), counter.send(0),
            0, len(group_headline) - 1,
            self.title,
            ezxf(
                'font: bold on, height 500;'
                ' align:wrap on, vert centre, horiz center;'
            )
        )

        # write info
        sheet.write_merge(
            next(counter), counter.send(1),
            0, len(group_headline) - 1, self.create_info,
            ezxf(
                'font: bold on, height 200;'
                'align:wrap on, vert centre, horiz right;'
            )
        )

        # write group
        style = ezxf(
            'font: bold on; align:wrap on, vert centre, horiz center'
        )
        for group_title_data, group_data in self.data:
            # write group head
            sheet.write_merge(
                next(counter), counter.send(0),
                0, len(group_headline),
                '{}: {}'.format(group_title.encode(
                    self.encoding), group_title_data),
                style
            )
            next(counter)
            for colx, value in enumerate(group_headline):
                sheet.write(
                    counter.send(0), colx, value, style
                )

            # write group data
            for row in group_data:
                next(counter)
                for colx, value in enumerate(row):
                    if (
                        isinstance(value, datetime.datetime) or
                        isinstance(value, datetime.date) or
                        isinstance(value, datetime.time)
                    ):
                        value = (timezone.localtime(value)).strftime("%F %T")
                    sheet.write(counter.send(0), colx, value)

            # split one line
            next(counter)

        filename = self.export_filename + '.xls'
        book.save(
            os.path.join(self.export_path, filename)
        )
        return filename
