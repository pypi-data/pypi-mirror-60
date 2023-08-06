from django.forms import widgets
from geolocation_fields.settings import *

class PointWidget(widgets.Input):
    input_type = 'text'
    template_name = 'widgets/point.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['provider'] = GEOLOCATION_FIELDS['provider']
        context['display_input'] = GEOLOCATION_FIELDS['display_input']
        context['center'] = GEOLOCATION_FIELDS['center']
        context['dragging'] = GEOLOCATION_FIELDS['dragging']
        if value:
            context['point_value'] = value
        return context


class PolygonWidget(widgets.Textarea):
    template_name = 'widgets/polygon.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['provider'] = GEOLOCATION_FIELDS['provider']
        context['display_input'] = GEOLOCATION_FIELDS['display_input']
        context['center'] = GEOLOCATION_FIELDS['center']
        return context