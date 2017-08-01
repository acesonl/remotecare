from django.core.urlresolvers import reverse


class lazy_reverse:
    def __init__(self, url, app_name, model_name):
        self.url = url
        self.app_name = app_name
        self.model_name = model_name

    def __unicode__(self):
        return reverse(self.url, args=[self.app_name, self.model_name, ])
