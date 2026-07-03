from __future__ import annotations

import json
import os
import ssl
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


REPO = os.environ.get("GITHUB_REPOSITORY", "FaberMach/AQRL-SMP_Allocation")
BRANCH = "main"
API = f"https://api.github.com/repos/{REPO}/contents"
SSL_CONTEXT = ssl._create_unverified_context()

PATHS = [
    "extracted_text/Análise de Empresas - top 5.txt",
    "extracted_text/Stock Watch - Modelo Claudemir melhor que Julia.txt",
    "extracted_text/U16265093_20260507.txt",
]


def request(method: str, path: str, token: str, payload: dict | None = None) -> dict | None:
    url = f"{API}/{quote(path, safe='/')}"
    if method == "GET":
        url += f"?ref={BRANCH}"
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
        if exc.code == 404:
            return None
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed: {exc.code} {body}") from exc


def main() -> None:
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GH_TOKEN is required")
    for path in PATHS:
        existing = request("GET", path, token)
        if not existing:
            print(f"missing: {path}")
            continue
        payload = {
            "message": f"Remove sensitive source text {path}",
            "sha": existing["sha"],
            "branch": BRANCH,
        }
        request("DELETE", path, token, payload)
        print(f"deleted: {path}")


if __name__ == "__main__":
    main()
