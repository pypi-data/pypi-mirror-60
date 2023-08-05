from django.conf import settings


# Check to see if the GEOLOCATION_FIELD is provided in the settings
avalaible_options = ['provider', 'center', 'zoom']
try:
    GEOLOCATION_FIELD = settings.GEOLOCATION_FIELD
    for option in avalaible_options:
        value = GEOLOCATION_FIELD.get(option, None)
        if value is None:
            if option=='provider':
                GEOLOCATION_FIELD[option] = 'leaflet'
            if option=='center':
                GEOLOCATION_FIELD[option] = [0,0]
            if option=='zoom':
                GEOLOCATION_FIELD[option] = 12
except:
    GEOLOCATION_FIELD = {
        "provider": "leaflet", # Two provider: Leaflet, Mapbox
        "center" : [0,0],
        "zoom": 12,
    }