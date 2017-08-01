"""
Since all users use the same :class:`apps.account.models.User` model,
this module provides a baseclass for adding new users.

:subtitle:`Function definitions:`
"""
from core.views import FormView
from core.encryption.random import randompassword
from django.contrib.sites.requests import RequestSite
from apps.account.models import EncryptionKey


class BaseAddView(FormView):
    """
    Baseclass for adding user, used for adding users
    of all 3 different role types. (managers cannot be added)
    """
    def get_user_for_form(self, form):
        """
        Args:
            - form: The modelform with model=User
        Returns:
            Saved user with some default values set.
        """
        user = form.save(commit=False)
        if not user.hospital:
            user.hospital = self.request.user.hospital

        key = EncryptionKey(key=randompassword())
        key.save()
        user.personal_encryption_key = key
        user.set_unusable_password()
        user.encrypted = False
        user.save()

        return user

    @property
    def url_prefix(self):
        """
        Returns:
            The url prefix to be included in the e-mail
        """
        # Sent password set e-mail
        rq = RequestSite(self.request)
        url_prefix = 'http'
        if self.request.is_secure():  # pragma: no cover
            url_prefix += 's'
        url_prefix += '://' + rq.domain
        return url_prefix
