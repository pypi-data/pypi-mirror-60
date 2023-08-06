"""
This is the base class for all the Geometric fields we will be creating
"""
import json

class Point:
    geojson = {}
    def __init__(self, iterable=[], *args, **kwargs):
        print(self)
        print(args)
        print(kwargs)
        if isinstance(iterable, list):
            self.geojson = json.dumps(iterable)
        else:
            raise ValueError