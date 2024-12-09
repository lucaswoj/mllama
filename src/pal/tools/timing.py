import os
from typing import Literal, Optional
from pydantic import BaseModel
import requests
from datetime import datetime, timedelta
from areas import areas

from tool import tool


class TimingReportItem(BaseModel):
    duration: float
    notes: Optional[str] = None
    project: dict[Literal["self"], str]
    title: Optional[str] = None
    timespan: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


def get_project_id(name: str):
    url = "https://web.timingapp.com/api/v1/projects"
    params = {"hide_archived": "1"}
    headers = {
        "Authorization": f'Bearer {os.environ["TIMING_API_KEY"]}',
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers, params=params)
    projects = response.json()["data"]
    return next(
        project["self"]
        for project in projects
        if project["title"].lower() == name.lower()
    )


def get_report(project_ids, days):
    url = "https://web.timingapp.com/api/v1/report"
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    params = {
        "include_app_usage": "1",
        "include_child_projects": "1",
        "include_team_members": "0",
        "start_date_min": start_date,
        "start_date_max": end_date,
        "columns[0]": "title",
        "columns[1]": "notes",
        "columns[2]": "timespan",
        "columns[3]": "project",
    }
    for i, project_id in enumerate(project_ids):
        params[f"projects[{i}]"] = project_id

    headers = {
        "Authorization": f'Bearer {os.environ["TIMING_API_KEY"]}',
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers, params=params)

    return [
        TimingReportItem.model_validate({**data, "notes": format_notes(data["notes"])})
        for data in response.json()["data"]
    ]


def format_notes(notes):
    if not notes:
        return ""
    return notes.split("Join Zoom Meeting")[0].split(
        "-::~:~::~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~::~:~::-\nJoin with Google Meet"
    )[0]


@tool
def timing(project: str, days: int = 14):

    project_id = get_project_id(project)
    if not project_id:
        return "Project not found"

    report = get_report([project_id], days)

    return report
