django-geolocation-fields
-------------------------
A Django app to facilitate the manipulation of Geolocation objects in a GeoDjango app without using a spatial database.

Detailed documentation is in the "docs" directory.

Quick start
-----------

The project is still in development

Here is an example that uses it https://github.com/syk1k/django-geolocation

1. Add "geolocation_fields" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
        ...
        'geolocation_fields',
    ]

2. Add a PointField to a model:
    ```python
    from geolocation_fields.models import fields
    field_name = fields.PointField(verbose_name='field_name')
    ```