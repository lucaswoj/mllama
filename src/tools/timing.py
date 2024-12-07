import os
import requests
from datetime import datetime, timedelta

from tool import tool


def get_hours_report(areas, timespan_days):
    area_names = [area["timingProject"] for area in areas]
    projects = [
        project for project in get_all_projects() if project["title"] in area_names
    ]
    report = get_timing_app_report(areas, projects, timespan_days)
    return report


def get_all_projects():
    url = "https://web.timingapp.com/api/v1/projects"
    params = {"hide_archived": "1"}
    headers = {
        "Authorization": f'Bearer {os.environ["TIMING_API_KEY"]}',
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()["data"]


def get_timing_app_report(areas, projects, timespan_days):
    url = "https://web.timingapp.com/api/v1/report"
    start_date = (datetime.now() - timedelta(days=timespan_days)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    params = {
        "include_app_usage": "1",
        "include_child_projects": "1",
        "start_date_min": start_date,
        "start_date_max": end_date,
        "columns[0]": "title",
        "columns[1]": "notes",
        "columns[2]": "timespan",
        "columns[3]": "project",
    }
    for i, project in enumerate(projects):
        params[f"projects[{i}]"] = project["self"]
    headers = {
        "Authorization": f'Bearer {os.environ["TIMING_API_KEY"]}',
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers, params=params).json()
    output = {}
    for entry in response["data"]:
        project = next(
            (p for p in projects if p["self"] == entry["project"]["self"]), None
        )
        area = next((a for a in areas if a["timingProject"] == project["title"]), None)
        date = entry.get("start_date", "unknown").split("T")[0]
        if area["obsidianDir"] not in output:
            output[area["obsidianDir"]] = {}
        if date not in output[area["obsidianDir"]]:
            output[area["obsidianDir"]][date] = {
                "area": area,
                "date": date,
                "duration": 0,
                "details": [{"title": "Timing App", "details": ""}],
            }
        output[area["obsidianDir"]][date]["duration"] += entry["duration"]
        hours = round(entry["duration"] / 3600, 1)
        if output[area["obsidianDir"]][date]["details"][0]["details"]:
            output[area["obsidianDir"]][date]["details"][0]["details"] += "\n\n"
        output[area["obsidianDir"]][date]["details"][0][
            "details"
        ] += f"### {entry['title'] or 'Unknown Task'} ({hours} hours)\n{format_notes(entry['notes'])}"
    return output


def format_notes(notes):
    if not notes:
        return ""
    return notes.split("Join Zoom Meeting")[0].split(
        "-::~:~::~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~::~:~::-\nJoin with Google Meet"
    )[0]


@tool
def timing():
    areas = [
        {
            "timingProject": "onNAV",
            "obsidianDir": "Work/onNAV",
        }
    ]
    timespan_days = 20
    report = get_hours_report(areas, timespan_days)
    for area, dates in report.items():
        for date, data in dates.items():
            yield f"## {data['area']['timingProject']} - {data['date']} ({round(data['duration'] / 3600, 1)} hours)\n{data['details'][0]['details']}\n"
