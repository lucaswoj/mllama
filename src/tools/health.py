#!/usr/bin/env python3

import os
import requests
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from pathlib import Path

from tool import tool


def get_types():
    url = "https://remoteapi.healthexport.app/api/v2/healthtypes"
    url += f"?accountKey={os.getenv('HEALTHEXPORT_KEY')}"

    response = requests.get(url, headers={"Accept": "application/json"})
    output = response.json()

    types = [
        {"name1": name1, "name2": name2, "name3": name3, "id": id}
        for name1, types1 in output.items()
        for type1 in types1
        for type2 in type1["types"]
        for name2, name3, id in [(type1["name"], type2["name"], type2["id"])]
    ]

    return [
        {
            "name": (
                f"{type['name1'][0].upper()}{type['name1'][1:]} {type['name3'][0].lower()}{type['name3'][1:]}"
                if type["name1"] != "record"
                and len([t for t in types if t["name3"] == type["name3"]]) > 1
                else type["name3"]
            ),
            "id": type["id"],
        }
        for type in types
    ]


@tool
def health():
    types = get_types()

    timespan_days = 20

    url = "https://remoteapi.healthexport.app/api/v2/healthdata/decrypted"
    date_from = datetime.now() - timedelta(days=timespan_days)

    params = {
        "uid": "PjYqU3L+r/3VVFIFPhSQu5cDUh/WMz7TM8HxwvO7UImTfd1IexfH5zAj9UaQBOUUovD0nOFoQgyc8I0dzVibNg==",
        "dateFrom": date_from.isoformat(),
        "dateTo": datetime.now().isoformat(),
        "accountKey": os.getenv("HEALTHEXPORT_KEY"),
        "type": [str(type["id"]) for type in types],
    }

    response = requests.get(url, headers={"Accept": "application/json"}, params=params)
    data = response.json()

    output = {}

    for stat in data:
        for datum in stat["data"]:
            type = next(t for t in types if t["id"] == stat["type"])
            type_name = f"{type['name']} ({datum['units']})"

            for record in datum["records"]:
                date_object = isoparse(record["time"])
                date = (
                    (
                        date_object
                        - timedelta(
                            minutes=date_object.utcoffset().total_seconds() / 60
                        )
                    )
                    .date()
                    .isoformat()
                )

                if date not in output:
                    output[date] = {}
                if type_name not in output[date]:
                    output[date][type_name] = []
                output[date][type_name].append(record["value"])

    for date, records in sorted(output.items()):
        yield f"## {date}\n"
        yield "---\n"
        for type_name, values in records.items():
            yield f"{type_name}: [{', '.join(map(str, values))}]\n"
        yield "---\n"
