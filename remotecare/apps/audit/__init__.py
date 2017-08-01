# -*- coding: utf-8 -*-
"""
Contains a model for storing auditing information.

The audit information, which include the datetime,
edited by user and a json containing the  actually changes made
is automatically stored when a model is saved. For this
purpose the logged in user is automatically passed from the view to the form
and eventually to the instance that is saved.

By using the baseclass :class:`core.models.AuditBaseModel` models can
be automatically set to store audit trails.
"""
