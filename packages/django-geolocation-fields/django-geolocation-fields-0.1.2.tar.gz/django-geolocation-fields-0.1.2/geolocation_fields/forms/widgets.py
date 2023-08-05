from django.forms import widgets
from geolocation_fields.settings import *

class PointWidget(widgets.Input):
    input_type = 'text'
    template_name = 'widgets/point.html'

    def get_context(self, name, value, attrs):
        print(GEOLOCATION_FIELD)
        context = super().get_context(name, value, attrs)
        context['provider'] = GEOLOCATION_FIELD['provider']
        return context