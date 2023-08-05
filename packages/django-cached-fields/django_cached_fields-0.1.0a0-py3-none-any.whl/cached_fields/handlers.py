from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models.query import QuerySet
from django.db.models import Model

import inspect

from django.apps import apps

"""
    How the decorator should work.

    Layer 1: for_class
        The for_class decorator should accept all relevant variables and plumb them down
        into the correct layers. For example, the class name should be 

"""

def for_class(cls, signals=[pre_save], prefetch=[], *args, **kwargs):
    """
        Receivers, by default should hook into pre_save of the class.
    """
    def return_function(decorated, *args, **kwargs):
        """
            Prefetch fields are passed down, so that when they are executed by run_method
            they can be handled.
        """

        class wropper:
            obj = None

            def __call__(self, *args, **kwargs):
                return self.obj.__class__.update_cache(decorated(self, *args, **kwargs))

            def initialise(self, obj, *args, **kwargs):
                class_name = obj.__class__.get_class(cls)
                obj.__class__.methods[class_name] = (decorated, prefetch,)
                obj.__class__.signals[class_name] = signals
                receiver(signals, sender=class_name)(obj.__class__.propogate_signal)
                self.obj = obj

        return wropper()

    return return_function

class CachedFieldSignalHandler(object):
    methods = {}
    signals = {}

    def __init__(self, field, cls, *args, **kwargs):
        self.__class__.field = field
        self.__class__.parent_class = cls
        method_list = self.__dir__()
        for method in method_list:
            if method[:7] == "handle_":
                getattr(self, method).initialise(self)
        super(CachedFieldSignalHandler, self).__init__(*args, **kwargs)

    @classmethod
    def update_cache(cls, value):
        return value

    @classmethod
    def get_class(cls, class_name):
        if not isinstance(class_name, str):
            return "{}.{}".format(class_name._meta.app_label, class_name.__name__)
        else:
            return class_name

    @classmethod
    def propogate_signal(cls, signal, sender, instance, *args, **kwargs):
        cls.run_method(instance, cls.methods[cls.get_class(sender)])
        

    @classmethod
    def run_method(cls, instance, callback):
        """
            self.run_method(instance, self.methods[sender], prefetch_related=[])
            If instance is of type QuerySet, and its elements are of type sender, apply prefetch to it.
            If instance is either list or tuple, and its elements are of type sender, just loop through it.
            If instance is of type sender, just run the method on this instance.
        """
        callback, prefetch = callback
        if isinstance(instance, QuerySet):
            instance = instance.prefetch_related(*prefetch)
            for i in instance:
                return cls.execute(i, callback)
        elif isinstance(instance, (list, tuple,)):
            for i in instance:
                return cls.execute(i, callback)
        else:
            return cls.execute(instance, callback)

    @classmethod
    def execute(cls, instance, callback):
        result = callback(instance)
        instance._set_cache_value(cls.field, result)
        instance._commit_values_to_cache()

    def provision_signals(self):
        for class_name, signal in self.signals:
            self.connect_receiver(class_name, signal, self.methods[class_name])

    def as_handler(self, *args, **kwargs):
        """
            1. Connect all signals
        """
        # cls.provision_signals()
        pass