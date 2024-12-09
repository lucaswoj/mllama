import json
import logging


def get_json_schema(format):
    if format == "json":
        return '{"type": "object", "additionalProperties": true}'
    elif format is not None:
        return json.dumps(format)
    else:
        return None


logger = logging.getLogger("pal")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)-10s %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
