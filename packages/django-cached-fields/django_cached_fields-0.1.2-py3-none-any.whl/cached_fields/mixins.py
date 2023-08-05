from django.forms.models import model_to_dict
from .exceptions import UnauthorisedChange

from datetime import datetime

class CachedFieldsMixin(object):
    """
    Based off ModelDiffMixin
    """
    def __init__(self, *args, **kwargs):
        super(CachedFieldsMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict
        self.__cached_fields_enabled = True

    @property
    def _hot_fields(self):
        result = []
        for v in self._dcf_trigger_params.values():
            result.extend(v['field_triggers'])
        return list(set(result)) 

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def _process_recalculation(self, triggered):
        for k,v in self._dcf_trigger_params.items():
            if [i for i in triggered if i in v['field_triggers']]:
                func = v['calculation_method']
                result = func(instance=self)
                setattr(self, k, result)
                setattr(self, "{}_last_updated".format(k), datetime.now())
        return 1

    def _set_cache_value(self, field, value):
        setattr(self, "_dcf_cache_values", {field: value})

    def _commit_values_to_cache(self):
        for field, value in getattr(self, "_dcf_cache_values", {}).items():
            setattr(self, field, value)
            setattr(self, "{}_last_updated".format(field), datetime.now())

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        if [i for i in self.changed_fields if i in self._dcf_trigger_params.keys()]:
            raise UnauthorisedChange("You cannot directly edit cached fields.")
        triggered = [i for i in self.changed_fields if i in self._hot_fields]
        
        if self.has_changed and triggered or not self.pk:
            if not self.pk:
                triggered = self.__initial.keys()
                for field in self._dcf_cached_fields:
                    if getattr(self, field):
                        raise UnauthorisedChange("You cannot directly assign a cached field.")
            self._process_recalculation(triggered)
            self._commit_values_to_cache()

        super(CachedFieldsMixin, self).save(*args, **kwargs)
        self.__initial = self._dict

    def create(self, *args, **kwargs):
        self._commit_values_to_cache()
        super(CachedFieldsMixin, self).create(*args, **kwargs)
    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])
