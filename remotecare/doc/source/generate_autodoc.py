#!/usr/bin/env python
# -*- coding:Utf-8 -*-
import os
import sys
import django
from django.core.management import call_command

HERE = os.path.realpath(os.path.dirname(__file__) + '../../')
sys.path.insert(0, os.path.abspath('../../'))
# setup Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'remotecare.settings'
django.setup()


try:
    # Get the list of applications from the settings
    from django.conf import settings
except ImportError:
    raise ImportError("The script should be run from the project root")


class Modules(object):
    """
    auto generate template directory structure
    """

    def __init__(self):
        self.internal_apps = {}
        self.fname = settings.DS_FILENAME

    def create_dir(self, directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

    def write_file(self, path_and_file_name, lines):
        f = open(path_and_file_name, 'w')
        f.writelines(lines)
        f.close()

    def write(self):
        """Write the created list in the new file"""
        app_lines = ['Remote Care\'s documentation']
        app_lines.append('=' * len(app_lines[0]))
        app_lines.append('')
        app_lines.append('Contents:')
        app_lines.append('')
        app_lines.append('.. toctree::')
        app_lines.append('   :maxdepth: 1')
        app_lines.append('')

        for internal_app in sorted(self.internal_apps):
            app_lines.append('   ' + internal_app + '/index.rst')

            if '.' in internal_app:
                internal_app_dir = '/'.join(internal_app.split('.'))
            else:
                internal_app_dir = internal_app
            self.create_dir(settings.DS_ROOT + '/' + internal_app_dir)
            module_lines = []

            module_lines.append(internal_app)
            module_lines.append('=' * len(internal_app))
            module_lines.append('.. automodule:: ' + internal_app)
            module_lines.append('')
            module_lines.append('Contents:')
            module_lines.append('')
            module_lines.append('.. toctree::')
            module_lines.append('   :maxdepth: 2')
            module_lines.append('')

            for module in sorted(self.internal_apps[internal_app]):
                module_lines.append('   ' + module + '.rst')
                self.write_file(
                    settings.DS_ROOT + '/' +
                    internal_app_dir + '/' + module + '.rst',
                    self.internal_apps[internal_app][module])
            self.write_file(
                settings.DS_ROOT + '/' +
                internal_app_dir + '/index.rst',
                self.add_lf(module_lines))

        app_lines.append('')
        app_lines.append('Indices and tables')
        app_lines.append('==================')
        app_lines.append('')
        app_lines.append('* :ref:`genindex`')
        app_lines.append('* :ref:`modindex`')
        app_lines.append('* :ref:`search`')

        self.write_file(settings.DS_ROOT + '/index.rst',
                        self.add_lf(app_lines))

    def process_app_dict(self, app_dict, path):
        """recursively process the app_dict"""

        index_rst = []
        if path == '':
            index_rst.append('Remote Care\'s documentation')
            index_rst.append('=' * len(index_rst[0]))
            index_rst.append('')
            index_rst.append('.. toctree::')
            index_rst.append('')
            index_rst.append('   main.rst')
            index_rst.append('   install.rst')
            index_rst.append('')
        else:

            app = path.split('/')[-2]
            index_rst.append(app)
            index_rst.append('=' * len(app))
            index_rst.append('.. automodule:: ' + path.replace('/', '.')[:-1])
            index_rst.append('')

        self.create_dir(settings.DS_ROOT + '/' + path)

        if app_dict != {}:
            index_rst.append(':subtitle:`Packages:`')
            index_rst.append('')
            index_rst.append('.. toctree::')
            index_rst.append('   :maxdepth: 2')
            index_rst.append('')
            for app in app_dict:
                if path:
                    app_name = path.replace('/', '.') + app
                else:
                    app_name = app

                index_rst.append('   ' + app + '/index.rst')

                self.process_app_dict(app_dict[app], path + app + '/')

        app_name = path.replace('/', '.')
        if app_name != '':
            app_instance = App(app_name)
            if len(app_instance.modules) > 0:
                index_rst.append('')
                index_rst.append(':subtitle:`Modules:`')
                index_rst.append('')
                index_rst.append('.. toctree::')
                index_rst.append('   :maxdepth: 1')
                index_rst.append('')

                self.create_dir(settings.DS_ROOT + '/' + path)
                for module in app_instance.modules:
                    index_rst.append('   ' + module + '.rst')

                    module_lines = []
                    module_lines.append(module + '.py')
                    module_lines.append("-" * len(module_lines[0])),
                    module_lines.append('')
                    module_lines.append('.. toctree::')
                    module_lines.append('   :maxdepth: 2')
                    module_lines.append('')
                    module_lines.append('')
                    module_lines.append(".. automodule:: %s%s" %
                                        (app_name, module))
                    module_lines.append("    :members:")
                    module_lines.append("    :show-inheritance:")

                    self.write_file(
                        settings.DS_ROOT + '/' +
                        path + module + '.rst',
                        self.add_lf(module_lines))

        if path == '':
            index_rst.append('')
            index_rst.append('Indices and tables')
            index_rst.append('==================')
            index_rst.append('')
            index_rst.append('* :ref:`genindex`')
            index_rst.append('* :ref:`modindex`')
            index_rst.append('* :ref:`search`')

        self.write_file(settings.DS_ROOT + '/' +
                        path + 'index.rst',
                        self.add_lf(index_rst))

    def add_lf(self, l):
        """Append line feed \n to all elements of the given list"""
        return ["%s\n" % line for line in l]


class App(object):
    """Application with its name and the list of python files it contains"""

    def __init__(self, name):
        self.name = name
        self.is_internal = self.name in os.listdir(HERE)
        self.path = self.get_path()
        self.modules = self.get_modules()

    def get_path(self):
        """return absolute path for this application"""
        try:
            path = __import__(self.name).__path__[0]
            splitedName = self.name.split(".")
            if len(splitedName) > 1:
                path = os.path.join(path, *splitedName[1:])
            return path
        except ImportError:
            print(("The application %s couldn't" +
                   " be autodocumented" % self.name))
            return False

    def get_modules(self):
        """Scan the repository for any python files"""
        if not self.path:
            return []
        # Move inside the application
        os.chdir(self.path)

        modules = [f.split(".py")[0] for f in os.listdir(".") if f not
                   in settings.DS_EXCLUDED_MODULES and f.endswith(".py")]
        # Remove all irrelevant modules. A module is relevant if he
        # contains a function or class
        not_relevant = []
        for module in modules:
            f_module = open("%s.py" % module, "r")
            content = f_module.read()
            f_module.close()
            keywords = ["def", "class"]
            relevant = sum([value in content for value in keywords])
            if not relevant:
                not_relevant.append(module)
                # print "%s.%s not relevant, removed" % (self.name, module)
        [modules.remove(module) for module in not_relevant]
        return modules

    def has_description(self):
        """Get the application docstring from __init__.py if it exists"""
        f_init = open("%s/__init__.py" % self.path, "r")
        content = f_init.read()
        if '"""' in content or "'''" in content:
            return True
        return False


def create_app_dict(l_apps):
    app_dict = {}

    for app in l_apps:
        if '.' in app:
            pointer = app_dict
            splitted = app.split('.')
            for index, app_name in enumerate(splitted):
                if app_name in pointer:
                    pointer = pointer[app_name]
                else:
                    pointer.update({app_name: {}})
                    pointer = pointer[app_name]
        else:
            if app not in app_dict:
                app_dict.update({app: {}})

    return app_dict


def main():
    # Define some variables

    settings.DS_ROOT = getattr(settings, "DS_ROOT",
                               os.path.join(HERE, "doc/source"))
    settings.DS_MASTER_DOC = getattr(settings, "DS_MASTER_DOC", "index.rst")
    settings.DS_FILENAME = getattr(settings, "DS_FILENAME", "auto_modules")
    settings.DS_EXCLUDED_APPS = getattr(settings, "DS_EXCLUDED_APPS", [])
    settings.DS_EXCLUDED_MODULES = getattr(
        settings, "DS_EXCLUDED_MODULES",
        ["__init__.py", ])

    # Create a file for new modules
    f_modules = Modules()
    # Write all the apps autodoc in the newly created file
    l_apps = set(settings.PROJECT_APPS + settings.EXTRA_DOC_APPS) -\
        set(settings.DS_EXCLUDED_APPS)

    app_dict = create_app_dict(l_apps)

    f_modules.process_app_dict(app_dict, '')

    # Create dot files
    call_command('graph_models',
                 'account', 'healthperson', 'healthprofessional',
                 'secretariat', 'patient', 'management',
                 exclude_models='LoginSMSCode,OldPassword,' +
                                'PasswordChangeRequest,AgreedwithRules,' +
                                'PolymorphicModel,LoginAttempt,' +
                                'AbstractBaseUser,EncryptModel,' +
                                'PermissionsMixin,Hospital,Group,Permission',
                 disable_fields=True,
                 inheritance=True,
                 outputfile=settings.DS_ROOT +
                            '/_static/user_healthperson.dot')

    include_list = ['QuestionnaireRequest',
                    'RequestStep',
                    'WizardDatabaseStorage',
                    'QuestionnaireBase']

    exclude = []

    import inspect
    from apps.questionnaire import models as models_module
    for name, obj in inspect.getmembers(models_module):
        if inspect.isclass(obj) and name not in include_list:
            exclude.append(name)

    # Create dot files
    call_command('graph_models',
                 'questionnaire',
                 exclude_models=','.join(exclude),
                 disable_fields=True,
                 inheritance=True,
                 outputfile=settings.DS_ROOT + '/_static/questionnaire.dot')


if __name__ == '__main__':
    main()
