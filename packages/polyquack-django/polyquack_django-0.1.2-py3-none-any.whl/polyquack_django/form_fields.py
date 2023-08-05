import json

from django.contrib.postgres.forms import JSONField

from polyquack.translation import Translatable


class TranslatablePgJSONFormField(JSONField):
    def prepare_value(self, value):
        # Return translations when we have a Translatable object
        if isinstance(value, Translatable):
            return json.dumps(value.translations)
        # Dicts default to single-quotes, which is not valid JSON
        if isinstance(value, dict):
            return json.dumps(value)
        return value
