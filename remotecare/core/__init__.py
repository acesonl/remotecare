# -*- coding: utf-8 -*-
"""
The core package provides core functionality which is (mostly) not Remote care
specific:

    - Encryption: provides encryption wrappers based on the Crypto package
    - Unittest: defines a baseclass with handy functions for all unitests
    - Templatetags: custom template tags

    - Serializers: contains a custom JSON serializer
    - Backends: e-mail authorization backend
    - Forms: default form classes and widgets
    - Widgets: default widgets
    - Views: default views for auditing purposes
    - run_csslint: include this runner if you want to run csslint
    - context_processors: default context processor for datetime format
    - models: base models and modelfields
"""
