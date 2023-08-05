from datetime import datetime

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from .exceptions import CalculationMethodMissing
from .mixins import CachedFieldsMixin
from .handlers import CachedFieldSignalHandler

import types

class CachedFieldMixin(object):

    def __init__(self, method, field_triggers=[], signals=[], timeout=None, *args, **kwargs):
        self.method = method
        self.field_triggers = field_triggers
        self.signals = signals
        self.timeout = timeout
        self.args = args
        self.kwargs = kwargs
        self.externally_handled = not isinstance(method, types.FunctionType)
        super(CachedFieldMixin, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        self.name = name

        # Set type field
        type_field = type(self).__bases__[1](*self.args, **self.kwargs)
        setattr(cls, self.name, type_field)
        type_field.contribute_to_class(cls, self.name)

        # Timestamp field to log when changes happen
        last_update_field_name = "{}_changed".format(self.name)
        last_update = models.DateTimeField(null=True)
        # setattr(cls, last_update_field_name, last_update)
        last_update.contribute_to_class(cls, last_update_field_name)
        trigger_data = {}
        if not self.externally_handled:
            trigger_data = getattr(cls, "_dcf_trigger_params", {})
            trigger_data[self.name] = {
                "field_triggers": self.field_triggers,
                "signals": self.signals,
                "calculation_method": self.method,
            }
        else:
            self.method(self.name, cls)

        cached_fields_list = getattr(cls, "_dcf_cached_fields", [])
        cached_fields_list.append(self.name)
        setattr(cls, '_dcf_cached_fields', cached_fields_list)
        setattr(cls, "_dcf_trigger_params", trigger_data)
        setattr(cls, "_dcf_cache_values", {})


        # Silently inject mixin ensuring it hasn't already been injected
        if CachedFieldsMixin not in cls.__bases__:
            cls.__bases__ = (CachedFieldsMixin, ) + cls.__bases__ 


class CachedBigIntegerField(CachedFieldMixin, models.BigIntegerField):
    pass


class CachedBooleanField(CachedFieldMixin, models.BooleanField):
    pass


class CachedCharField(CachedFieldMixin, models.CharField):
    pass


class CachedDateField(CachedFieldMixin, models.DateField):
    pass


class CachedDateTimeField(CachedFieldMixin, models.DateTimeField):
    pass


class CachedDecimalField(CachedFieldMixin, models.DecimalField):
    pass


class CachedEmailField(CachedFieldMixin, models.EmailField):
    pass


class CachedFloatField(CachedFieldMixin, models.FloatField):
    pass


class CachedIntegerField(CachedFieldMixin, models.IntegerField):
    pass


class CachedIPAddressField(CachedFieldMixin, models.IPAddressField):
    pass


class CachedNullBooleanField(CachedFieldMixin, models.NullBooleanField):
    pass


class CachedPositiveIntegerField(CachedFieldMixin, models.PositiveIntegerField):
    pass


class CachedPositiveSmallIntegerField(CachedFieldMixin, models.PositiveSmallIntegerField):
    pass


class CachedSlugField(CachedFieldMixin, models.SlugField):
    pass


class CachedSmallIntegerField(CachedFieldMixin, models.SmallIntegerField):
    pass


class CachedTextField(CachedFieldMixin, models.TextField):
    pass


class CachedTimeField(CachedFieldMixin, models.TimeField):
    pass