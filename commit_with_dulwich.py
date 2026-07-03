from __future__ import annotations

from pathlib import Path

from dulwich import porcelain
from dulwich.repo import Repo


ROOT = Path(__file__).resolve().parent

TRACKED = [
    ".gitignore",
    "README.md",
    "portfolio_rebalance_analysis.py",
    "generate_dashboard_data.py",
    "analysis_outputs/ibkr_holdings_analysis.csv",
    "analysis_outputs/prices_2026-06-01.csv",
    "analysis_outputs/rebalance_proposal.csv",
    "analysis_outputs/rebalance_report.md",
    "analysis_outputs/watchlist_analysis.csv",
    "dashboard/app.js",
    "dashboard/data.js",
    "dashboard/index.html",
    "dashboard/styles.css",
    "docs/MOBILE_ACCESS.md",
    "docs/PROJECT_REVIEW.md",
    "docs/REPOSITORY_SAVE_PLAN.md",
]


def ensure_repo() -> Repo:
    git_dir = ROOT / ".git"
    if not (git_dir / "HEAD").exists():
        porcelain.init(str(ROOT), bare=False)
    return Repo(str(ROOT))


def main() -> None:
    repo = ensure_repo()
    porcelain.remote_add(str(ROOT), "origin", "https://github.com/FaberMach/AQRL-SMP_Allocation.git")
    porcelain.add(str(ROOT), paths=TRACKED)
    commit_id = porcelain.commit(
        str(ROOT),
        message=b"Add AQRL-SMP Allocation portfolio rebalance dashboard",
        author=b"Codex <codex@openai.com>",
        committer=b"Codex <codex@openai.com>",
    )
    print(commit_id.decode("ascii"))
    print(repo.get_config().get((b"remote", b"origin"), b"url").decode("utf-8"))


if __name__ == "__main__":
    main()
