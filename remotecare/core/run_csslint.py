# -*- coding: utf-8; mode: django -*-
"""
Customized Reporter class which includes all static files dirs
in the apps_locations argument for CSS lint

:subtitle:`Class definitions:`
"""
from django.conf import settings
from django_jenkins.tasks.run_csslint import Reporter as BaseReporter


class Reporter(BaseReporter):
    """
    Subclass the Reporter class of run_csslint in jenkins.
    Adds the locations of the staticfiles.
    """
    def run(self, apps_locations, **options):
        for location in settings.STATICFILES_DIRS:
            if location not in (None, ''):
                apps_locations.append(location)
        super(Reporter, self).run(apps_locations, **options)
