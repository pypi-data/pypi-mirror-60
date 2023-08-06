"""
Settings and configuration for Django.

Read values from the module specified by the DJANGO_SETTINGS_MODULE environment
variable, and then from django.conf.global_settings; see the global_settings.py
for a list of all possible variables.
"""

import importlib


class SettingsManager(object):
    """
    A lazy proxy for either global Django settings or a custom settings object.
    The user can manually configure settings prior to using them. Otherwise,
    Django uses the settings module pointed to by DJANGO_SETTINGS_MODULE.
    """

    def __init__(self):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time settings are needed, if the user hasn't
        configured settings manually.
        """
        settings_module = "settings"
        self._wrapped = Settings(settings_module)

    def __getattr__(self, name):
        """Return the value of a setting and cache it in self.__dict__."""
        val = getattr(self._wrapped, name)
        self.__dict__[name] = val
        return val

    def __getitem__(self, x):
        return getattr(self, x)

    def __setattr__(self, name, value):
        """
        Set the value of setting. Clear all cached values if _wrapped changes
        (@override_settings does this) or clear single values when set.
        """
        if name == "_wrapped":
            self.__dict__.clear()
        else:
            self.__dict__.pop(name, None)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        """Delete a setting and clear it from cache if needed."""
        super().__delattr__(name)
        self.__dict__.pop(name, None)


class Settings:
    def __init__(self, settings_module):
        self.SETTINGS_MODULE = settings_module

        mod = importlib.import_module(self.SETTINGS_MODULE)

        self._explicit_settings = set()
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)
                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)


settings = SettingsManager()
