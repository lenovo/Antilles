# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.db.migrations.operations.base import Operation


class CreatePreferenceData(Operation):
    reversible = True

    def __init__(self, name, value):
        from datetime import datetime
        self.name = name
        self.value = value
        self.create_time = datetime.now()
        self.modify_time = self.create_time

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute("INSERT INTO user_preference (NAME,VALUE,CREATE_TIME,MODIFY_TIME) VALUES"
                              " ('{0}','{1}','{2}','{3}');".format(self.name, self.value, self.create_time,
                                                                   self.modify_time))

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute('DROP TABLE user_preference;')

    def describe(self):
        return "Creates  a Preference data: name is {}, value is {}.".format(self.name, self.value)
