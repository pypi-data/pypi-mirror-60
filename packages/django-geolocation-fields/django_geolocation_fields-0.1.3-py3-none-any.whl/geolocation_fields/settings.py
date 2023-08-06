from django.conf import settings


# Check to see if the GEOLOCATION_FIELD is provided in the settings
avalaible_options = ['provider', 'center', 'zoom', 'display_input']

# Default configurations
GEOLOCATION_FIELD = {
    "provider": "leaflet", # Two provider: Leaflet, Mapbox
    "center" : [0,0],
    "zoom": 12,
    'display_input': False,
}
try:
    for option in avalaible_options:
        value = settings.GEOLOCATION_FIELD.get(option, None)
        if value:
            GEOLOCATION_FIELD[option] = value                
except:
    pass