"""A python implementation of the factory design pattern.  It's designed for use as a base class
for various types of data gateways.
"""
from __future__ import absolute_import, division, print_function

from .compat import with_metaclass
from .exceptions import InitializationError

__all__ = ['Factory']


class FactoryBase(object):

    @classmethod
    def initialize(cls, context, default_provider):
        cls.context = context
        cls._default_provider = (default_provider.__name__ if isinstance(default_provider, type)
                                 else str(default_provider))
        if not cls.is_registered_provider(cls._default_provider):
            raise RuntimeError("{0} is not a registered provider for "
                               "{1}".format(cls._default_provider, cls.__name__))

    @classmethod
    def get_instance(cls, provider=None):
        if not hasattr(cls, 'context'):
            raise InitializationError("RecordRepoFactory has not been initialized.")
        provider = provider.__name__ if isinstance(provider, type) else provider or cls._default_provider  # noqa
        return cls.providers[provider](cls.context)

    @classmethod
    def get_registered_provider_names(cls):
        return cls.providers.keys()

    @classmethod
    def get_registered_providers(cls):
        return cls.providers.values()

    @classmethod
    def is_registered_provider(cls, provider):
        if isinstance(provider, type):
            provider = provider.__name__
        return provider in cls.get_registered_provider_names()


class FactoryType(type):

    def __init__(self, name, bases, attr):
        super(FactoryType, self).__init__(name, bases, attr)
        if 'skip_registration' in self.__dict__ and self.skip_registration:
            pass  # we don't even care  # pragma: no cover
        elif self.factory is None:
            # this must be the base implementation; add a factory object
            self.factory = type(
                f'{self.__name__}Factory',
                (FactoryBase,),
                {'providers': dict(), 'cache': dict()},
            )

            if hasattr(self, 'gateways'):
                self.gateways.add(self)
        else:
            # must be a derived object, register it as a provider in cls.factory
            self.factory.providers[self.__name__] = self

    def __call__(self, *args):
        if 'factory' in self.__dict__:
            return (
                self.factory.get_instance(args[0])
                if args and args[0]
                else self.factory.get_instance()
            )

        if not getattr(self, 'do_cache', False):
            return super(FactoryType, self).__call__(*args)
        cache_id = "{0}".format(self.__name__)
        try:
            return self.factory.cache[cache_id]
        except KeyError:
            instance = super(FactoryType, self).__call__(*args)
            self.factory.cache[cache_id] = instance
            return instance


@with_metaclass(FactoryType)
class Factory(object):
    skip_registration = True
    factory = None


# ## Document these ##
# __metaclass__
# factory
# skip_registration
# gateways
# do_cache

# TODO: add name parameter  --give example from transcomm client factory
