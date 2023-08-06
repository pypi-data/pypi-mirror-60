from django.forms import fields
from geolocation_fields.forms import widgets

class PointField(fields.CharField):
    widget = widgets.PointWidget
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    