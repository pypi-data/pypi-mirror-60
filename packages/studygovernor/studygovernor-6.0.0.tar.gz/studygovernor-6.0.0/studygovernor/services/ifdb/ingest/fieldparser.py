import os.path
import json

class FieldParser():
    def __init__(self, template_data):
        self._template = template_data

    def find_field_description(self, field_name):
        field_description = self._recursive_field_finder(self._template, field_name)
        return field_description

    def _recursive_field_finder(self, obj, field_name):
        if not isinstance(obj, dict):
            return None

        if field_name in obj:
            return obj[field_name]

        for field in obj.keys():
            val = self._recursive_field_finder(obj[field], field_name)

            if val is not None:
                return val

        return None

    def find_field_options(self, field_name):
        description = self.find_field_description(field_name)

        if 'options' in description:
            return description['options']

        return None