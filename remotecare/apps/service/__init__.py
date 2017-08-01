# -*- coding: utf-8 -*-
"""
The service package contains functions which should be run daily
via a deamon around 9:00. (since sms and e-mail notifications are sent
to Remote Care users)

The service functions automatically sent e-mail and/or sms notifications
for due controls to patients or due handling of filled in controls to
healthprofessionals. Patient that are set for deleting are automatically
deleted after two weeks.
"""
