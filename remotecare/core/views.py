# -*- coding: utf-8 -*-
"""
Module containing a baseclass for all formviews and a
function for serving files via the X-Sendfile directive.

:subtitle:`Class and function definitions:`
"""

import os
import posixpath

from django.conf import settings
from django.views.static import serve, directory_index
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.utils.six.moves.urllib.parse import unquote
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView as DefaultFormView


USE_XSENDFILE = getattr(settings, 'USE_XSENDFILE', False)
XSENDFILE_HEADER = getattr(settings, 'XSENDFILE_HEADER',
                           'X-Accel-Redirect')
XSENDFILE_LOCATION = getattr(settings, 'XSENDFILE_LOCATION', 'xsendmedia')


class FormView(DefaultFormView):
    """
    Baseclass formview which automatically adds a 'changed_by_user'
    property to the form instance which is the logged in user.

    Used for getting the logged in user from the view to model instance
    via a form.
    """
    def get_form_kwargs(self):
        """
        Automatically add the changed_by_user
        to the form kwargs. This is picked up in the baseclass form
        and set on the form itselves and later in the save method of the
        form to the model.

        This way the self.request.user is pushed via a form to the model
        to be used in the audit trail.
        """
        kwargs = super(FormView, self).get_form_kwargs()
        kwargs.update({'changed_by_user': self.request.user})
        return kwargs


@login_required
def xsendfileserve(request, path, document_root=None, show_indexes=False):
    """
    Serve static files below a given point in the directory structure.

    Uses X-Sendfile to sent the file to the client via the webserver,
    allowing authentication for media files.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', 'apps.core.views.xsendfileserve',
        {'document_root' : '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index.html``.

    Nginx default setup (include in sites-available config file(s))::

        location /xsendmedia {
            internal;
            alias /full/path/to/remotecare/media;
        }

    """
    if USE_XSENDFILE:
        path = posixpath.normpath(unquote(path))
        path = path.lstrip('/')
        newpath = ''
        for part in path.split('/'):
            if not part:
                # Strip empty path components.
                continue
            drive, part = os.path.splitdrive(part)
            head, part = os.path.split(part)
            if part in (os.curdir, os.pardir):
                # Strip '.' and '..' in path.
                continue
            newpath = os.path.join(newpath, part).replace('\\', '/')
        if newpath and path != newpath:
            return HttpResponseRedirect(newpath)
        fullpath = os.path.join(document_root, newpath)

        if os.path.isdir(fullpath):
            if show_indexes:
                return directory_index(newpath, fullpath)
            raise Http404(_("Directory indexes are not allowed here."))
        if not os.path.exists(fullpath):
            raise Http404(_('"%(path)s" does not exist') % {'path': fullpath})
        # Until here everything is copied from the django.views.static.serve

        # Set the X-Sendfile header, which the webserver should
        # pickup
        response = HttpResponse()
        response[XSENDFILE_HEADER] = '/{0}/{1}'.format(XSENDFILE_LOCATION,
                                                       path)
        # Unset the Content-Type as to allow for the webserver
        # to determine it.
        response['Content-Type'] = ''
        return response

    # Use the default function
    return serve(request, path, document_root, show_indexes)
