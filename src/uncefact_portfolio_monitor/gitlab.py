from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Any
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class GitLabSource:
    base_url: str
    group: str
    include_subgroups: bool = True
    archived: bool = False


def _request_json(url: str) -> tuple[list[dict[str, Any]], str]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "uncefact-portfolio-monitor"})
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
        next_page = response.headers.get("X-Next-Page", "")
    if not isinstance(payload, list):
        raise ValueError("GitLab projects endpoint did not return a list")
    return payload, next_page


def normalize_project(project: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": project.get("id"),
        "name": project.get("name"),
        "path_with_namespace": project.get("path_with_namespace"),
        "web_url": project.get("web_url"),
        "default_branch": project.get("default_branch"),
        "visibility": project.get("visibility"),
        "archived": bool(project.get("archived", False)),
        "last_activity_at": project.get("last_activity_at"),
        "description": project.get("description"),
        "topics": sorted(project.get("topics") or []),
    }


def discover_projects(source: GitLabSource, requester=_request_json) -> list[dict[str, Any]]:
    page = "1"
    projects: list[dict[str, Any]] = []
    encoded_group = quote(source.group, safe="")
    while page:
        query = urlencode({
            "include_subgroups": str(source.include_subgroups).lower(),
            "archived": str(source.archived).lower(),
            "simple": "true",
            "per_page": "100",
            "page": page,
        })
        url = f"{source.base_url.rstrip('/')}/api/v4/groups/{encoded_group}/projects?{query}"
        payload, page = requester(url)
        projects.extend(normalize_project(item) for item in payload)
    return sorted(projects, key=lambda item: (item.get("path_with_namespace") or ""))


def build_snapshot(source: GitLabSource, projects: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": {
            "provider": "gitlab",
            "base_url": source.base_url,
            "group": source.group,
            "include_subgroups": source.include_subgroups,
            "archived": source.archived,
        },
        "project_count": len(projects),
        "projects": projects,
    }
