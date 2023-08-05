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
                return decorated(self.obj, *args, **kwargs)

            def initialise(self, obj, *args, **kwargs):
                class_name = obj.get_class(cls)
                obj.methods[class_name] = (decorated, prefetch,)
                obj.signals[class_name] = signals
                receiver(signals, sender=class_name)(obj.propogate_signal)
                self.obj = obj

        return wropper()

    return return_function

class CachedFieldSignalHandler(object):
    def __init__(self, field, cls, *args, **kwargs):
        self.field = field
        self.parent_class = cls
        self.methods = {}
        self.signals = {}
        method_list = super(CachedFieldSignalHandler, self).__dir__()
        for method in method_list:
            if method[:7] == "handle_":
                getattr(self, method).initialise(self)
        super(CachedFieldSignalHandler, self).__init__(*args, **kwargs)

    def update_cache(self, value):
        return value

    def get_class(self, class_name):
        if not isinstance(class_name, str):
            return "{}.{}".format(class_name._meta.app_label, class_name.__name__)
        else:
            return class_name

    def propogate_signal(self, signal, sender, instance, save=False, *args, **kwargs):
        self.run_method(instance, self.methods[self.get_class(sender)], save=save)
        

    def run_method(self, instance, callback, save=False):
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
                self.execute(i, callback, save=save)
        elif isinstance(instance, (list, tuple,)):
            for i in instance:
                self.execute(i, callback, save=save)
        else:
            self.execute(instance, callback, save=save)

    def execute(self, instance, callback, save=False):
        result = callback(instance)
        if isinstance(result, self.parent_class) or isinstance(result, QuerySet):
            self.propogate_signal(None, self.parent_class, result, save=True)
        else:
            instance._set_cache_value(self.field, result)
            instance._commit_values_to_cache()
            if save:
                instance.save()


