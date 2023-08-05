"""
This file holds all our Geometric fields
"""
from django.db import models
from geolocation_fields.models import base
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

    
    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': fields.PointField}
        defaults.update(kwargs)
        return super().formfield(**defaults)