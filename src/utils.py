import json


def format_to_schema(format):
    if format == "json":
        return '{"type": "object", "additionalProperties": true}'
    elif format is not None:
        return json.dumps(format)
    else:
        return None
