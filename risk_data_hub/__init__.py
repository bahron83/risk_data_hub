# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2018 European Commission
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
'''from django.utils.translation import ugettext_noop as _
from geonode.notifications_helper import NotificationsAppConfigBase


class RisksAppConfig(NotificationsAppConfigBase):
    name = 'risk_data_hub'
    NOTIFICATIONS = (("data_uploaded", _("Data uploaded"), _("Finished uploading data from Excel"),),                     
                     )

    def ready(self):
        super(RisksAppConfig, self).ready()


default_app_config = 'risk_data_hub.RisksAppConfig'
'''

from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ['celery_app']
