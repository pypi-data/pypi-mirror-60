"""
This file holds all our Geometric fields
"""
from django.db import models
from django.template import Context

from geolocation_fields.models import base, values_checks
from geolocation_fields.forms import fields



class PointField(models.Field):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 104
        super().__init__(*args, **kwargs)
        
    
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    
    def from_db_value(self, value, expression, connection):
        return value


    def get_internal_type(self):
        return "CharField"

    
    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': fields.PointField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    
    def validate(self, value, model_instance):
        values_checks.point_check(value)
        super().validate(value, model_instance)


class PolygonField(models.Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    
    def get_internal_type(self):
        return "TextField"


    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': fields.PolygonField}
        defaults.update(kwargs)
        return super().formfield(**defaults)