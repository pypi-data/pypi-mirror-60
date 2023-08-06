from django.conf import settings


# Check to see if the GEOLOCATION_FIELDS is provided in the settings
avalaible_options = [
    'provider', # The map title provider
    'center', # Where to center the map
    'zoom', # The zoom value of the map
    'display_input', # If the input field should be displayed or not
    'dragging', # If the map tile can be dragged or not
]

# Default configurations
GEOLOCATION_FIELDS = {
    "provider": "leaflet", # Two provider: Leaflet, Mapbox
    "center" : [0,0],
    "zoom": 12,
    'display_input': False,
    'dragging': True,
}
try:
    for option in avalaible_options:
        value = settings.GEOLOCATION_FIELDS.get(option, None)
        if value:
            GEOLOCATION_FIELDS[option] = value                
except:
    pass