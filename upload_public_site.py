from __future__ import annotations

import base64
import json
import os
import ssl
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public_site"
REPO = os.environ.get("GITHUB_REPOSITORY", "FaberMach/AQRL-SMP_Allocation")
BRANCH = "main"
API = f"https://api.github.com/repos/{REPO}/contents"
SSL_CONTEXT = ssl._create_unverified_context()

FILES = [
    ".github/workflows/pages.yml",
    ".nojekyll",
    "README.md",
    "index.html",
    "app.js",
    "styles.css",
    "data.js",
    "executive_report.html",
]


def request(method: str, path: str, token: str, payload: dict | None = None) -> dict | None:
    url = f"{API}/{quote(path, safe='/')}?ref={BRANCH}" if method == "GET" else f"{API}/{quote(path, safe='/')}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, context=SSL_CONTEXT, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404 and method == "GET":
            return None
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed: {exc.code} {body}") from exc


def upload_file(path: str, token: str) -> str:
    local = PUBLIC / path
    content = local.read_bytes()
    existing = request("GET", path, token)
    payload = {
        "message": f"Update {path}" if existing else f"Add {path}",
        "content": base64.b64encode(content).decode("ascii"),
        "branch": BRANCH,
    }
    if existing:
        payload["sha"] = existing["sha"]
    result = request("PUT", path, token, payload)
    action = "updated" if existing else "created"
    commit = result["commit"]["sha"][:12] if result and "commit" in result else "unknown"
    return f"{action}: {path} ({commit})"


def main() -> None:
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GH_TOKEN is required")
    for path in FILES:
        print(upload_file(path, token))


if __name__ == "__main__":
    main()
